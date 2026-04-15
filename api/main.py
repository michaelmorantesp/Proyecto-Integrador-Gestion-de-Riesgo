import math
import os
import sys
import numpy as np
from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta

# Fechas dinámicas (último año por defecto)
END_DATE = datetime.now().strftime("%Y-%m-%d")
START_DATE = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

# Asegurar que src/ sea accesible desde api/
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.ingestion.market_api import fetch_portfolio_data
from src.analysis.pipeline import calculate_returns
from src.analysis.risk_models import (
    calculate_var_historical, calculate_var_parametric, calculate_var_montecarlo,
    calculate_kupiec_test, calculate_christoffersen_test, calculate_cvar,
)
from src.analysis.portfolio import simulate_markowitz_portfolios, get_optimal_portfolios
from src.analysis.technical import (
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_sma, calculate_stochastic, evaluate_signals,
)

# ── Utilidades ─────────────────────────────────────────────────────────────────
def _safe(v):
    """Convierte valores numpy/NaN/Inf a tipos Python serializables en JSON."""
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating, float)):
        if math.isnan(v) or math.isinf(v):
            return None
        return float(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    return v

def _safe_dict(d: dict) -> dict:
    return {k: _safe(v) for k, v in d.items()}


# ── Aplicación ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="RiskLab API",
    version="1.0.0",
    description=(
        "API REST de análisis cuantitativo de portafolios. "
        "Endpoints: rendimientos, VaR (3 métodos) con backtesting Kupiec, "
        "frontera eficiente Markowitz con optimización por objetivo, y alertas técnicas."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Modelos de Respuesta (Pydantic) ────────────────────────────────────────────

class RendimientosResponse(BaseModel):
    ticker: str
    periodo_inicio: str
    periodo_fin: str
    rendimiento_acumulado_pct: float = Field(..., description="Rendimiento total del período (%)")
    media_diaria_pct: float = Field(..., description="Media aritmética diaria (%)")
    volatilidad_diaria_pct: float = Field(..., description="Desviación estándar diaria (%)")
    volatilidad_anualizada_pct: float = Field(..., description="Volatilidad anualizada √252 (%)")
    sharpe_ratio: Optional[float] = Field(None, description="Sharpe Ratio anualizado (rf=4.5%)")


class VarResponse(BaseModel):
    ticker: str
    metodo_var: str
    confianza: float
    var_estimado_pct: float = Field(..., description="VaR diario estimado (%)")
    var_anual_pct: float = Field(..., description="VaR anualizado √252 (%)")
    cvar_pct: float = Field(..., description="CVaR / Expected Shortfall (%)")


class BacktestResponse(BaseModel):
    ticker: str
    metodo: str
    confianza: float
    var_estimado_pct: float
    test_kupiec: dict
    test_christoffersen: dict
    estatus_modelo: str


class MarkowitzRequest(BaseModel):
    tickers: List[str]
    simulations: int = Field(10000, ge=1000, le=50000)
    target_return: Optional[float] = Field(None, description="Rendimiento objetivo anualizado (ej: 0.15)")
    start_date: Optional[str] = None
    end_date: Optional[str] = None


# ── Interfaz HTML ──────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def serve_html_client():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"status": "RiskLab API activa. Visita /docs para la documentación."}


# ── 1. Rendimientos ────────────────────────────────────────────────────────────
@app.get("/rendimientos/{ticker}", response_model=RendimientosResponse, tags=["Mercado"])
def api_rendimientos(
    ticker: str,
    start_date: str = Query(START_DATE, description="Fecha inicio YYYY-MM-DD"),
    end_date: str = Query(END_DATE, description="Fecha fin YYYY-MM-DD"),
):
    """
    Estadísticas de rendimiento para un activo individual.
    Incluye rendimiento acumulado, media diaria, volatilidad y Sharpe Ratio.
    """
    ticker = ticker.upper()
    data = fetch_portfolio_data([ticker], start_date, end_date)
    if data.empty:
        raise HTTPException(status_code=404, detail=f"Sin datos para {ticker} en el período solicitado.")

    simple_ret, _ = calculate_returns(data)
    ret = simple_ret[ticker].dropna()

    ann_vol = float(ret.std() * np.sqrt(252)) * 100
    ann_ret = float(ret.mean() * 252) * 100
    sharpe = round((ann_ret / 100 - 0.045) / (ann_vol / 100), 4) if ann_vol > 0 else None

    return RendimientosResponse(
        ticker=ticker,
        periodo_inicio=start_date,
        periodo_fin=end_date,
        rendimiento_acumulado_pct=round(float((1 + ret).prod() - 1) * 100, 4),
        media_diaria_pct=round(float(ret.mean()) * 100, 4),
        volatilidad_diaria_pct=round(float(ret.std()) * 100, 4),
        volatilidad_anualizada_pct=round(ann_vol, 4),
        sharpe_ratio=sharpe,
    )


# ── 2b. Backtesting del VaR — Test de Kupiec (Bonificación) ───────────────────
# NOTA: esta ruta debe ir ANTES de /var/{metodo} para que FastAPI no confunda
# el segmento literal "backtest" con un valor de {metodo}.
@app.get("/var/backtest/{ticker}", response_model=BacktestResponse, tags=["Riesgo"])
def api_var_backtest(
    ticker: str,
    method: str = Query("parametrico", description="historico | parametrico | montecarlo"),
    conf: float = Query(0.95, ge=0.90, le=0.99),
    start_date: str = Query(START_DATE),
    end_date: str = Query(END_DATE),
):
    """
    **Backtesting del VaR** — valida estadísticamente la calidad del modelo.

    - **Test de Kupiec (POF)**: verifica que la tasa de fallos sea correcta.
    - **Test de Christoffersen**: verifica que los fallos sean independientes (sin agrupamiento).

    Un modelo robusto pasa ambos tests.
    """
    ticker = ticker.upper()
    data = fetch_portfolio_data([ticker], start_date, end_date)
    if data.empty:
        raise HTTPException(status_code=404, detail=f"Ticker inválido: {ticker}")

    simple_ret, _ = calculate_returns(data)
    ret = simple_ret[ticker].dropna()

    if method == "historico":
        var_val = calculate_var_historical(ret, conf)
    elif method == "parametrico":
        var_val = calculate_var_parametric(ret, conf)
    else:
        var_val = calculate_var_montecarlo(ret, conf)

    kupiec = _safe_dict(calculate_kupiec_test(ret, var_val, conf))
    christ = _safe_dict(calculate_christoffersen_test(ret, var_val))

    robusto = kupiec.get("Aceptado") and christ.get("Independiente")
    return BacktestResponse(
        ticker=ticker,
        metodo=method,
        confianza=conf,
        var_estimado_pct=round(float(var_val) * 100, 4),
        test_kupiec=kupiec,
        test_christoffersen=christ,
        estatus_modelo="Robusto ✅" if robusto else (
            "Cobertura OK / Fallos Agrupados ⚠️" if kupiec.get("Aceptado") else "Inválido ❌"
        ),
    )


# ── 2. VaR ────────────────────────────────────────────────────────────────────
@app.get("/var/{metodo}", response_model=VarResponse, tags=["Riesgo"])
def api_var(
    metodo: str,
    ticker: str = Query(..., description="Símbolo del activo (ej: AAPL)"),
    conf: float = Query(0.95, ge=0.90, le=0.99, description="Nivel de confianza"),
    start_date: str = Query(START_DATE),
    end_date: str = Query(END_DATE),
):
    """
    Valor en Riesgo (VaR) diario y anualizado para un activo.

    **Métodos disponibles** (path parameter):
    - `historico` — percentil empírico de los retornos observados
    - `parametrico` — distribución normal con μ y σ observados
    - `montecarlo` — simulación de 2 000 escenarios

    También retorna el CVaR (Expected Shortfall).
    """
    metodo = metodo.lower()
    if metodo not in ("historico", "parametrico", "montecarlo"):
        raise HTTPException(
            status_code=400,
            detail="Método debe ser: historico, parametrico o montecarlo",
        )

    ticker = ticker.upper()
    data = fetch_portfolio_data([ticker], start_date, end_date)
    if data.empty:
        raise HTTPException(status_code=404, detail=f"Ticker inválido: {ticker}")

    simple_ret, _ = calculate_returns(data)
    ret = simple_ret[ticker].dropna()

    if metodo == "historico":
        val = calculate_var_historical(ret, conf)
    elif metodo == "parametrico":
        val = calculate_var_parametric(ret, conf)
    else:
        val = calculate_var_montecarlo(ret, conf, num_sims=2000)

    cvar = calculate_cvar(ret, conf)

    return VarResponse(
        ticker=ticker,
        metodo_var=metodo,
        confianza=conf,
        var_estimado_pct=round(float(val) * 100, 4),
        var_anual_pct=round(float(val) * np.sqrt(252) * 100, 4),
        cvar_pct=round(float(cvar) * 100, 4),
    )


# ── 3. Frontera Eficiente (Markowitz) ─────────────────────────────────────────
@app.post("/frontera-eficiente", tags=["Optimización"])
def api_frontera_eficiente(req: MarkowitzRequest):
    """
    **Optimización de portafolio** vía Frontera Eficiente de Markowitz.

    Simula `simulations` portafolios aleatorios y retorna:
    - **Mínima Varianza**: portafolio de mayor diversificación
    - **Máximo Sharpe**: mejor retorno ajustado por riesgo

    Si se especifica `target_return`, busca el portafolio de mínima volatilidad
    para ese nivel de rendimiento objetivo (**optimización interactiva por objetivo**).
    """
    start = req.start_date or START_DATE
    end = req.end_date or END_DATE

    data = fetch_portfolio_data(req.tickers, start, end)
    simple_ret, _ = calculate_returns(data)

    portfolios = simulate_markowitz_portfolios(simple_ret, req.simulations)
    optimal = get_optimal_portfolios(portfolios)

    min_vol = {k: float(v) for k, v in optimal["Minima Varianza"].items()}
    max_shp = {k: float(v) for k, v in optimal["Maximo Sharpe"].items()}

    res = {
        "status": "Optimización Completada",
        "portafolios_simulados": req.simulations,
        "minima_varianza": min_vol,
        "maximo_sharpe": max_shp,
    }

    if req.target_return is not None:
        tolerance = 0.02
        candidates = portfolios[abs(portfolios["Rendimiento"] - req.target_return) < tolerance]
        if not candidates.empty:
            best = candidates.loc[candidates["Volatilidad"].idxmin()]
            res["portafolio_objetivo"] = {k: float(v) for k, v in best.to_dict().items()}
            res["target_info"] = (
                f"Portafolio de mínima volatilidad ({best['Volatilidad']*100:.2f}%) "
                f"para retorno objetivo de ~{req.target_return*100:.1f}%."
            )
        else:
            res["target_info"] = (
                f"No se encontraron portafolios cercanos al {req.target_return*100:.1f}%. "
                "Aumenta `simulations` o ajusta el objetivo."
            )

    return res


# ── 4. Alertas de Trading ──────────────────────────────────────────────────────
@app.get("/alertas", tags=["Señales"])
def api_alertas(
    tickers: str = Query("AAPL,MSFT,TSLA", description="Tickers separados por coma"),
    start_date: str = Query(START_DATE),
    end_date: str = Query(END_DATE),
):
    """
    Motor de señales técnicas consolidadas para múltiples activos.
    Combina RSI, MACD, Bollinger Bands, Cruce de Medias Móviles y Estocástico.
    Genera señales: **Fuerte Compra → Comprar → Neutro → Vender → Fuerte Venta**.
    """
    ticker_list = [t.strip().upper() for t in tickers.split(",")]
    prices = fetch_portfolio_data(ticker_list, start_date, end_date)

    alertas = []
    for t in ticker_list:
        if t not in prices.columns:
            continue
        data = prices[t].dropna()
        if len(data) < 200:
            continue

        rsi = calculate_rsi(data).iloc[-1]
        _, _, macd_hist = calculate_macd(data)
        up, low = calculate_bollinger_bands(data)
        sma_f = calculate_sma(data, 50).iloc[-1]
        sma_s = calculate_sma(data, 200).iloc[-1]
        k, d = calculate_stochastic(data, data, data)
        price = data.iloc[-1]

        signal = evaluate_signals(
            price, rsi, macd_hist.iloc[-1],
            up.iloc[-1], low.iloc[-1],
            sma_f, sma_s,
            k.iloc[-1], d.iloc[-1],
        )
        alertas.append({
            "ticker": t,
            "ultimo_precio": round(float(price), 2),
            "señal_consolidada": signal,
            "rsi": round(float(rsi), 2),
            "tendencia_ma": "Alcista 📈" if sma_f > sma_s else "Bajista 📉",
            "posicion_bollinger": (
                "Sobrecompra" if price > up.iloc[-1]
                else "Sobreventa" if price < low.iloc[-1]
                else "Zona media"
            ),
        })

    return {
        "activos_evaluados": len(alertas),
        "periodo": {"inicio": start_date, "fin": end_date},
        "alertas": alertas,
    }
