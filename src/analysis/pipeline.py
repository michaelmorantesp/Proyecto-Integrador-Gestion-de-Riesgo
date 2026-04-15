"""
pipeline.py - Pipeline central que orquesta la descarga y cálculo de rendimientos.
"""
import pandas as pd
import numpy as np
from src.ingestion.market_api import fetch_portfolio_data


def calculate_returns(prices: pd.DataFrame):
    """
    Calcula rendimientos simples y logarítmicos a partir de precios de cierre.
    
    Returns:
        (simple_returns, log_returns) como DataFrames.
    """
    simple_ret = prices.pct_change().dropna()
    log_ret = np.log(prices / prices.shift(1)).dropna()
    return simple_ret, log_ret


def run_portfolio_analysis(tickers: list, start: str, end: str):
    """
    Pipeline principal: descarga precios y calcula rendimientos.
    
    Args:
        tickers: Lista de tickers incluyendo el benchmark (ej. SPY).
        start:   Fecha inicio 'YYYY-MM-DD'.
        end:     Fecha fin   'YYYY-MM-DD'.
    
    Returns:
        (prices, simple_returns, log_returns)
    """
    prices = fetch_portfolio_data(tickers, start, end)
    simple_ret, log_ret = calculate_returns(prices)
    return prices, simple_ret, log_ret
