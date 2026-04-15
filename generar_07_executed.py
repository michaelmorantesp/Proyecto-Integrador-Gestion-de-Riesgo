import nbformat as nbf
import os
import sys

# Agregar path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
import pandas as pd
from src.ingestion.data_loader import fetch_data_pipeline
from src.analysis.technical import calculate_sma, calculate_ema, calculate_bollinger_bands, calculate_rsi, calculate_macd

print("Ejecutando pipeline y calculando variables crudas para el Reporte Executed Analógico...")
tickers = ['AAPL', 'MSFT', 'SPY', 'JNJ', 'JPM']
prices, simple_ret, log_ret = fetch_data_pipeline(tickers, '2023-01-01', '2024-01-01')

nb = nbf.v4.new_notebook()

nb.cells.append(nbf.v4.new_markdown_cell("""\
# 🛡️ RiskLab: Notebook de Defensa Final (EXECUTED & PRECALCULATED)
Este documento funge como el **reporte final ya ejecutado**. Aquí visualizarás todas las gráficas técnicas generadas para CADA ACTIVO del portafolio, respaldadas con una celda de texto dedicada debajo de cada una que interpreta la situación coyuntural según su estado matemático.
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

from src.analysis.technical import calculate_sma, calculate_ema, calculate_bollinger_bands, calculate_rsi, calculate_macd
"""))

# Inyectamos el DataFrame para que el notebook convertido tenga las variables
nb.cells.append(nbf.v4.new_code_cell("""\
from src.ingestion.data_loader import fetch_data_pipeline
tickers = ['AAPL', 'MSFT', 'SPY', 'JNJ', 'JPM']
prices, _, _ = fetch_data_pipeline(tickers, '2023-01-01', '2024-01-01')
"""))

for asset in tickers:
    df = prices[asset].dropna()
    up, low = calculate_bollinger_bands(df, 20, 2)
    rsi = calculate_rsi(df, 14)
    macd_line, signal_line, macd_hist = calculate_macd(df)
    
    ultimo_rsi = rsi.iloc[-1]
    ultimo_macd = macd_hist.iloc[-1]
    ultimo_precio = df.iloc[-1]
    
    # Evaluación Textual Asistida
    status_rsi = "riesgo crítico de **SOBRECOMPRA** (se recomienda prudencia o toma de ganancias tácticas)" if ultimo_rsi > 70 else ("alivio extremo en **SOBREVENTA** (ventana técnica ideal para compras de largo plazo o rebote corto)" if ultimo_rsi < 30 else "**ZONA NEUTRAL** (fuerzas de mercado equilibradas sin catalizador claro)")
    status_macd = "positivo (**MOMENTUM ALCISTA**), confirmando que las presiones compradoras mantienen el timón estructural" if ultimo_macd > 0 else "negativo (**PRESIÓN BAJISTA ACTIVA**), denotando agotamiento severo y distribución institucional inminente"

    nb.cells.append(nbf.v4.new_code_cell(f"""\
# Trazando Módulo 1 para {asset}
df_asset = prices['{asset}'].dropna()
up, low = calculate_bollinger_bands(df_asset, 20, 2)
rsi_val = calculate_rsi(df_asset, 14)
macd, sig, hist = calculate_macd(df_asset)

# Visual 1: Precios y Bollinger
fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=df_asset.index, y=df_asset, name='Precio {asset}', line=dict(color='black')))
fig1.add_trace(go.Scatter(x=df_asset.index, y=up, name='Bollinger Up', line=dict(color='rgba(250,0,0,0.2)')))
fig1.add_trace(go.Scatter(x=df_asset.index, y=low, name='Bollinger Down', fill='tonexty', fillcolor='rgba(250,0,0,0.1)', line=dict(color='rgba(250,0,0,0.2)')))
fig1.update_layout(title="M1: Acicíclico y Volatilidad Canal - {asset}", height=350, template='plotly_white', margin=dict(t=40,b=10))
fig1.show()

# Visual 2: RSI
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=df_asset.index, y=rsi_val, name='RSI', line=dict(color='purple')))
fig2.add_hline(y=70, line_dash="dash", line_color="red")
fig2.add_hline(y=30, line_dash="dash", line_color="green")
fig2.update_layout(title="M1: RSI (Relative Strength Index) - {asset}", height=250, template='plotly_white', margin=dict(t=40,b=10))
fig2.show()

# Visual 3: MACD
fig3 = go.Figure()
colors = ['green' if v>=0 else 'red' for v in hist]
fig3.add_trace(go.Bar(x=df_asset.index, y=hist, name='Histograma MACD', marker_color=colors))
fig3.add_trace(go.Scatter(x=df_asset.index, y=macd, name='MACD', line=dict(color='blue')))
fig3.add_trace(go.Scatter(x=df_asset.index, y=sig, name='Signal', line=dict(color='orange')))
fig3.update_layout(title="M1: MACD Momentum - {asset}", height=300, template='plotly_white', margin=dict(t=40,b=10))
fig3.show()
"""))

    nb.cells.append(nbf.v4.new_markdown_cell(f"""\
### 💡 Interpretación de la Situación Actual: Activo **{asset}**

Evaluando detalladamente el flujo de cajas y los tensores matemáticos presentados en los visuales superiores, el RiskLab emite el siguiente veredicto fundacional:

* **Lectura RSI ({ultimo_rsi:.2f}):** El oscilador se encuentra dictando **{status_rsi}**. Tocar, rebotar o perforar fuertemente el canal de los espectros teóricos define toda la base algorítmica para futuras ejecuciones.
* **Lectura MACD Histograma ({ultimo_macd:.4f}):** El indicador métrico arroja columnas direccionales de volumen marcando un escenario {status_macd}. La divergencia entre la barra de MACD y las franjas de precios nos consolida el quiebre de tendencia visual anticipado.
* **Conclusión Estratégica:** El precio estacionario cerró cerca de los **{ultimo_precio:.2f} USD**, limitando fuertemente contenciones estocásticas hacia las bandas perimetrales.
"""))

os.makedirs('notebooks', exist_ok=True)
with open('notebooks/07_analisis_final_executed.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Estructura base nbformat guardada. ¡Listo para ejecución nbconvert!")
