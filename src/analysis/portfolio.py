"""
portfolio.py - Funciones de portafolio: Beta, CAPM, simulación de Markowitz.
"""
import pandas as pd
import numpy as np


def calculate_beta(asset_returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """
    Calcula la Beta de un activo respecto a un benchmark usando regresión OLS.
    
    Returns:
        float: Beta del activo.
    """
    aligned = pd.concat([asset_returns, benchmark_returns], axis=1).dropna()
    if aligned.shape[0] < 2:
        return np.nan

    asset = aligned.iloc[:, 0].values
    bench = aligned.iloc[:, 1].values

    cov_matrix = np.cov(asset, bench)
    beta = cov_matrix[0, 1] / cov_matrix[1, 1]
    return beta


def CAPM_expected_return(beta: float, rf: float, market_return: float) -> float:
    """
    Calcula el rendimiento esperado según el modelo CAPM.
    
    Args:
        beta:          Beta del activo.
        rf:            Tasa libre de riesgo (decimal, ej. 0.045).
        market_return: Rendimiento esperado del mercado (decimal, anualizado).
    
    Returns:
        float: Rendimiento esperado anualizado.
    """
    return rf + beta * (market_return - rf)


def simulate_markowitz_portfolios(returns: pd.DataFrame,
                                  num_portfolios: int = 10000,
                                  rf: float = 0.045) -> pd.DataFrame:
    """
    Genera portafolios aleatorios para trazar la Frontera Eficiente de Markowitz.
    
    Args:
        returns:         DataFrame de rendimientos simples diarios.
        num_portfolios:  Número de portafolios aleatorios a simular.
        rf:              Tasa libre de riesgo para el Sharpe Ratio.
    
    Returns:
        DataFrame con columnas: Rendimiento, Volatilidad, Sharpe_Ratio, Peso_<ticker>...
    """
    assets = returns.columns.tolist()
    n = len(assets)
    mean_returns = returns.mean() * 252
    cov_matrix = returns.cov() * 252

    portfolios = []
    rng = np.random.default_rng(42)

    for _ in range(num_portfolios):
        weights = rng.random(n)
        weights /= weights.sum()

        port_return = np.dot(weights, mean_returns)
        port_vol = np.sqrt(weights @ cov_matrix.values @ weights)
        sharpe = (port_return - rf) / port_vol if port_vol > 0 else 0

        row = {
            'Rendimiento': port_return,
            'Volatilidad': port_vol,
            'Sharpe_Ratio': sharpe,
        }
        for i, ticker in enumerate(assets):
            row[f'Peso_{ticker}'] = weights[i]

        portfolios.append(row)

    return pd.DataFrame(portfolios)


def get_optimal_portfolios(portfolios_df: pd.DataFrame) -> dict:
    """
    Identifica los portafolios óptimos: mínima varianza y máximo Sharpe.
    
    Returns:
        dict con llaves 'Minima Varianza' y 'Maximo Sharpe', cada uno es un dict de fila.
    """
    min_vol_idx = portfolios_df['Volatilidad'].idxmin()
    max_sharpe_idx = portfolios_df['Sharpe_Ratio'].idxmax()

    return {
        'Minima Varianza': portfolios_df.loc[min_vol_idx].to_dict(),
        'Maximo Sharpe': portfolios_df.loc[max_sharpe_idx].to_dict(),
    }
