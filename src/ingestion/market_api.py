"""
market_api.py - Descarga de precios de mercado usando yfinance con caché.
"""
import yfinance as yf
import pandas as pd
import requests_cache
import os

# Cache SQLite en la carpeta data/
CACHE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'yfinance_cache')
session = requests_cache.CachedSession(CACHE_PATH, expire_after=86400)  # 24h


def fetch_portfolio_data(tickers: list, start: str, end: str) -> pd.DataFrame:
    """
    Descarga precios de cierre ajustados para una lista de tickers.
    
    Args:
        tickers: Lista de símbolos bursátiles (ej. ['AAPL', 'SPY'])
        start: Fecha inicio 'YYYY-MM-DD'
        end:   Fecha fin   'YYYY-MM-DD'
    
    Returns:
        DataFrame con precios de cierre, una columna por ticker.
    """
    raw = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)

    # yfinance puede devolver MultiIndex si hay varios tickers
    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw['Close']
    else:
        prices = raw[['Close']] if 'Close' in raw.columns else raw
        prices.columns = tickers

    prices = prices.dropna(how='all')
    return prices
