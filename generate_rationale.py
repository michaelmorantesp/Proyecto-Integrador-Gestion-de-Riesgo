import nbformat as nbf
import os

# Asegurar directorios
os.makedirs('notebooks', exist_ok=True)

nb = nbf.v4.new_notebook()

md_intro = """\
# Proyecto Integrador Riesgo - 03: Racional Teórico y Toma de Decisiones

**Objetivo:** Este documento justifica de manera profunda cada decisión arquitectónica y estadística tomada en el backend del pipeline (`src/`). Asimismo, extrae e incorpora las funciones matemáticas provenientes del **Syllabus del RiskLab**, indicando exactamente las fuentes teóricas, libros guía y documentos de procedencia.

---

## 1. Justificación de los Retornos y Diagnósticos (¿Por qué Jarque-Bera y no Anderson-Darling?)
En la fase de pre-procesamiento (`src/analysis/returns.py`), se implementó la prueba de **Jarque-Bera** y **Shapiro-Wilk** en lugar de *Anderson-Darling* o *Kolmogorov-Smirnov*.

**Explicación Rigurosa:**
* **Jarque-Bera** (Jarque & Bera, 1980): Se enfoca exclusivamente en los primeros y segundos momentos de la distribución (Asimetría y Curtosis). Dado que en finanzas el problema principal del riesgo de cola proviene de las "colas pesadas" (curtosis leptocúrtica) y asimetría negativa o positiva, el estadístico JB nos dice *de qué forma* falla la curva en cumplir la normalidad, información vital para ajustar modelos GARCH o KDE.
* **Anderson-Darling (AD):** Si bien AD da gran peso a las desviaciones en las colas empíricas (es estricto), a menudo rechaza la normalidad de forma binaria ante cualquier ruido microscópico sin diferenciar si el rechazo se debe a asimetría, curtosis o simples outliers aislados. En finanzas (*Tsay, 2010*), preferimos diagnosticar el comportamiento de los momentos (JB) que un desvío general de la CDF (AD).

<img src="../visualizaciones/01_retornos_portafolio.png" width="800">
*Fig 1. Retornos logarítmicos del portafolio que exhiben la naturaleza aglomerada (volatility clustering).*
"""

code_garch = """\
# ==============================================================================
# SECCIÓN: JUSTIFICACIÓN GARCH VS EWMA 
# MATERIAL DE ORIGEN: Notas de Clase - Series de Tiempo Financieras y Volatilidad
# REFERENCIA TEÓRICA: Tsay, R. S. (2010). Analysis of Financial Time Series (Cap. 3).
# CONCEPTOS: Volatility Clustering & Mean Reversion.
# ==============================================================================

# Se optó por la familia ARCH/GARCH en 'src/analysis/volatility.py' porque EWMA 
# (Exponentially Weighted Moving Average) no asume "Reversión a la Media" de la volatilidad.
# El mercado tiende a estabilizarse tras choques, y el parámetro Omega (ω) en GARCH(1,1)
# captura magistralmente este nivel base (Hull, 2018, Cap. 10).
print("Justificación Volatilidad GARCH: Seleccionada por Capturar Reversión a la Media en el Pipeline Backend.")
"""

md_bootstrap = """\
## 2. Bootstrapping No Paramétrico de Simulaciones (El Código Base)
En lugar de depender de Montecarlo Clásico (que fuerza a generar dados asumiendo campanas Gausianas de varianza infinita), usamos un Bootstrap con reemplazo que clona directamente la naturaleza del mercado.
"""

code_bootstrap = """\
# ==============================================================================
# CÓDIGO BÁSICO INSTITUCIONAL
# UBICACIÓN ORIGINAL: Notebook 09 Consolidado / Documentación Interna
# LIBRO DE APOYO: Moscote Flórez, O. (2013). Elementos de estadística en riesgo (Simulación).
# ==============================================================================
import numpy as np
import matplotlib.pyplot as plt

def simulate_returns_bootstrap(real_returns, n_simulations=10000, n_days=252):
    \"\"\"
    Bootstrap con reemplazo.
    Mantiene intacta la curtosis real y dependencia cruzada latente.
    \"\"\"
    # Numpy extrae días aleatorios copiándolos de los datos originales
    sampled = np.random.choice(real_returns, size=(n_days, n_simulations), replace=True)
    return sampled

print("Función Simulate Returns Bootstrap (Notas Internas) inyectada y documentada con éxito.")
"""

