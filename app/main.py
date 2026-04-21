import sys
import os

# Asegura que la raíz del proyecto esté en el path sin importar desde dónde se corra
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import date, timedelta

st.set_page_config(
    page_title="RiskLab USTA · Risk Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Sistema de diseño ─────────────────────────────────────────────────────
from app.style import inject_styles
inject_styles()

# ── Backend ───────────────────────────────────────────────────────────────
from src.analysis.pipeline import run_portfolio_analysis

# ── Módulos de vista ──────────────────────────────────────────────────────
import app.views.m1_tecnico      as m1
import app.views.m2_rendimientos as m2
import app.views.m3_garch        as m3
import app.views.m4_capm         as m4
import app.views.m5_var          as m5
import app.views.m6_markowitz    as m6
import app.views.m7_senales      as m7
import app.views.m8_macro        as m8

# ── Tickers disponibles (universo + benchmark) ────────────────────────────
_ALL_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
    "JNJ", "PFE", "UNH",
    "JPM", "BAC", "GS", "MS",
    "XOM", "CVX",
    "GLD", "SLV",
    "BRK-B", "V", "MA",
    "SPY", "QQQ", "IWM",
]
_DEFAULT_TICKERS = ["AAPL", "JNJ", "JPM", "XOM", "GLD"]
_BENCHMARK       = "SPY"

# ── Estado de sesión ──────────────────────────────────────────────────────
_SESSION_DEFAULTS = {
    "prices":              None,
    "simple_ret":          None,
    "log_ret":             None,
    "show_flashcards":     False,
    "show_hero":           True,
    "_reset_tickers":      False,
}
for k, v in _SESSION_DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ═══════════════════════════════════════════════════════════════════════════
# HERO — HTML estático (sin comentarios ni líneas en blanco dentro del bloque)
# Regla CommonMark: un bloque HTML se cierra en la primera línea vacía →
# todo lo que siga se reinterpreta como Markdown y el indentado lo convierte
# en un código preformateado.  Solución: string sin indentación ni vacíos.
# ═══════════════════════════════════════════════════════════════════════════

_HERO_HTML = (
'<div class="hero-outer">'
'<div class="hero-blob hero-blob-1"></div>'
'<div class="hero-blob hero-blob-2"></div>'
'<div class="hero-blob hero-blob-3"></div>'
'<div class="hero-content">'
'<div class="hero-eyebrow"><span class="hero-eyebrow-dot"></span>'
'Teor\u00eda del Riesgo \u00b7 Universidad Santo Tom\u00e1s</div>'
'<div class="hero-title">RiskLab USTA'
'<span class="hero-title-thin">Risk Analytics Dashboard v2.0</span></div>'
'<div class="hero-desc" style="text-align:center;display:block;width:100%;">'
'Plataforma integrada de an\u00e1lisis cuantitativo de portafolios.<br>'
'Explora indicadores t\u00e9cnicos, modelos GARCH, CAPM,<br>'
'frontera eficiente de Markowitz, VaR y se\u00f1ales de trading.'
'</div>'
'<div class="hero-stats-bar">'
'<div class="hero-stat"><div class="hero-stat-val">8<em>m\u00f3d</em></div>'
'<div class="hero-stat-lbl">M\u00f3dulos</div></div>'
'<div class="hero-stat"><div class="hero-stat-val">20<em>+</em></div>'
'<div class="hero-stat-lbl">Indicadores</div></div>'
'<div class="hero-stat"><div class="hero-stat-val">\u221e</div>'
'<div class="hero-stat-lbl">Activos</div></div>'
'</div>'
'<div class="hero-authors">'
'<span class="hero-authors-label">Desarrollado por</span>'
'<div class="hero-authors-names">'
'<span class="hero-author-chip">Michael Morantes</span>'
'<span class="hero-authors-sep">&amp;</span>'
'<span class="hero-author-chip">Germ\u00e1n Chamorro</span>'
'</div>'
'<span class="hero-authors-uni">Universidad Santo Tom\u00e1s \u00b7 Teor\u00eda del Riesgo</span>'
'</div>'
'<div class="hero-tags">'
'<span class="hero-tag">\U0001f4ca T\u00e9cnico</span>'
'<span class="hero-tag">\U0001f4c8 Rendimientos</span>'
'<span class="hero-tag">\U0001f30a GARCH</span>'
'<span class="hero-tag">\u2696\ufe0f CAPM</span>'
'<span class="hero-tag">\U0001f4c9 VaR</span>'
'<span class="hero-tag">\U0001f3af Markowitz</span>'
'<span class="hero-tag">\U0001f4e1 Se\u00f1ales</span>'
'<span class="hero-tag">\U0001f310 Macro</span>'
'</div>'
'</div>'
'</div>'
)


