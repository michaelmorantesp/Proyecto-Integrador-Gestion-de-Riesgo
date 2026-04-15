import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

nb.cells.append(nbf.v4.new_markdown_cell("""\
# 🎓 Proyecto Integrador: Cuaderno de Defensa y Flashcards de Sustentación
**Entidad:** Risk Lab USTA

Este documento es la "Copia Carbón" de la teoría desplegada en el Dashboard de Streamlit. Contiene el arsenal académico y las justificaciones algorítmicas de las decisiones tomadas en el proyecto.
"""))

# M1
nb.cells.append(nbf.v4.new_markdown_cell("""\
## Módulo 1: Análisis Técnico e Indicadores

✏️ **Flashcard - Señales MACD vs RSI (¿Por qué EMA y no SMA?)**
- **Justificación:** SMA otorga el mismo peso a un precio de hace 50 días que al de ayer. La EMA (usada en MACD) pondera agresivamente la información reciente. Si estalla una crisis hoy, el MACD lo detectará instantáneamente cruzando a la baja, mientras que la SMA tardará semanas en enterarse y sangraremos dinero.

✏️ **Flashcard - Cruce MACD vs RSI**
- **Justificación:** El MACD evalúa *Momentum (tendencia)*. El RSI evalúa *Reversión a la media*. MACD nos dice hacia dónde va la masa, pero RSI nos advierte si la masa ya agotó su dinero (sobrecompra > 70). Comprar solo porque MACD es positivo ignorando un RSI de 85, es entrar cuando ya se acabó la liquidez.
"""))

# M2
nb.cells.append(nbf.v4.new_markdown_cell("""\
## Módulo 2: Retornos y Diagnóstico de Colas Pesadas

✏️ **Flashcard - Shapiro-Wilk vs Jarque-Bera**
- **Justificación:** Shapiro-Wilk es excelente para muestras pequeñas. En big data financiera, el ruido sobredimensiona la no-normalidad. **Jarque-Bera** aísla y penaliza puramente las dos cosas letales en riesgos bursátiles: **Asimetría** (sesgo a pérdidas) y **Curtosis** (probabilidad en la cola).

✏️ **Flashcard - Anderson-Darling**
- **Defensa:** Anderson-Darling penaliza demasiado las variaciones estocásticas insignificantes en las ramas infinitas. Nosotros como gestores necesitamos re-calibrar soportes matemáticos de grandes colas centrales, algo empíricamente estructurado a través de Jarque-Bera.
"""))

# M3
nb.cells.append(nbf.v4.new_markdown_cell("""\
## Módulo 3: GARCH y Riesgo Condicional

✏️ **Flashcard - Disección Ecuación GARCH (Alfa, Beta, Rho, Phi)**
- **¿Qué significan $\\omega$, $\\alpha$ y $\\beta$?**
  - $\\omega$ (Varianza Incondicional): La base constante del ruido de mercado.
  - $\\alpha$ (Shock ARCH): Sensibilidad a noticias abruptas (errores cuadrados pasados).
  - $\\beta$ (Persistencia GARCH): Su valor indica la inercia (memoria).
- **¿Dónde están $\\rho$ y $\\phi$?**
  - *Respuesta Técnica:* $\\phi$ y $\\rho$ corresponden a factores autorregresivos asumiendo dependencia en la **media** (Ej: ARMA). GARCH aísla la estructura heterocedástica dependiente enfocada estrictamente en modelar los clústeres de la **varianza** para robustecer el VaR no constante.
"""))

# M4
nb.cells.append(nbf.v4.new_markdown_cell("""\
## Módulo 4: CAPM y Riesgo Sistemático

✏️ **Flashcard - Beta vs Desviación Estándar**
- **Justificación:** La desviación estándar mide TODO el riesgo. Beta aísla solo el **Riesgo Sistemático**. Markowitz nos enseñó que el riesgo idiosincrático se puede (y se debe) diversificar. Por lo tanto, el CAPM solo renumera a un inversionista por tragar riesgo irremediable (Sistemático / Beta).
"""))

# M5
nb.cells.append(nbf.v4.new_markdown_cell("""\
## Módulo 5: Valor en Riesgo Estructural (VaR)

✏️ **Flashcard - Núcleo de Epanechnikov vs Normal Clásica**
- **Respuesta Técnica:** Asumir normalidad financiera es suicida en colas extremas (el airbag que amortigua el 95% del tiempo pero que explota cuando tienes un accidente). Usando el suavizado de *Epanechnikov*, hallamos el perfil asimétrico natural que estricta y matemáticamente minimiza el error cuadrático medio integrado (AMISE).

✏️ **Flashcard - Cota de Marchinkov**
- **Respuesta Técnica:** Ante choques mundiales nunca antes vistos (Cisnes Negros), los distribuciones estimadas históricas colapsan por falta de información análoga. Marchinkov nos traza el cortafuegos absoluto o "Airbag Blindado" dependiendo matemáticamente *sólo* de media y varianza teórica de la muestra, garantizando con dolor un soporte duro de pérdida.
"""))