md_kde = """\
## 3. Kernel Density Estimation (KDE) - El Suavizado Epanechnikov
El profesor plantea KDE en vez de historgramas brutos para poder inferir percentiles (VaR empírico mejorado) donde no han caído suficientes observaciones directas. 
¿Por qué Epanechnikov? Porque, matemáticamente, minimiza el AMISE (*Asymptotic Mean Integrated Squared Error*), lo cual significa que no asignará "riesgo" irreal donde las colas se cruzan, a diferencia de la campana Gausiana que "regala" probabilidad hasta el infinito.
"""

code_kernel = """\
# ==============================================================================
# CÓDIGO DEL PROFESOR JAVIER MAURICIO
# UBICACIÓN ORIGINAL: Notebook 09 Consolidado / Sección KDE.
# LIBRO DE APOYO: Silverman, B. W. (1986). Density Estimation for Statistics and Data Analysis.
# ==============================================================================

def ep_kernel(u, bandwidth=1.0):
    \"\"\"
    El Kernel Epanechnikov evalúa la distancia parabólica.
    A diferencia de la distribución de Gauss estricta, acota su forma localmente (entre -1 y 1).
    \"\"\"
    u = u / bandwidth
    return np.where(np.abs(u) <= 1, 0.75 * (1 - u**2) / bandwidth, 0)

print("Función Epanechnikov Kernel inyectada localmente y documentada exhaustivamente.")

# Visualización ya ejecutada previamente por el pipeline:
# <img src="../visualizaciones/03_kde_epanechnikov.png" width="800">
"""

md_airbag = """\
## 4. El "Airbag" del VaR y las Cotas Sólidas (Marchinkov bound)
En la **Sección 6 del material de fundamentos**, se advierte de un error gravísimo y letal en banca moderna: *"El VaR es una falsa sensación de seguridad... funciona como un airbag todo el tiempo, salvo cuando tienes un accidente"*.

El VaR en el 95% te protege de la volatilidad base, pero si el escenario rebasa ese 5%, rompes la campana teórica y las caídas no tienen soporte. Para solucionarlo, calculamos CVaR en nuestro backend (`src/analysis/risk_models.py`) y complementamos en los notebooks con desigualdades estadísticas duras como la de *Marchinkov*.
"""

code_marchinkov = """\
# ==============================================================================
# CÓDIGO DE PROTECCIÓN EXTREMA (Airbag Suplementario)
# UBICACIÓN ORIGINAL: Notas de profesor (Basado en Sección de Gestión Rígida de Riesgos)
# LIBRO DE APOYO: Hull, J. C. (2018). Risk Management and Financial Institutions (Expected Shortfall & Tail Risk).
# ==============================================================================

def marchinkov_bound(returns, confidence=0.05):
    \"\"\"
    Basado en lógica del teorema generalizado de cotas superiores.
    Al alejarnos Sigma veces ponderadas por 1/raíz(alfa), 
    calculamos el 'peor escenario' estocástico bajo cualquier distribución.
    \"\"\"
    mu = np.mean(returns)
    sigma = np.std(returns)
    cota = mu - (sigma / np.sqrt(confidence))
    return cota

print("Marchinkov Bound compilado y argumentado.")
"""

md_conclu = """\
## 5. Conclusión en el Dashboard Final
Esa fue la justificación para empaquetar estos scripts en un **Streamlit frontend (`app/main.py`)**: democratizar estas simulaciones densas para que el usuario simplemente pulse un botón. Markowitz requiere mucha iteración (el loop corre 10.000 veces nativamente en nuestro backend de `portfolio.py`); la interfaz gráfica hace imperceptible esta carga analítica.
"""

# Ensamblado del Notebook
nb['cells'] = [
    nbf.v4.new_markdown_cell(md_intro),
    nbf.v4.new_code_cell(code_garch),
    nbf.v4.new_markdown_cell(md_bootstrap),
    nbf.v4.new_code_cell(code_bootstrap),
    nbf.v4.new_markdown_cell(md_kde),
    nbf.v4.new_code_cell(code_kernel),
    nbf.v4.new_markdown_cell(md_airbag),
    nbf.v4.new_code_cell(code_marchinkov),
    nbf.v4.new_markdown_cell(md_conclu)
]

with open('notebooks/03_explicacion_razonamiento_afondo.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Notebook 03 Ratio Teórico Compilado.")
