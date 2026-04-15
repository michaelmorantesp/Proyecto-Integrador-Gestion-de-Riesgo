import nbformat as nbf
import os
import sys

# Agregar path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
import pandas as pd
from src.analysis.pipeline import run_portfolio_analysis
from src.analysis.technical import calculate_sma, calculate_rsi, calculate_macd, calculate_bollinger_bands, calculate_stochastic, evaluate_signals

print("Ejecutando pipeline y calculando variables crudas para el Reporte Final de Señales (M7)...")
tickers = ['AAPL', 'MSFT', 'SPY', 'JNJ', 'JPM']
prices, simple_ret, log_ret = run_portfolio_analysis(tickers, '2023-01-01', '2024-01-01')

nb = nbf.v4.new_notebook()

nb.cells.append(nbf.v4.new_markdown_cell("""\
# 🛡️ RiskLab: Auditory Notebook de Algoritmia de Señales M7 (EXECUTED)
Este reporte materializa la **Evaluación Simultánea de Multi-Vectores** desarrollada en el Módulo 7. Evaluaremos el último registro algorítmico del cruce *Estocástico*, las bandas *Bollinger*, el Momentum *MACD*, el *RSI* y el *Golden Cross (SMA 50 vs 200)* para determinar el grado de viabilidad (comprar/vender/mantener).
"""))

nb.cells.append(nbf.v4.new_code_cell("""\
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# Optimizado para guardado de nbconvert
pio.renderers.default = "plotly_mimetype+notebook"

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
sys.path.append(os.getcwd())

from src.analysis.technical import calculate_sma, calculate_rsi, calculate_macd, calculate_bollinger_bands, calculate_stochastic, evaluate_signals
"""))

# Inyectamos el DataFrame para que el notebook convertido tenga las variables
nb.cells.append(nbf.v4.new_code_cell("""\
from src.analysis.pipeline import run_portfolio_analysis
tickers = ['AAPL', 'MSFT', 'SPY', 'JNJ', 'JPM']
prices, _, _ = run_portfolio_analysis(tickers, '2023-01-01', '2024-01-01')
"""))

for asset in tickers:
    if asset == 'SPY': continue # Se salta el índice
    
    df = prices[asset].dropna()
    up, low = calculate_bollinger_bands(df)
    rsi = calculate_rsi(df)
    _, _, macd_hist = calculate_macd(df)
    
    sma_fast = calculate_sma(df, 50)
    sma_slow = calculate_sma(df, 200)
    k_stoch, d_stoch = calculate_stochastic(df, df, df)
    
    ultimo_precio = df.iloc[-1]
    umbral_ob = 80.0
    umbral_os = 20.0
    k_ult = k_stoch.iloc[-1]
    d_ult = d_stoch.iloc[-1]
    
    signal = evaluate_signals(
        ultimo_precio, rsi.iloc[-1], macd_hist.iloc[-1], up.iloc[-1], low.iloc[-1],
        sma_fast.iloc[-1], sma_slow.iloc[-1], k_ult, d_ult
    )
    
    cruce_sma = "Golden Cross Alcista (SMA50 > SMA200)" if sma_fast.iloc[-1] > sma_slow.iloc[-1] else "Death Cross Bajista (SMA50 < SMA200)"
    
    est_status = "Presión de Venta (Zona Crítica)" if k_ult > umbral_ob and k_ult < d_ult else ("Presión de Compra (Zona Sobreventa)" if k_ult < umbral_os and k_ult > d_ult else "En rango de acumulación / inerte")

    nb.cells.append(nbf.v4.new_code_cell(f"""\
# Trazando Golden Cross y Momentum M7 para {asset}
df_asset = prices['{asset}'].dropna()
sma_f = calculate_sma(df_asset, 50)
sma_s = calculate_sma(df_asset, 200)

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_asset.index, y=df_asset, name='Precio {asset}', line=dict(color='black')))
fig.add_trace(go.Scatter(x=df_asset.index, y=sma_f, name='SMA 50 (Fast)', line=dict(color='green', dash='dot')))
fig.add_trace(go.Scatter(x=df_asset.index, y=sma_s, name='SMA 200 (Slow)', line=dict(color='red', width=3)))
fig.update_layout(title="Cruces Dinámicos de Continuidad (M7) - {asset}", height=400, template='plotly_white')
fig.show()
"""))

    nb.cells.append(nbf.v4.new_markdown_cell(f"""\
### ⚙️ Resolución Algorítmica Multi-Vectorial: **{asset}**

Cruzando las 5 capas condicionales desarrolladas en el laboratorio, este es el estatus del activo el día de cierre analizado:

* **Relación de Medias (SMA 50/200):** Se registra configurativamente un **{cruce_sma}**.
* **Oscilador Estocástico (%K vs %D):** El cruce corto estocástico denota **{est_status}** (K: {k_ult:.1f}, D: {d_ult:.1f}).
* **Resumen de Variables Estáticas:** 
    * RSI: {rsi.iloc[-1]:.2f}
    * Histograma MACD: {macd_hist.iloc[-1]:.4f}
    * Aciclicidad Bollinger: ${up.iloc[-1]:.2f} (Techo) / ${low.iloc[-1]:.2f} (Suelo) VS Precio: ${ultimo_precio:.2f}.
* **Veredicto Definitivo Final (Señal Operativa Automática): => `{signal.upper()}` <=**
"""))

os.makedirs('notebooks', exist_ok=True)
with open('notebooks/08_analisis_senales_finales.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Reporte de Señales M7 EXECUTED generado en notebooks/08_analisis_senales_finales.ipynb")
