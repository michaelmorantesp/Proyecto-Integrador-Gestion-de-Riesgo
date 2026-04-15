# Guía de Desarrollo - Proyecto Integrador Teoría del Riesgo

Esta es la hoja de ruta para ir completando los entregables.

### FASE 1: Bases y Datos
- [x] Configurar entorno virtual (`python -m venv env`).
- [x] Obtener API Key de FRED (gratuita).
- [x] Probar `src/ingestion/market_api.py` asegurando que el caché funcione.
- [x] Implementar la descarga de la Tasa Libre de Riesgo en `macro_api.py`.

### FASE 2: Analítica Core (Backend en `src/analysis/`)
- [ ] **Módulo 1 & 7:** Programar funciones de RSI, MACD, Bandas de Bollinger. Crear una función que devuelva un string ("Compra", "Venta", "Neutro") según el cruce.
- [ ] **Módulo 2:** Funciones para Test de Jarque-Bera y Shapiro-Wilk (`scipy.stats`).
- [ ] **Módulo 3:** Usar la librería `arch` para estimar `arch_model(vol='GARCH', p=1, q=1)`. Extraer el AIC/BIC.
- [ ] **Módulo 4 & 5:** Escribir funciones matemáticas para Covarianza, Beta (CAPM), y np.percentile para el VaR Histórico.
- [ ] **Módulo 6:** Escribir el loop de Montecarlo (10,000 iteraciones) generando pesos aleatorios `np.random.random(len(tickers))` y calculando Sharpe Ratio.

### FASE 3: El Tablero en Streamlit (`app/`)
- [ ] Construir `main.py` con `st.sidebar` para navegar entre los 8 módulos.
- [ ] Enlazar los inputs del usuario (Fechas, Tickers) con los datos del backend.
- [ ] Usar `plotly.express` y `plotly.graph_objects` para los gráficos (Velas japonesas, Frontera Eficiente, Dispersión CAPM).