def _render_hero():
    """Full-screen animated landing section. Hides when user clicks Launch."""
    with st.container():
        st.markdown('<span class="hero-cta-marker"></span>', unsafe_allow_html=True)
        st.markdown(_HERO_HTML, unsafe_allow_html=True)
        _, cta, _ = st.columns([3, 2, 3])
        with cta:
            st.markdown('<div class="hero-cta-col">', unsafe_allow_html=True)
            if st.button("🚀  Abrir Dashboard", key="hero_cta",
                         use_container_width=True, type="primary"):
                st.session_state.show_hero = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    components.html(
        """
        <script>
        (function() {
            window.parent.document.addEventListener('keydown', function handler(e) {
                if (e.code === 'Space' || e.key === ' ') {
                    e.preventDefault();
                    const btn = window.parent.document.querySelector(
                        '[data-testid="stBaseButton-primary"]'
                    );
                    if (btn) btn.click();
                }
            });
        })();
        </script>
        """,
        height=0,
    )


# ── Mostrar Hero o Dashboard ──────────────────────────────────────────────
if st.session_state.show_hero:
    _render_hero()
    st.stop()


# ═══════════════════════════════════════════════════════════════════════════
# HEADER — Branding + estado de datos
# ═══════════════════════════════════════════════════════════════════════════
col_brand, col_status = st.columns([5, 2.5], vertical_alignment="center")

