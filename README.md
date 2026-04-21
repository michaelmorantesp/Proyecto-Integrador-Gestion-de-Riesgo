# RiskLab USTA — Dashboard de Riesgo Financiero

## Descripción

Dashboard interactivo para la evaluación cuantitativa de portafolios financieros, desarrollado como **Proyecto Integrador de Teoría del Riesgo** en la Universidad Santo Tomás (USTA). La aplicación consume datos de mercado en tiempo real mediante APIs financieras, ejecuta modelos estadísticos y estocásticos, y presenta los resultados en un tablero visual e interactivo.

**Portafolio por defecto:** AAPL · JNJ · JPM · XOM · GLD (benchmark: SPY).

---

## Módulos

| #  | Módulo                  | Descripción                                                                                                                          |
| -- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| M1 | Análisis Técnico       | Indicadores RSI, MACD, Bandas de Bollinger, SMA, Estocástico                                                                         |
| M2 | Rendimientos             | Rendimientos simples y logarítmicos, tests de normalidad (Jarque-Bera, Shapiro-Wilk)                                                 |
| M3 | Modelos GARCH            | Ajuste ARCH/GARCH con selección por AIC/BIC, volatilidad condicional                                                                 |
| M4 | Riesgo Sistemático      | Beta, CAPM, Alpha de Jensen, Tracking Error                                                                                           |
| M5 | Valor en Riesgo          | VaR Paramétrico, Histórico, Montecarlo, CVaR, VaR KDE, Test de Kupiec                                                               |
| M6 | Markowitz                | Frontera eficiente, portafolio de mínima varianza, máximo Sharpe (10 000 simulaciones)                                              |
| M7 | Señales Automáticas    | Alertas de compra/venta/neutro basadas en cruces de indicadores técnicos                                                             |
| M8 | Contexto Macro           | Tasa libre de riesgo (FRED DGS10), inflación (CPIAUCSL), tipo de cambio EUR/USD                                                      |
| B+ | **Bonificaciones** | **API REST avanzada**, **Backtesting VaR (Kupiec)**, **Despliegue Cloud (Render/Streamlit)**, **Stress Test** |

---

## Interfaz y Experiencia de Usuario

### Portada (Hero Screen)

La pantalla de inicio presenta un diseño **Premium SaaS** con las siguientes características:

- **Fondo animado** con blobs de color en deriva, grid overlay y línea de escaneo
- **Tarjeta de métricas** con efecto glassmorphism (`backdrop-filter: blur(24px) saturate(180%)`)
- **Badges de autores** con estilo glass pill y efecto hover suave
- **Tags de módulos** con hover interactivo (lift + brillo azul)
- **Animaciones de entrada** escalonadas tipo fade-up con curva `cubic-bezier` para cada elemento
- **Botón CTA** pill completamente redondeado con gradiente azul y efecto hover de escala

### Navegación por Teclado

| Tecla       | Acción                              |
| ----------- | ------------------------------------ |
| `Espacio` | Abre el dashboard desde la portada   |
| `→`      | Avanza al siguiente módulo (tabs)   |
| `←`      | Retrocede al módulo anterior (tabs) |

> Las teclas de módulo no actúan si el foco está en un campo de texto o selector.

### Correcciones y Mejoras Técnicas

- **Reset de portafolio corregido:** el botón "Reset" usaba escritura directa sobre la key del widget después de instanciarlo, lo que generaba `StreamlitAPIException`. Se corrigió usando una flag `_reset_tickers` en `session_state` evaluada antes de renderizar el multiselect.
- **Descripción centrada:** se fuerza `text-align: center` con inline style y regla CSS `!important` para neutralizar el estilo que Streamlit inyecta en el wrapper `stMarkdown`.

---

## Estructura del Proyecto

```
RiskLab_Portfolio/
├── app/                            # Frontend Streamlit
│   ├── main.py                     # Punto de entrada: hero, controles, navegación y tabs
│   ├── style.py                    # Sistema de diseño: paleta, CSS global, flashcard(), module_header()
│   ├── static/                     # Recursos estáticos (portada.png)
│   └── views/                      # Vistas por módulo
│       ├── m1_tecnico.py           # Análisis técnico: MA, Bollinger, RSI, MACD, Estocástico
│       ├── m2_rendimientos.py      # Rendimientos simples/log, estadísticas, tests de normalidad
│       ├── m3_garch.py             # Modelos ARCH/GARCH, pronóstico de volatilidad
│       ├── m4_capm.py              # Beta, CAPM, riesgo sistemático vs idiosincrático
│       ├── m5_var.py               # VaR (paramétrico, histórico, MC, KDE), CVaR, Kupiec
│       ├── m6_markowitz.py         # Frontera eficiente, mínima varianza, máximo Sharpe
│       ├── m7_senales.py           # Motor multi-indicador: señales automáticas de trading
│       └── m8_macro.py             # Benchmark SPY, Alpha de Jensen, panel macro (FRED)
├── api/                            # API REST (FastAPI)
│   ├── main.py                     # Endpoints cuantitativos
│   └── index.html                  # Cliente HTML del API
├── src/                            # Backend analítico
│   ├── ingestion/
│   │   ├── market_api.py           # Precios de mercado via yfinance + caché SQLite
│   │   └── macro_api.py            # Indicadores macro via FRED API
│   └── analysis/
│       ├── pipeline.py             # Pipeline de descarga y cálculo de rendimientos
│       ├── technical.py            # Indicadores técnicos (RSI, MACD, Bollinger, etc.)
│       ├── volatility.py           # Modelos ARCH/GARCH
│       ├── risk_models.py          # VaR, CVaR, KDE Epanechnikov, Kupiec, Christoffersen
│       ├── portfolio.py            # Beta, CAPM, Markowitz, Alpha de Jensen
│       └── returns.py              # Estadísticas descriptivas y tests de normalidad
├── data/
│   └── yfinance_cache.sqlite       # Caché local de precios descargados
├── .streamlit/
│   ├── config.toml                 # Configuración del servidor Streamlit
│   └── static/                     # Activos estáticos servidos por Streamlit
├── .env.example                    # Plantilla de variables de entorno (FRED_API_KEY)
├── .gitignore
├── render.yaml                     # Configuración de despliegue en Render
├── requirements.txt                # Dependencias Python
├── guia_indicadores_risklab.html   # Guía de referencia de indicadores
├── presentacion_risklab.html       # Presentación del proyecto
└── 09_proyecto_consolidado_final.ipynb  # Notebook de investigación original
```

