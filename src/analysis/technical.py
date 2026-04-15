"""
technical.py - Indicadores técnicos: SMA, EMA, RSI, MACD, Bollinger Bands,
               Estocástico y evaluación de señales de trading.
"""
import pandas as pd
import numpy as np


def calculate_sma(series: pd.Series, window: int) -> pd.Series:
    """Media móvil simple."""
    return series.rolling(window=window).mean()


def calculate_ema(series: pd.Series, window: int) -> pd.Series:
    """Media móvil exponencial."""
    return series.ewm(span=window, adjust=False).mean()


def calculate_rsi(series: pd.Series, window: int = 14) -> pd.Series:
    """
    RSI (Relative Strength Index).
    Valores > 70 → sobrecompra, < 30 → sobreventa.
    """
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(com=window - 1, min_periods=window).mean()
    avg_loss = loss.ewm(com=window - 1, min_periods=window).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """
    MACD (Moving Average Convergence Divergence).
    
    Returns:
        (macd_line, signal_line, histogram)
    """
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(series: pd.Series, window: int = 20, num_std: float = 2.0):
    """
    Bandas de Bollinger.
    
    Returns:
        (upper_band, lower_band)
    """
    sma = series.rolling(window=window).mean()
    std = series.rolling(window=window).std()
    upper_band = sma + num_std * std
    lower_band = sma - num_std * std
    return upper_band, lower_band


def calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series,
                         k_window: int = 14, d_window: int = 3):
    """
    Oscilador Estocástico %K y %D.
    Cuando high=low=close (simplificación), el resultado es constante.
    
    Returns:
        (K, D) como pd.Series
    """
    lowest_low = low.rolling(window=k_window).min()
    highest_high = high.rolling(window=k_window).max()

    denom = (highest_high - lowest_low).replace(0, np.nan)
    k = 100 * (close - lowest_low) / denom
    d = k.rolling(window=d_window).mean()
    return k.fillna(50), d.fillna(50)


def evaluate_signals(price: float, rsi: float, macd_hist: float,
                     bb_upper: float, bb_lower: float,
                     sma_fast: float, sma_slow: float,
                     k_stoch: float, d_stoch: float,
                     rsi_overbought: float = 70, rsi_oversold: float = 30,
                     stoch_overbought: float = 80, stoch_oversold: float = 20) -> str:
    """
    Evalúa múltiples indicadores y retorna una señal consolidada.
    
    Returns:
        str: 'Fuerte Compra', 'Comprar', 'Neutro', 'Vender', 'Fuerte Venta'
    """
    score = 0

    # RSI
    if rsi < rsi_oversold:
        score += 2
    elif rsi > rsi_overbought:
        score -= 2

    # MACD histograma
    if macd_hist > 0:
        score += 1
    else:
        score -= 1

    # Bollinger
    if price < bb_lower:
        score += 1
    elif price > bb_upper:
        score -= 1

    # Golden / Death Cross
    if sma_fast > sma_slow:
        score += 1
    else:
        score -= 1

    # Estocástico
    if k_stoch < stoch_oversold:
        score += 1
    elif k_stoch > stoch_overbought:
        score -= 1

    if score >= 4:
        return "Fuerte Compra"
    elif score >= 2:
        return "Comprar"
    elif score <= -4:
        return "Fuerte Venta"
    elif score <= -2:
        return "Vender"
    else:
        return "Neutro"
