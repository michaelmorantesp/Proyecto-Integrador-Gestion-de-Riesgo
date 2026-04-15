"""
returns.py - Estadísticas descriptivas y pruebas de normalidad sobre rendimientos.
"""
import pandas as pd
import numpy as np
from scipy import stats


def calculate_descriptive_stats(series: pd.Series) -> dict:
    """
    Calcula estadísticas descriptivas clave de una serie de rendimientos.
    
    Returns:
        dict con Media, Volatilidad, Asimetría, Curtosis, Mínimo, Máximo.
    """
    clean = series.dropna()
    return {
        'Media': clean.mean(),
        'Volatilidad (Desv. Std)': clean.std(),
        'Asimetría (Skewness)': float(stats.skew(clean)),
        'Curtosis': float(stats.kurtosis(clean)),
        'Mínimo': clean.min(),
        'Máximo': clean.max(),
        'Observaciones': len(clean),
    }


def run_normality_tests(series: pd.Series) -> dict:
    """
    Ejecuta pruebas de normalidad: Jarque-Bera y Shapiro-Wilk.
    
    Returns:
        dict con resultados de cada prueba.
    """
    clean = series.dropna().values
    results = {}

    # --- Jarque-Bera ---
    jb_stat, jb_pval = stats.jarque_bera(clean)
    results['Jarque-Bera'] = {
        'statistic': jb_stat,
        'p_value': jb_pval,
        'is_normal': jb_pval > 0.05,
    }

    # --- Shapiro-Wilk (limitado a 5000 muestras por velocidad) ---
    sample = clean if len(clean) <= 5000 else clean[-5000:]
    note = ' (muestra 5000)' if len(clean) > 5000 else ''
    sw_stat, sw_pval = stats.shapiro(sample)
    results['Shapiro-Wilk'] = {
        'statistic': sw_stat,
        'p_value': sw_pval,
        'is_normal': sw_pval > 0.05,
        'note': note,
    }

    return results
