import nbformat as nbf
import os

os.makedirs('notebooks', exist_ok=True)
nb = nbf.v4.new_notebook()

code_setup = """\
import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display, Markdown

sys.path.append(os.path.abspath('..'))
from src.ingestion.market_api import fetch_portfolio_data
from src.analysis.pipeline import calculate_returns
from src.analysis.risk_models import compare_risk_models
from src.analysis.portfolio import simulate_markowitz_portfolios, get_optimal_portfolios

plt.style.use('seaborn-v0_8-whitegrid')

# Cargar Datos
tickers = ['AAPL', 'JNJ', 'JPM', 'XOM', 'GLD']
print(f"Descargando datos para: {tickers}")
prices = fetch_portfolio_data(tickers, '2020-01-01', '2024-01-01').dropna()
_, log_ret = calculate_returns(prices)
"""

md_intro = """\
# Reporte Final Analítico (04) - Optimización y Gestión de Colas
Este cuaderno extrae de manera iterativa los verdaderos soportes de caída permitida bajo asunciones Gausianas (Paramétrico) frente al alisamiento óptimo (Kernel de Epanechnikov) y los límites teóricos del Airbag de riesgo (Cota de Marchinkov) para cada activo del ecosistema. Asimismo, genera la configuración de Pesos (Weights) para Frontera Eficiente.
"""

code_analysis = """\
conf = 0.95

for asset in tickers:
    data = log_ret[asset].dropna()
    risk_df = compare_risk_models(data, conf)
    
    var_hist = risk_df.loc['Riesgo', 'VaR Histórico'] * 100
    var_epa = risk_df.loc['Riesgo', 'VaR KDE Epanechnikov'] * 100
    cvar = risk_df.loc['Riesgo', 'CVaR'] * 100
    marchinkov = risk_df.loc['Riesgo', 'Marchinkov Bound'] * 100
    
    display(Markdown(f"### Análisis de Riesgo para: **{asset}**"))
    display(risk_df * 100)
    
    interpretacion = f\"\"\"
**🔎 Explicación Estocástica de {asset}:**
* Si nos basamos estrictamente en el historial reciente (VaR Histórico), tendríamos un umbral de pérdida máxima en 1 día de **{var_hist:.2f}%**.
* Sin embargo, debido a la **Falsa Sensación de Seguridad** (efecto Airbag), aplicamos el modelo avanzado KDE de Epanechnikov. Este núcleo, al minimizar el error cuadrático asintótico de las colas, nos ajusta la pérdida a **{var_epa:.2f}%**. Esto significa que si un cisne negro ocurre, esta métrica es estadísticamente más robusta.
* Pero, ¿y si ocurre lo impredecible? La cota teórica absolutista de *Marchinkov* dicta que un nivel de estrés puro puede hacernos caer hasta **{marchinkov:.2f}%**. 
* Mientras tanto, la pérdida promedio si ya superamos el abismo del riesgo (CVaR) se sitúa en **{cvar:.2f}%**.
    \"\"\"
    display(Markdown(interpretacion))
    
    # Export Chart
    fig, ax = plt.subplots(figsize=(6,4))
    sns.histplot(data, bins=50, kde=False, color='steelblue', stat='density', ax=ax)
    ax.axvline(var_hist/100, color='orange', linestyle='--', label=f'VaR Hist: {var_hist:.2f}%')
    ax.axvline(var_epa/100, color='purple', linestyle='-.', label=f'VaR Epanech: {var_epa:.2f}%')
    ax.axvline(marchinkov/100, color='darkred', linestyle='-', linewidth=2, label=f'Marchinkov: {marchinkov:.2f}%')
    ax.set_title(f"Distribución de Riesgo {asset}")
    ax.legend()
    plt.savefig(f'../visualizaciones/04_{asset}_risk_dist.png', dpi=300, bbox_inches='tight')
    plt.close()
"""

