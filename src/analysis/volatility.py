"""
volatility.py - Modelado de volatilidad condicional con ARCH y GARCH.
Usa la librería `arch` de Kevin Sheppard.
"""
import pandas as pd
import numpy as np
from arch import arch_model


def fit_garch_model(series: pd.Series, model_type: str = 'GARCH', p: int = 1, q: int = 1):
    """
    Ajusta un modelo ARCH o GARCH a una serie de rendimientos.
    
    Args:
        series:     Rendimientos logarítmicos diarios.
        model_type: 'GARCH' o 'ARCH'.
        p:          Orden del término GARCH (rezagos de varianza).
        q:          Orden del término ARCH (rezagos de shock). Para ARCH puro usar q=0.
    
    Returns:
        Resultado del modelo ajustado (ARCHModelResult).
    """
    clean = series.dropna() * 100  # Escalar a % para estabilidad numérica

    if model_type == 'ARCH':
        am = arch_model(clean, vol='ARCH', p=p)
    else:
        am = arch_model(clean, vol='Garch', p=p, q=q)

    result = am.fit(disp='off', show_warning=False)
    return result


def compare_volatility_models(series: pd.Series) -> pd.DataFrame:
    """
    Compara múltiples especificaciones ARCH/GARCH por AIC y BIC.
    
    Returns:
        DataFrame con columnas ['Modelo', 'AIC', 'BIC', 'Log-Likelihood'].
    """
    specs = [
        ('ARCH(1)', 'ARCH', 1, 0),
        ('GARCH(1,1)', 'GARCH', 1, 1),
        ('GARCH(1,2)', 'GARCH', 1, 2),
        ('GARCH(2,1)', 'GARCH', 2, 1),
    ]

    rows = []
    for name, model_type, p, q in specs:
        try:
            res = fit_garch_model(series, model_type=model_type, p=p, q=q)
            rows.append({
                'Modelo': name,
                'AIC': round(res.aic, 4),
                'BIC': round(res.bic, 4),
                'Log-Likelihood': round(res.loglikelihood, 4),
            })
        except Exception:
            pass

    df = pd.DataFrame(rows).set_index('Modelo')
    return df