with col_brand:
    st.markdown(
        """
        <div style="line-height:1.2;">
            <span style="
                font-size:1.7rem;font-weight:700;letter-spacing:-0.02em;
                background:linear-gradient(90deg,#3B82F6 0%,#06B6D4 60%,#8B5CF6 100%);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            ">RiskLab USTA</span>
            <br>
            <span style="font-size:0.7rem;color:#475569;font-weight:500;
                         text-transform:uppercase;letter-spacing:0.1em;">
                Teoría del Riesgo &nbsp;·&nbsp; Dashboard v2.0
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_status:
    if st.session_state.prices is not None:
        n    = len(st.session_state.prices)
        cols = list(st.session_state.prices.columns)
        label = ", ".join(cols[:4]) + (f" +{len(cols)-4}" if len(cols) > 4 else "")
        st.markdown(
            f'<div class="status-pill status-ok">● {n} sesiones · {label}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-pill status-idle">● Sin datos — pulsa Cargar</div>',
            unsafe_allow_html=True,
        )

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# PANEL DE CONTROLES — Glassmorphism container
# ═══════════════════════════════════════════════════════════════════════════
with st.container():
    # Marker span that CSS :has() uses to target this container
    st.markdown(
        '<span class="ctrl-panel-marker" style="display:none;"></span>',
        unsafe_allow_html=True,
    )

    # ── Fila 1: Fechas + Acciones ─────────────────────────────────────────
    ctrl_c1, ctrl_c2, ctrl_c3, ctrl_c4, ctrl_c5 = st.columns(
        [2.2, 2.2, 2.2, 2, 1.8], gap="medium"
    )

    _today = date.today()
    _two_years_ago = _today - timedelta(days=730)

    with ctrl_c1:
        start_date = st.date_input(
            "Fecha inicio",
            value=_two_years_ago,
            key="start_date_input",
        )

    with ctrl_c2:
        end_date = st.date_input(
            "Fecha fin",
            value=_today,
            key="end_date_input",
        )

    with ctrl_c3:
        st.markdown('<div style="height:1.6rem;"></div>', unsafe_allow_html=True)
        load_clicked = st.button(
            "⚡ Cargar Portfolio",
            use_container_width=True,
            type="primary",
        )

    with ctrl_c4:
        st.markdown('<div style="height:1.8rem;"></div>', unsafe_allow_html=True)
        show_flashcards = st.toggle(
            "🎓 Modo Defensa",
            value=st.session_state.show_flashcards,
            help="Activa flashcards y explicaciones para el jurado.",
        )
        st.session_state.show_flashcards = show_flashcards

    with ctrl_c5:
        st.markdown('<div style="height:1.6rem;"></div>', unsafe_allow_html=True)
        refresh_clicked = st.button(
            "🔄 Refrescar",
            use_container_width=True,
            disabled=st.session_state.prices is None,
            help="Recarga los datos con las fechas actuales.",
        )

    # ── Fila 2: Selector de activos ───────────────────────────────────────
    st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)
    tc1, tc2 = st.columns([5.5, 1.5], gap="medium")

    with tc1:
        _ms_default = _DEFAULT_TICKERS if st.session_state._reset_tickers else _DEFAULT_TICKERS
        if st.session_state._reset_tickers:
            st.session_state._reset_tickers = False
        selected_assets = st.multiselect(
            "Activos del portafolio",
            options=_ALL_TICKERS,
            default=_ms_default,
            key="ticker_multiselect",
            help=f"Selecciona los activos. '{_BENCHMARK}' siempre se añade como benchmark.",
            placeholder="Escribe o selecciona tickers…",
        )

    with tc2:
        st.markdown('<div style="height:1.65rem;"></div>', unsafe_allow_html=True)
        if st.button(
            "🏠 Reset",
            use_container_width=True,
            help="Restaurar portafolio por defecto.",
        ):
            st.session_state._reset_tickers = True
            del st.session_state["ticker_multiselect"]
            st.rerun()

# ── Construcción de la lista final de tickers ─────────────────────────────
_base = selected_assets if selected_assets else _DEFAULT_TICKERS
tickers = list(dict.fromkeys(_base + [_BENCHMARK]))   # deduplica, mantiene orden

# ── Acción Cargar / Refrescar ──────────────────────────────────────────────
if load_clicked or refresh_clicked:
    if len(tickers) < 2:
        st.warning("Selecciona al menos un activo además del benchmark SPY.")
    else:
        try:
            with st.spinner("Descargando precios y calculando rendimientos…"):
                prices, simple_ret, log_ret = run_portfolio_analysis(
                    tickers,
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d"),
                )
            st.session_state.prices     = prices
            st.session_state.simple_ret = simple_ret
            st.session_state.log_ret    = log_ret
            st.success(f"✅ {len(prices)} sesiones · {', '.join(tickers)} · {start_date} → {end_date}")
            st.rerun()
        except Exception as exc:
            st.error(f"Error al cargar datos: {exc}")

st.markdown(
    '<div class="section-divider" style="margin-top:0.5rem;"></div>',
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════════════════════════════
# NAVEGACIÓN — Tabs horizontales (un tab por módulo)
# ═══════════════════════════════════════════════════════════════════════════
tab_defs = [
    ("📊", "M1 · Técnico",       m1),
    ("📈", "M2 · Rendimientos",  m2),
    ("🌊", "M3 · GARCH",        m3),
    ("⚖️", "M4 · CAPM",          m4),
    ("📉", "M5 · VaR",           m5),
    ("🎯", "M6 · Markowitz",     m6),
    ("📡", "M7 · Señales",       m7),
    ("🌐", "M8 · Macro",         m8),
]

labels  = [f"{icon} {name}" for icon, name, _ in tab_defs]
modules = [mod for _, _, mod in tab_defs]

tabs = st.tabs(labels)

# ── Navegación con flechas del teclado ────────────────────────────────────
components.html(
    """
    <script>
    (function() {
        function navigate(dir) {
            const doc = window.parent.document;
            const tabList = doc.querySelectorAll('[data-baseweb="tab"]');
            if (!tabList.length) return;
            const active = Array.from(tabList).findIndex(
                t => t.getAttribute('aria-selected') === 'true'
            );
            const target = active + dir;
            if (target >= 0 && target < tabList.length) {
                tabList[target].click();
            }
        }
        window.parent.document.addEventListener('keydown', function(e) {
            const tag = document.activeElement
                ? document.activeElement.tagName : '';
            if (['INPUT','TEXTAREA','SELECT'].includes(tag)) return;
            if (e.key === 'ArrowRight') { e.preventDefault(); navigate(1);  }
            if (e.key === 'ArrowLeft')  { e.preventDefault(); navigate(-1); }
        });
    })();
    </script>
    """,
    height=0,
)

for tab, module in zip(tabs, modules):
    with tab:
        module.render(
            st.session_state.prices,
            st.session_state.simple_ret,
            st.session_state.log_ret,
        )
