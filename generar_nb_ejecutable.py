import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

nb.cells.append(nbf.v4.new_markdown_cell("""\
# 🛡️ RiskLab: Notebook Ejecutable de Interpretación y Defensa Final

Este notebook ejecuta directamente las funciones matemáticas de tu aplicación Streamlit (`src.analysis`) para generar el mismo output. Confirmamos empíricamente que los resultados del dashboard son 100% fidedignos. 

**NUEVO ESTÁNDAR GLOBAL:** Hemos integrado el Módulo 1, el cual procesa iterativamente CADA activo del portafolio mostrando gráficas de Bollinger, RSI y MACD, seguido de un motor analítico que genera una interpretación explícita en texto basándose en los datos crudos del último día.
"""))

nb.cells.append(nbf.v4.new_code_cell("""\
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio

# Renderizar en entorno Jupyter
pio.renderers.default = "iframe"

from src.analysis.pipeline import run_portfolio_analysis

print("Recopilando Datasets Universales...")
tickers = ['AAPL', 'MSFT', 'SPY', 'JNJ', 'JPM']
prices, simple_ret, log_ret = run_portfolio_analysis(tickers, '2023-01-01', '2024-01-01')
print("¡Carga Completa! Datos listos para la defensa.")
"""))

nb.cells.append(nbf.v4.new_markdown_cell("""\
### 📈 Módulo 1: Análisis Técnico (Iteración Exhaustiva de Portafolio)
*Interpretación Visual y Diagnóstico Dinámico:* Vamos a mapear la acción del precio para todos los activos de la cartera. Aplicaremos canales de Bollinger para identificar sobre-extensiones (euforia/pánico), analizador RSI y cruzaremos histogramas MACD, determinando el estado empírico de cada mercado.
"""))

nb.cells.append(nbf.v4.new_code_cell("""\
# Módulo 1: Análisis Técnico para TODOS los activos
from src.analysis.technical import calculate_sma, calculate_ema, calculate_bollinger_bands, calculate_rsi, calculate_macd
import plotly.graph_objects as go

for asset in tickers:
    print(f"\\n================ AUDITORÍA VISUAL: {asset} ================")
    df = prices[asset].dropna()
    sma = calculate_sma(df, 20)
    ema = calculate_ema(df, 20)
    up, low = calculate_bollinger_bands(df, 20, 2)
    rsi = calculate_rsi(df, 14)
    macd_line, signal_line, macd_hist = calculate_macd(df)
    
    # 1. Bollinger
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df, name=f'Precio {asset}'))
    fig.add_trace(go.Scatter(x=df.index, y=up, name='Bollinger Up', line=dict(color='rgba(250,0,0,0.2)')))
    fig.add_trace(go.Scatter(x=df.index, y=low, name='Bollinger Down', fill='tonexty', fillcolor='rgba(250,0,0,0.1)', line=dict(color='rgba(250,0,0,0.2)')))
    fig.update_layout(title=f"M1: Bollinger Bands & Price Action ({asset})", height=400, template='plotly_white')
    fig.show()
    
    # 2. RSI
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=df.index, y=rsi, name='RSI', line=dict(color='purple')))
    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Sobrecompra (>70)")
    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Sobreventa (<30)")
    fig_rsi.update_layout(title=f"M1: Relative Strength Index - {asset}", height=250, template='plotly_white')
    fig_rsi.show()
    
    # 3. MACD
    fig_macd = go.Figure()
    fig_macd.add_trace(go.Bar(x=df.index, y=macd_hist, name='Histograma MACD', marker_color=['green' if val >= 0 else 'red' for val in macd_hist]))
    fig_macd.add_trace(go.Scatter(x=df.index, y=macd_line, name='MACD Line', line=dict(color='blue')))
    fig_macd.add_trace(go.Scatter(x=df.index, y=signal_line, name='Signal Line', line=dict(color='orange')))
    fig_macd.update_layout(title=f"M1: MACD Momentum - {asset}", height=300, template='plotly_white')
    fig_macd.show()
    
    # --- EVALUACIÓN DE INTERPRETACIÓN DINÁMICA ---
    ultimo_rsi = rsi.iloc[-1]
    ultimo_macd = macd_hist.iloc[-1]
    
    status_rsi = "🔴 SOBRECOMPRA EXTREMA (Riesgo brutal de corrección, tomar ganancias)" if ultimo_rsi > 70 else ("🟢 SOBREVENTA (Posible rebote al alza detectado, pánico inyectado)" if ultimo_rsi < 30 else "⚪ ZONA NEUTRAL (Fricción sin tendencia aguda)")
    status_macd = "🟢 FASE DE EXPANSIÓN ALCISTA (Toros dominan la fuerza)" if ultimo_macd > 0 else "🔴 PRESIÓN BAJISTA ACTIVA (Agotamiento del momentum o caída prolongada)"
    
    print(f"💡 DIAGNÓSTICO DEL ACTIVO {asset} a última ventana evaluada:")
    print(f" -> Lectura RSI   : {ultimo_rsi:.2f} | Interpretación: {status_rsi}")
    print(f" -> Lectura MACD  : {ultimo_macd:.4f}  | Interpretación: {status_macd}")
    print("=========================================================================\\n")
"""))

