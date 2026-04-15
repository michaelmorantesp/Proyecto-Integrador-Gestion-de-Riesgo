"""
risk_models.py - Modelos de riesgo: VaR paramétrico, histórico, Montecarlo,
                 CVaR, VaR KDE Epanechnikov, Cota de Marchinkov,
                 Test de Kupiec y Cono de VaR.
"""
import pandas as pd
import numpy as np
from scipy import stats
from scipy.interpolate import interp1d


# ──────────────────────────────────────────────
# VaR Métodos
# ──────────────────────────────────────────────

def calculate_var_parametric(series: pd.Series, confidence: float = 0.95) -> float:
    """VaR Paramétrico asumiendo distribución Normal."""
    mu = series.mean()
    sigma = series.std()
    return stats.norm.ppf(1 - confidence, loc=mu, scale=sigma)


def calculate_var_historical(series: pd.Series, confidence: float = 0.95) -> float:
    """VaR Histórico usando percentil empírico."""
    return np.percentile(series.dropna(), (1 - confidence) * 100)


def calculate_var_montecarlo(series: pd.Series, confidence: float = 0.95,
                              num_sims: int = 10000) -> float:
    """VaR por simulación de Montecarlo (distribución Normal)."""
    mu = series.mean()
    sigma = series.std()
    rng = np.random.default_rng(42)
    simulated = rng.normal(loc=mu, scale=sigma, size=num_sims)
    return np.percentile(simulated, (1 - confidence) * 100)


def calculate_cvar(series: pd.Series, confidence: float = 0.95) -> float:
    """CVaR / Expected Shortfall: promedio de pérdidas más allá del VaR."""
    var = calculate_var_historical(series, confidence)
    tail = series[series <= var]
    return tail.mean() if len(tail) > 0 else np.nan


def calculate_var_kde_epanechnikov(series: pd.Series, confidence: float = 0.95) -> float:
    """
    VaR usando KDE Gaussiano como aproximación empírica (Epanechnikov como referencia).
    Se usa scipy.stats.gaussian_kde para portabilidad (sin statsmodels).
    """
    clean = series.dropna().values
    kde = stats.gaussian_kde(clean)
    x_eval = np.linspace(clean.min() - 0.05, clean.max() + 0.05, 2000)
    pdf = kde.evaluate(x_eval)
    cdf = np.cumsum(pdf) * (x_eval[1] - x_eval[0])
    cdf = cdf / cdf[-1]

    inv_cdf = interp1d(cdf, x_eval, bounds_error=False, fill_value=(x_eval[0], x_eval[-1]))
    return float(inv_cdf(1 - confidence))


def calculate_marchinkov_bound(series: pd.Series, confidence: float = 0.95) -> float:
    """
    Cota de Markov/Marchinkov: límite teórico inferior basado en media y varianza.
    P(X <= c) >= 1 - E[X²] / c²  →  despejando c para nivel de confianza.
    Usamos approximación conservadora: mu - k*sigma con k de Chebyshev.
    """
    clean = series.dropna()
    mu = clean.mean()
    sigma = clean.std()
    # Desigualdad de Chebyshev: k = 1/sqrt(1-conf)
    k = 1 / np.sqrt(1 - confidence)
    return mu - k * sigma


# ──────────────────────────────────────────────
# Tabla comparativa
# ──────────────────────────────────────────────

def compare_risk_models(series: pd.Series, conf_1: float = 0.95,
                         conf_2: float = 0.99, num_sims: int = 10000) -> pd.DataFrame:
    """
    Tabla comparativa de VaR y CVaR en múltiples niveles de confianza.
    
    Returns:
        DataFrame indexado por nivel de riesgo, columnas por método.
    """
    rows = {}
    for conf in [conf_1, conf_2]:
        label = f"Riesgo {int(conf*100)}%"
        var_p = calculate_var_parametric(series, conf)
        var_h = calculate_var_historical(series, conf)
        var_mc = calculate_var_montecarlo(series, conf, num_sims)
        cvar = calculate_cvar(series, conf)

        # Anualizados (sqrt(252))
        rows[label] = {
            'Paramétrico Diario': var_p,
            'Histórico Diario': var_h,
            'Montecarlo Diario': var_mc,
            'CVaR (ES) Diario': cvar,
            'Paramétrico Anual': var_p * np.sqrt(252),
            'Histórico Anual': var_h * np.sqrt(252),
        }

    return pd.DataFrame(rows).T


# ──────────────────────────────────────────────
# Backtesting (Test de Kupiec)
# ──────────────────────────────────────────────

def calculate_kupiec_test(series: pd.Series, var: float, confidence: float = 0.95) -> dict:
    """
    Test de Kupiec POF (Proportion of Failures).
    
    Args:
        series:     Serie de rendimientos observados.
        var:        VaR estimado (valor negativo esperado).
        confidence: Nivel de confianza usado.
    
    Returns:
        dict con Fallos Observados, Esperados, P-Value y si fue Aceptado.
    """
    clean = series.dropna()
    T = len(clean)
    p = 1 - confidence  # probabilidad teórica de exceder el VaR

    observed_failures = int((clean < var).sum())
    expected_failures = T * p

    # Likelihood ratio (LR) de Kupiec
    if observed_failures == 0 or observed_failures == T:
        lr = 0.0
    else:
        po = observed_failures / T
        try:
            lr = -2 * (
                np.log((1 - p) ** (T - observed_failures) * p ** observed_failures)
                - np.log((1 - po) ** (T - observed_failures) * po ** observed_failures)
            )
        except Exception:
            lr = 0.0

    p_value = 1 - stats.chi2.cdf(lr, df=1)

    return {
        'Fallos Observados': observed_failures,
        'Fallos Esperados': round(expected_failures, 2),
        'LR Kupiec': round(lr, 4),
        'P-Value': round(p_value, 4),
        'Aceptado': p_value > 0.05,
    }