md_portfolio = """\
## Simulación Markowitz y Recomendación de Inversión (10,000 Iteraciones)
¿Cómo distribuimos nuestro capital frente a este nivel de estrés detectado? Simularemos 10,000 universos de pesos paralelos para hallar el portafolio de Menor Volatilidad y el de Mejor Relación Retorno/Riesgo (Max Sharpe).
"""

code_portfolio = """\
simulated_results = simulate_markowitz_portfolios(prices, num_portfolios=10000, risk_free_rate=0.045)
optimal = get_optimal_portfolios(simulated_results)

max_sharpe_portfolio = optimal['Maximo Sharpe']
min_vol_portfolio = optimal['Minima Varianza']

rp_max = max_sharpe_portfolio['Rendimiento']
sdp_max = max_sharpe_portfolio['Volatilidad']
max_sharpe_allocation = max_sharpe_portfolio[3:] * 100 # Saltamos las primeras 3 (rendimiento, vol, sharpe)

rp_min = min_vol_portfolio['Rendimiento']
sdp_min = min_vol_portfolio['Volatilidad']
min_vol_allocation = min_vol_portfolio[3:] * 100

display(Markdown("### ⚖️ Recomendación de Pesos de Inversión (10,000 escenarios evaluados)"))
display(Markdown("**Portafolio Máximo Sharpe (Crecimiento Balanceado):**"))
display(max_sharpe_allocation.to_frame(name="Peso Óptimo (%)"))
display(Markdown(f"*Rendimiento Esperado Anual: {rp_max*100:.2f}% | Volatilidad Anual: {sdp_max*100:.2f}%*"))

display(Markdown("**Portafolio Mínima Varianza (Defensivo Conservador):**"))
display(min_vol_allocation.to_frame(name="Peso Min Riesgo (%)"))
display(Markdown(f"*Rendimiento Esperado Anual: {rp_min*100:.2f}% | Volatilidad Anual: {sdp_min*100:.2f}%*"))

# Gráfica Frontera
fig, ax = plt.subplots(figsize=(10,6))
sc = ax.scatter(simulated_results['Volatilidad'], simulated_results['Rendimiento'], c=simulated_results['Sharpe_Ratio'], cmap='YlGnBu', marker='o', s=10, alpha=0.3)
plt.colorbar(sc, label='Sharpe Ratio')
ax.scatter(sdp_max, rp_max, marker='*', color='r', s=500, label='Max Sharpe')
ax.scatter(sdp_min, rp_min, marker='*', color='g', s=500, label='Min Volatility')
ax.set_title('Frontera Eficiente Markowitz')
ax.set_xlabel('Volatilidad')
ax.set_ylabel('Retorno')
ax.legend()
plt.savefig(f'../visualizaciones/04_markowitz_frontier.png', dpi=300, bbox_inches='tight')
plt.close()

recommendation = f\"\"\"
**💡 Veredicto y Recomendación de Inversión Estratégica:**
El portafolio de **Máximo Sharpe** recomienda inyectar masivamente en los pesos dominantes mostrados arriba. Este perfil de inversión compensa magistralmente el enorme castigo de VaR que detectamos en los activos tóxicos (como vimos arriba en la sección de colas pesadas de *Epanechnikov*).
Si el entorno macroeconómico actual sufre mucha contracción, sugerimos volcar el portafolio estrictamente hacia el perfil **Mínima Varianza**, refugiándonos generalmente en el Oro (GLD) y sector defensivo (JNJ), neutralizando los cisnes negros que advertimos mediante el límite de Marchinkov.
\"\"\"
display(Markdown(recommendation))
"""

nb['cells'] = [
    nbf.v4.new_markdown_cell(md_intro),
    nbf.v4.new_code_cell(code_setup),
    nbf.v4.new_code_cell(code_analysis),
    nbf.v4.new_markdown_cell(md_portfolio),
    nbf.v4.new_code_cell(code_portfolio)
]

with open('notebooks/04_analisis_resultados.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print("Notebook 04 Reporte generado.")