# M6
nb.cells.append(nbf.v4.new_markdown_cell("""\
## Módulo 6: Markowitz y Portafolios Óptimos

✏️ **Flashcard - Matriz de Correlación**
- **Defensa:** Colores muy vibrantes revelan auto-correlación (redundancia de riesgo). Lo importante para la diversificación estricta son valores cercanos a cero (ortogonalidad). Si el activo A se desploma y tiene correlación 0 con el activo B, B no absorberá el impacto, diversificando la cartera.

✏️ **Flashcard - Estrategias de Veredicto**
- **Máximo Sharpe (Ofensiva Algorítmica):** Obliga a la cartera a concentrarse violentamente en los gigantes tecnológicos (AAPL).
- **Mínima Varianza (Defensiva de Marchinkov):** Neutraliza la exposición de tecnología hacia rubros como Salud y Commodities protectores (Oro / JNJ), asegurando amortiguamiento.
"""))

# M7 y M8
nb.cells.append(nbf.v4.new_markdown_cell("""\
## Módulos 7 y 8: Señales Algorítmicas y Contexto Macroeconómico

✏️ **Flashcard - Algoritmos Ponderados (M7)**
- **Justificación:** Ignoramos señales huérfanas porque producen "Latigazos" (Whipsaws). Requerimos que MACD, RSI y Bollinger se alineen geográficamente para detonar una recomendación y así evadir el ruido 80% del tiempo estático del mercado.

✏️ **Flashcard - Tasa Libre de Riesgo DGS10 y Jensen (M8)**
- **Justificación Geopolítica:** Si la tasa DGS10 se eleva, los capitales escapan a renta fija quebrando nuestras acciones (Apetito por Liquidez). El rendimiento excedente logrado (Alpha de Jensen) nos ayuda a probar si de verdad vencimos al mercado pasivo a pesar del costo de oportunidad.
"""))

nb.cells.append(nbf.v4.new_markdown_cell("""\
## 📸  Anexo de Interpretación Visual de Gráficos (Plotly)

A continuación, ejecutamos dinámicamente en Python el código para renderizar las gráficas de soporte analítico:
"""))

# Añadiendo celda de código que despliega los gráficos en el Jupyter Notebook
nb.cells.append(nbf.v4.new_code_cell("""\
import plotly.express as px
import plotly.graph_objects as go
from IPython.display import display, HTML

print("Las figuras interactivas han sido salvaguardadas en la carpeta /visualizaciones/. Puedes abrirlas directamente en tu navegador o explorador de archivos.")
display(HTML("<a href='../visualizaciones/M1_Tecnico.html' target='_blank'>Abrir Gráfico M1 - Análisis Técnico</a><br>"))
display(HTML("<a href='../visualizaciones/M4_CAPM.html' target='_blank'>Abrir Gráfico M4 - CAPM Regresión</a><br>"))
display(HTML("<a href='../visualizaciones/M8_Macro_Acumulado.html' target='_blank'>Abrir Gráfico M8 - Macroeconomía Base 100</a><br>"))
"""))

nb.cells.append(nbf.v4.new_markdown_cell("""\
### 📈 Gráficos M1 (Técnico)
- **Bandas Bollinger:** Si se abren, hay pánico/euforia. Si quiebra banda superior, sobrecompra.
- **RSI/MACD:** En el RSI, >70 es momento de vender; MACD sirve de confirmación cuando el color del histograma pierde intensidad.

### 🔔 Gráfico M2 (Retornos)
- Si el pico del histograma es más alto que la campana gaussiana negra, tenemos _Curtosis_ extrema (mucha quietud y luego un shock violento repentino).

### 📐 CAPM (M4)
- **Pendiente / Beta:** Mide qué tan inclinada va la curva vs el mercado. Los puntos dispersos alrededor de la recta son pura volatilidad inútil (_Riesgo Idiosincrático_).

### 📉 VaR Epanechnikov y Marchinkov (M5)
- La zona gris/roja hacia la izquierda es riesgo letal. La brecha enorme entre la predicción de kernel y Marchinkov es el _Cinturón de Incertidumbre Inédita_ de Cisnes Negros.

### 🐢 Frontera Eficiente M6
- El "Borde/Caparazón" de la izquierda y arriba es la eficiencia absoluta. Todo lo de adentro es malo. La estrella izquierda te defiende, la estrella derecha (tangente) te exprime dinero asumiendo riesgo extra.

### 🌍 Acumulado M8
- Todo lo que termine por _encima de la línea punteada gruesa del SPY_ se justifica, si la línea de nuestro portafolio está por debajo, habremos quemado tiempo e indexarse pasivamente habría sido mejor.
"""))

os.makedirs('notebooks', exist_ok=True)
with open('notebooks/05_flashcards_master.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Master Notebook 05 generado correctamente.")