def calculate_christoffersen_test(series: pd.Series, var: float) -> dict:
    """
    Test de Independencia de Christoffersen.
    Evalúa si los fallos del VaR ocurren en rachas (clusters) o son independientes.
    """
    clean = series.dropna()
    hit = (clean < var).astype(int).values
    
    # Matriz de transición de estados (0: no fallo, 1: fallo)
    # n00: 0 -> 0, n01: 0 -> 1, n10: 1 -> 0, n11: 1 -> 1
    n00 = n01 = n10 = n11 = 0
    for i in range(len(hit) - 1):
        if hit[i] == 0 and hit[i+1] == 0: n00 += 1
        elif hit[i] == 0 and hit[i+1] == 1: n01 += 1
        elif hit[i] == 1 and hit[i+1] == 0: n10 += 1
        elif hit[i] == 1 and hit[i+1] == 1: n11 += 1
        
    # Probabilidades observadas
    p01 = n01 / (n00 + n01) if (n00 + n01) > 0 else 0
    p11 = n11 / (n10 + n11) if (n10 + n11) > 0 else 0
    p = (n01 + n11) / (n00 + n11 + n01 + n10) if (n00 + n11 + n01 + n10) > 0 else 0
    
    # Likelihood Ratio para independencia
    try:
        # Log-likelihood bajo la hipótesis nula (independencia: p01 = p11 = p)
        l_null = (n00 + n10) * np.log(1 - p) + (n01 + n11) * np.log(p)
        # Log-likelihood bajo la hipótesis alternativa (dependencia)
        l_alt = n00 * np.log(1 - p01) + n01 * np.log(p01) + n10 * np.log(1 - p11) + n11 * np.log(p11)
        lr_ind = -2 * (l_null - l_alt)
        p_value = 1 - stats.chi2.cdf(lr_ind, df=1)
    except Exception:
        lr_ind = 0.0
        p_value = 1.0
        
    return {
        'LR Independencia': round(lr_ind, 4),
        'P-Value': round(p_value, 4),
        'Independiente': p_value > 0.05,
        'Rachas (n11)': n11
    }


# ──────────────────────────────────────────────
# Cono de VaR
# ──────────────────────────────────────────────

def generate_var_cone(var_1d: float, horizon: int = 30) -> np.ndarray:
    """
    Proyecta el VaR diario a múltiples horizontes usando la raíz del tiempo.

    Args:
        var_1d:   VaR a 1 día (valor negativo).
        horizon:  Número de días a proyectar.

    Returns:
        Array con el VaR proyectado para cada día.
    """
    days = np.arange(1, horizon + 1)
    return var_1d * np.sqrt(days)


# ──────────────────────────────────────────────
# VaR de Portafolio (con correlaciones reales)
# ──────────────────────────────────────────────

def calculate_portfolio_var(
    returns: pd.DataFrame,
    weights: list,
    confidence: float = 0.95,
    method: str = "historico",
    num_sims: int = 10000,
) -> dict:
    """
    Calcula el VaR de un portafolio completo usando los pesos dados.
    Tiene en cuenta las correlaciones reales entre activos.

    Args:
        returns:    DataFrame con rendimientos simples de cada activo.
        weights:    Lista de pesos (deben sumar ~1.0).
        confidence: Nivel de confianza (0.95 por defecto).
        method:     'historico', 'parametrico' o 'montecarlo'.
        num_sims:   Simulaciones para Montecarlo.

    Returns:
        dict con VaR, CVaR y métricas del portafolio.
    """
    w = np.array(weights)
    w = w / w.sum()  # Normalizar por si no suman exactamente 1

    # Rendimiento diario del portafolio (serie combinada)
    port_ret = returns.dropna().values @ w
    port_series = pd.Series(port_ret, index=returns.dropna().index)

    ann_return = float(port_series.mean() * 252)
    ann_vol = float(port_series.std() * np.sqrt(252))

    if method == "historico":
        var_val = calculate_var_historical(port_series, confidence)
    elif method == "parametrico":
        var_val = calculate_var_parametric(port_series, confidence)
    else:
        var_val = calculate_var_montecarlo(port_series, confidence, num_sims)

    cvar_val = calculate_cvar(port_series, confidence)
    kupiec = calculate_kupiec_test(port_series, var_val, confidence)

    return {
        "rendimiento_anualizado_pct": round(ann_return * 100, 4),
        "volatilidad_anualizada_pct": round(ann_vol * 100, 4),
        "sharpe_ratio": round((ann_return - 0.045) / ann_vol, 4) if ann_vol > 0 else None,
        "var_diario_pct": round(float(var_val) * 100, 4),
        "cvar_diario_pct": round(float(cvar_val) * 100, 4),
        "var_anual_pct": round(float(var_val) * np.sqrt(252) * 100, 4),
        "backtesting_kupiec": kupiec,
    }