---

## Tecnologías

| Categoría       | Herramientas                      |
| ---------------- | --------------------------------- |
| Lenguaje         | Python 3.10+                      |
| Frontend         | Streamlit, Plotly                 |
| API REST         | FastAPI, Uvicorn, Pydantic        |
| Analítica       | Pandas, NumPy, SciPy, Statsmodels |
| Volatilidad      | arch (Kevin Sheppard)             |
| Datos de mercado | yfinance, requests-cache          |
| Datos macro      | fredapi (FRED)                    |
| Configuración   | python-dotenv                     |

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd RiskLab_Portfolio

# 2. Crear y activar entorno virtual
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env y agregar tu FRED_API_KEY (obtener en https://fred.stlouisfed.org/docs/api/api_key.html)
```

> **Nota:** La API de FRED es gratuita. Si no se configura la key, el sistema usa un fallback con tasa fija del 4.5%.

---

## Uso

### Dashboard (Streamlit)

```bash
streamlit run app/main.py
```

Se abrirá el tablero en `http://localhost:8501`. Desde el sidebar se selecciona el período de análisis y se navega entre los 8 módulos.

### API REST (FastAPI)

```bash
uvicorn api.main:app --reload
```

Documentación interactiva disponible en `http://localhost:8000/docs`.

---

## 🚀 Despliegue en la Nube

### 1. Render (API & Dashboard)

El proyecto incluye un archivo `render.yaml` que permite el despliegue automático en la plataforma Render.

- Conecta tu repositorio de GitHub a Render.
- Crea un nuevo **Blueprint Instance**.
- Render detectará el archivo yaml y desplegará dos servicios: la API y el Dashboard.

### 2. Streamlit Cloud (Dashboard optimizado)

- Sube el código a GitHub.
- Ve a [share.streamlit.io](https://share.streamlit.io/).
- Conecta el repo y selecciona `app/main.py` como punto de entrada.

---

## 🛠️ Especificaciones de Bonificación

Este proyecto implementa las siguientes características avanzadas de profundidad:

1. **API REST como Backend Propio:** Desarrollada con FastAPI, exponiendo endpoints para cálculos cuantitativos.
2. **Backtesting del VaR:** Implementación del **Test de Kupiec** (POF) y **Test de Independencia de Christoffersen** para validar la robustez de los modelos de riesgo.
3. **Optimización por Rendimiento Objetivo:** En el módulo de Markowitz, el sistema permite hallar el portafolio de mínima volatilidad para un rendimiento específico deseado por el usuario.
4. **Stress Testing:** Análisis de escenarios extremos mediante la **Cota de Marchinkov** y cálculo de **CVaR (Expected Shortfall)** al 99%.

---

## Changelog

### v2.1 — UI/UX Premium (2026-04)

- **Portada rediseñada** con sistema de diseño Premium SaaS completo
- **Créditos de autores** integrados en la portada como badges glassmorphism
- **Navegación por teclado:** `Espacio` para abrir el dashboard, `←` / `→` para cambiar de módulo
- **Glassmorphism** en tarjeta de métricas con `backdrop-filter: blur(24px) saturate(180%)`
- **Botón CTA pill** con gradiente, hover de escala y animación de pulso
- **Animaciones escalonadas** con curva `cubic-bezier(.22,1,.36,1)` para todos los elementos del hero
- **Corrección bug Reset:** `StreamlitAPIException` al escribir sobre key de widget ya instanciado
- **Eliminación del logo** del header para un layout más limpio
- **Descripción centrada** con neutralización del `text-align:left` de Streamlit

### v2.0 — Release inicial

- 8 módulos de análisis cuantitativo
- API REST con FastAPI
- Backtesting VaR (Kupiec), Markowitz, GARCH, señales automáticas
- Despliegue en Render y Streamlit Cloud

---

## Autores

- **Michael Morantes**
- **Germán Chamorro**

Universidad Santo Tomás — Proyecto Integrador de Teoría del Riesgo
