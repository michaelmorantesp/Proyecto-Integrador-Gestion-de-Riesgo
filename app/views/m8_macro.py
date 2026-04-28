import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from src.analysis.portfolio import calculate_beta
from app.style import COLORS, apply_chart_layout, flashcard, module_header

def fetch_macro_panel_local(start: str, end: str) -> dict:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    api_key = os.getenv("FRED_API_KEY", "")
    res = {"DGS10": 0.042, "CPI_YOY": 0.031, "USDCOP": 3950.00}

    if api_key:
        try:
            from fredapi import Fred
            fred = Fred(api_key=api_key)
            dgs = fred.get_series('DGS10', observation_start=start, observation_end=end).dropna()
            if not dgs.empty: res["DGS10"] = float(dgs.iloc[-1]) / 100.0
            
            cpi = fred.get_series('CPIAUCSL', observation_start="2020-01-01", observation_end=end).dropna()
            if len(cpi) > 12: res["CPI_YOY"] = float((cpi.iloc[-1] / cpi.iloc[-13]) - 1)
            
            fx = fred.get_series('DEXCOUS', observation_start=start, observation_end=end).dropna()
            if not fx.empty: res["USDCOP"] = float(fx.iloc[-1])
        except Exception as e:
            pass
            
    return res


def _max_drawdown(returns: pd.Series) -> float:
    cumulative = (1 + returns).cumprod()
    peak = cumulative.cummax()
    return ((cumulative - peak) / peak).min()


def render(prices, simple_ret, log_ret):
    module_header(
        "🌍 Contexto Macro y Desempeño vs Benchmark",
        "Alpha de Jensen, Sharpe y Max Drawdown vs SPY.",
    )

    if prices is None or prices.empty:
        st.info("⬅️ Carga el portafolio desde el panel lateral para comenzar.")
        return

    benchmark = "SPY"
    if benchmark not in simple_ret.columns:
        st.error("No se encontró el benchmark SPY en los datos.")
        return

    # ── Desempeño Acumulado ───────────────────────────────────────────────
    st.subheader("📈 Desempeño Acumulado (Base 100)")
    cum_returns = (1 + simple_ret).cumprod() * 100

    fig = go.Figure()
    palette = [COLORS["accent_blue"], COLORS["accent_teal"], COLORS["accent_violet"],
               COLORS["success"], COLORS["warning"]]

    for i, col in enumerate(cum_returns.columns):
        is_spy = col == benchmark
        fig.add_trace(go.Scatter(
            x=cum_returns.index, y=cum_returns[col],
            name=col,
            mode="lines",
            line=dict(
                color="#CBD5E1" if is_spy else palette[i % len(palette)],
                width=2.5 if is_spy else 1.8,
                dash="dot" if is_spy else "solid",
            ),
            opacity=0.85,
        ))

    apply_chart_layout(fig, height=480, title="Evolución del Capital (Base 100)")
    st.plotly_chart(fig, use_container_width=True)

    if st.session_state.get("show_flashcards"):
        spy_cum = float((1 + simple_ret[benchmark]).prod() - 1) * 100
        flashcard(
            "Desempeño acumulado vs benchmark",
            f"El SPY acumuló {spy_cum:.1f}% en el período analizado, estableciendo el piso de referencia que cualquier inversor pasivo habría obtenido sin costos de gestión activa. Solo los activos que superan este umbral justifican el riesgo adicional asumido.",
            "info",
        )

    # ── Panel Macroeconómico API ──────────────────────────────────────────
    st.markdown("---")
    st.subheader("🌐 Panel Macroeconómico Vivo (API FRED)")
    
    with st.spinner("Conectando con base de datos macroeconómica (FRED)…"):
        macro_data = fetch_macro_panel_local("2023-01-01", "2024-01-01")
        rf_rate = macro_data["DGS10"]
        cpi = macro_data["CPI_YOY"]
        fx  = macro_data["USDCOP"]
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Risk-Free Rate (DGS10)", f"{rf_rate*100:.2f}%", help="Tasa de bonos del Tesoro USA a 10 años")
        m2.metric("Inflación USA (YoY)", f"{cpi*100:.2f}%", help="CPIAUCSL (Índice de Precios al Consumidor) Anualizado")
        m3.metric("USD/COP FX Rate", f"${fx:,.0f} COP", help="Tasa de cambio Dólar por Peso Colombiano (DEXCOUS)")

    st.markdown("---")

    # ── Métricas por activo ───────────────────────────────────────────────
    st.subheader("📊 Métricas de Performance vs Benchmark")

    bench_data = simple_ret[benchmark].dropna()
    bench_ann   = bench_data.mean() * 252
    bench_vol   = bench_data.std() * np.sqrt(252)

    rows = []
    for ticker in simple_ret.columns:
        if ticker == benchmark:
            continue
        asset_data = simple_ret[ticker].dropna()
        ret_ann = asset_data.mean() * 252
        vol_ann = asset_data.std() * np.sqrt(252)
        sharpe  = (ret_ann - rf_rate) / vol_ann if vol_ann > 0 else np.nan
        beta    = calculate_beta(asset_data, bench_data)
        capm_r  = rf_rate + beta * (bench_ann - rf_rate)
        alpha   = ret_ann - capm_r
        mdd     = _max_drawdown(asset_data)

        rows.append({
            "Activo":             ticker,
            "Ret. Anual":         f"{ret_ann*100:.2f}%",
            "Volatilidad":        f"{vol_ann*100:.2f}%",
            "Sharpe":             f"{sharpe:.2f}",
            "Beta (β)":           f"{beta:.2f}",
            "Alpha Jensen":       f"{alpha*100:.2f}%",
            "Max Drawdown":       f"{mdd*100:.2f}%",
            "_alpha_float":       alpha,
        })

    df = pd.DataFrame(rows)
    display_df = df.drop(columns=["_alpha_float"]).set_index("Activo")

    def style_alpha(val):
        try:
            v = float(val.replace("%", ""))
            if v > 0: return "color:#34D399;font-weight:600"
            if v < 0: return "color:#F87171;font-weight:600"
        except Exception:
            pass
        return ""

    st.dataframe(
        display_df.style.map(style_alpha, subset=["Alpha Jensen"]),
        use_container_width=True,
    )

    # ── Veredicto ─────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("⚖️ Veredicto Automático")
    ganadores  = [r["Activo"] for r in rows if r["_alpha_float"] > 0]
    perdedores = [r["Activo"] for r in rows if r["_alpha_float"] <= 0]

    if ganadores:
        st.success(f"🏆 **Generadores de Alpha:** {', '.join(ganadores)} superaron al benchmark. Su Alpha de Jensen es positivo – justifican el riesgo asumido sobre el SPY con Rf={rf_rate*100:.1f}%.")
    if perdedores:
        st.error(f"📉 **Destructores de valor:** {', '.join(perdedores)} no superaron al SPY. En esos casos hubiera sido más eficiente invertir en el índice pasivo.")

    if st.session_state.get("show_flashcards"):
        n_alfa_pos = len(ganadores)
        flashcard(
            "Alpha de Jensen y métricas de performance",
            f"{n_alfa_pos} de {len(rows)} activos superaron al mercado después de ajustar por su nivel de riesgo sistemático, con una tasa libre de riesgo de referencia de {rf_rate*100:.1f}%. El Alpha positivo es la evidencia cuantitativa de que la selección de activos aportó valor real por encima de lo que el mercado compensa naturalmente.",
            "success" if n_alfa_pos > len(rows) / 2 else "warning",
        )