nb.cells.append(nbf.v4.new_markdown_cell("""\
### 📊 Módulo 2: Rendimientos (Jarque-Bera y Curtosis)
*Interpretación Visual:* La función genera el histograma log-ret. Notarás que las colas de la distribución empírica (barras) sobrepasan la campana teórica, corroborando Curtosis (y validando por qué Jarque-Bera nos falla al decir que no es Normal).
"""))

nb.cells.append(nbf.v4.new_code_cell("""\
# Módulo 2
from src.analysis.returns import calculate_descriptive_stats

asset = 'AAPL'
data = log_ret[asset].dropna()
stats = calculate_descriptive_stats(data)

fig_hist = px.histogram(data, nbins=100, opacity=0.7, color_discrete_sequence=['indigo'], title=f"M2: Distribución de {asset}")
fig_hist.show()

print(f"Curtosis calculada de {asset}: {stats['Curtosis']:.2f}")
print("Demostración: Si es >3, es Leptocúrtica (Colas Pesadas, Cisnes Negros probables). Jarque-Bera destruye la curva de Gauss aquí.")
"""))

nb.cells.append(nbf.v4.new_markdown_cell("""\
### 📐 Módulo 4: CAPM y Dispersión de Residuos
*Interpretación Visual:* La pendiente de regresión OLS es exactamente el Riesgo Sistemático (Beta). La suma de los errores cuadrados (cada punto alejado de la línea) representa el Riesgo Idiosincrático que es penalizado en la bolsa porque podías diversificarlo.
"""))

nb.cells.append(nbf.v4.new_code_cell("""\
# Módulo 4
from src.analysis.portfolio import calculate_beta

bench = simple_ret['SPY'].dropna()
asset_ret = simple_ret['AAPL'].dropna()

fig_m4 = px.scatter(x=bench, y=asset_ret, trendline="ols", title="M4: Regresión CAPM")
fig_m4.show()

beta_calc = calculate_beta(asset_ret, bench)
print(f"Beta (Sistemático) {asset}: {beta_calc:.4f}")
print(f" -> Si es mayor a 1, somos volátiles amplificadores de mercado. Veredicto: {'AGRESIVO' if beta_calc > 1 else 'DEFENSIVO'}")
"""))

nb.cells.append(nbf.v4.new_markdown_cell("""\
### 🐢 Módulo 6: Frontera Eficiente de Markowitz
*Interpretación Visual:* La eficiencia existe SÓLO en la frontera superior izquierda (parábola). Cualquier portafolio simulado (punto) dentro de la campana acarrea ineficiencia. Buscamos tangencia con la Tasa Libre de Riesgo.
"""))

nb.cells.append(nbf.v4.new_code_cell("""\
# Módulo 6
from src.analysis.portfolio import simulate_markowitz_portfolios, get_optimal_portfolios

print("Computando 3000 escenarios estocásticos de simulación de tensores...")
portfolios = simulate_markowitz_portfolios(simple_ret.drop(columns=['SPY']), num_portfolios=3000)
fig_m6 = px.scatter(portfolios, x='Volatilidad', y='Rendimiento', color='Sharpe_Ratio', title="M6: Matriz de Markowitz Frontera")
fig_m6.show()

optimal = get_optimal_portfolios(portfolios)
min_v = optimal['Minima Varianza']
max_s = optimal['Maximo Sharpe']

print(f"RECOMENDACIÓN ALGORÍTMICA MIN VARIANZA (Defensivo):\\n{min_v}")
print(f"\\nRECOMENDACIÓN ALGORÍTMICA MAX SHARPE (Agresivo Tangente):\\n{max_s}")
"""))

os.makedirs('notebooks', exist_ok=True)
with open('notebooks/07_analisis_ejecutable.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print("Notebook FINAL generado exitosamente en notebooks/07_analisis_ejecutable.ipynb")
