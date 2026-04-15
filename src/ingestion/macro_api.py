"""
macro_api.py - Descarga de la tasa libre de riesgo (DGS10) desde la API de FRED.
Requiere FRED_API_KEY en las variables de entorno (.env).
"""
import os
import pandas as pd

def fetch_risk_free_rate(start: str, end: str) -> pd.Series:
    """
    Obtiene la tasa libre de riesgo (DGS10 - Bono del Tesoro USA 10 años) desde FRED.
    
    Args:
        start: Fecha inicio 'YYYY-MM-DD'
        end:   Fecha fin   'YYYY-MM-DD'
    
    Returns:
        pd.Series con la tasa libre de riesgo en formato decimal (ej. 0.045 = 4.5%).
    """
    # Intentar cargar dotenv si está disponible
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    api_key = os.getenv("FRED_API_KEY", "")

    if api_key:
        try:
            from fredapi import Fred
            fred = Fred(api_key=api_key)
            series = fred.get_series('DGS10', observation_start=start, observation_end=end)
            series = series.dropna() / 100.0  # Convertir de % a decimal
            return series
        except Exception as e:
            print(f"[FRED] Error al obtener datos: {e}. Usando fallback.")

    # Fallback: serie sintética con tasa fija del 4.5%
    date_range = pd.date_range(start=start, end=end, freq='B')
    fallback = pd.Series(0.045, index=date_range, name='DGS10_fallback')
    return fallback

def fetch_macro_panel(start: str, end: str) -> dict:
    """Obtiene indicadores macroeconómicos clave: Rf (DGS10), Inflación YoY (CPIAUCSL) y EUR/USD (DEXUSEU)."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    api_key = os.getenv("FRED_API_KEY", "")
    res = {"DGS10": 0.042, "CPI_YOY": 0.031, "EURUSD": 1.08} # Fallbacks conservadores

    if api_key:
        try:
            from fredapi import Fred
            fred = Fred(api_key=api_key)
            # Risk free
            dgs = fred.get_series('DGS10', observation_start=start, observation_end=end).dropna()
            if not dgs.empty: res["DGS10"] = float(dgs.iloc[-1]) / 100.0
            
            # Inflation (yoy calc)
            cpi = fred.get_series('CPIAUCSL', observation_start="2020-01-01", observation_end=end).dropna()
            if len(cpi) > 12: res["CPI_YOY"] = float((cpi.iloc[-1] / cpi.iloc[-13]) - 1)
            
            # FX EURUSD
            fx = fred.get_series('DEXUSEU', observation_start=start, observation_end=end).dropna()
            if not fx.empty: res["EURUSD"] = float(fx.iloc[-1])
        except Exception as e:
            print(f"[FRED] Panel fallback, error: {e}")
            
    return res
