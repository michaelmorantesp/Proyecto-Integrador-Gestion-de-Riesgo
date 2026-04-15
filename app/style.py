"""
style.py - Sistema de diseño RiskLab
Inyecta CSS global y exporta la paleta de colores para los gráficos Plotly.
"""
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# PALETA DE COLORES (centralizada – úsala en todos los módulos)
# ─────────────────────────────────────────────────────────────────────────────
COLORS = {
    # Fondos
    "bg_main":        "#0A0E1A",   # Fondo principal – navy profundo
    "bg_card":        "#111827",   # Tarjetas / contenedores
    "bg_sidebar":     "#0D1117",   # Sidebar
    "bg_surface":     "#1E2433",   # Superficies elevadas

    # Texto
    "text_primary":   "#E2E8F0",   # Texto principal
    "text_secondary": "#94A3B8",   # Labels, ayuda
    "text_muted":     "#475569",   # Texto desactivado

    # Acentos
    "accent_blue":    "#3B82F6",   # Primario – azul eléctrico suave
    "accent_teal":    "#06B6D4",   # Precio / línea principal
    "accent_violet":  "#8B5CF6",   # Indicadores secundarios
    "accent_indigo":  "#6366F1",   # Alternativo

    # Semánticos
    "success":        "#10B981",   # Verde suave – señal alcista
    "warning":        "#F59E0B",   # Ámbar – alerta neutra
    "danger":         "#F87171",   # Rojo suave – señal bajista
    "info":           "#38BDF8",   # Azul info

    # Gráficos (secuencia ordenada)
    "chart_1":        "#3B82F6",
    "chart_2":        "#06B6D4",
    "chart_3":        "#8B5CF6",
    "chart_4":        "#10B981",
    "chart_5":        "#F59E0B",
    "chart_6":        "#F87171",
}

# ─────────────────────────────────────────────────────────────────────────────
# TEMPLATE PLOTLY (reutilizable en todos los módulos)
# ─────────────────────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,0.8)",
    font=dict(family="Inter, system-ui, sans-serif", color=COLORS["text_primary"], size=13),
    title=dict(font=dict(size=16, color=COLORS["text_primary"]), x=0.02),
    legend=dict(
        bgcolor="rgba(17,24,39,0.6)",
        bordercolor=COLORS["bg_surface"],
        borderwidth=1,
        font=dict(size=12),
    ),
    xaxis=dict(
        gridcolor="rgba(71,85,105,0.3)",
        linecolor="rgba(71,85,105,0.5)",
        zerolinecolor="rgba(71,85,105,0.3)",
    ),
    yaxis=dict(
        gridcolor="rgba(71,85,105,0.3)",
        linecolor="rgba(71,85,105,0.5)",
        zerolinecolor="rgba(71,85,105,0.3)",
    ),
    margin=dict(l=40, r=20, t=50, b=40),
)


def apply_chart_layout(fig, height: int = 500, **kwargs):
    """Aplica el template estándar a cualquier figura Plotly."""
    layout = {**PLOTLY_LAYOUT, "height": height, **kwargs}
    fig.update_layout(**layout)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# CSS GLOBAL
# ─────────────────────────────────────────────────────────────────────────────
_CSS = """
/* ── Google Fonts ─────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ══════════════════════════════════════════════════════════════════════════
   HERO SECTION — Keyframes & Layout
   ══════════════════════════════════════════════════════════════════════════ */

@keyframes blob-drift-1 {
    0%, 100% { transform: translate(0px,   0px) scale(1.00); }
    25%       { transform: translate(40px, -60px) scale(1.08); }
    50%       { transform: translate(-30px, 30px) scale(0.95); }
    75%       { transform: translate(20px,  50px) scale(1.05); }
}
@keyframes blob-drift-2 {
    0%, 100% { transform: translate(0px,   0px) scale(1.00); }
    25%       { transform: translate(-50px, 40px) scale(1.12); }
    50%       { transform: translate(35px, -25px) scale(0.88); }
    75%       { transform: translate(-15px,-40px) scale(1.04); }
}
@keyframes blob-drift-3 {
    0%, 100% { transform: translate(-50%,-50%) scale(1.00); }
    33%       { transform: translate(-55%,-45%) scale(1.10); }
    66%       { transform: translate(-45%,-55%) scale(0.90); }
}
@keyframes hero-gradient-shift {
    0%, 100% { background-position: 0% 50%; }
    50%       { background-position: 100% 50%; }
}
@keyframes hero-fade-up {
    from { opacity: 0; transform: translateY(32px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes hero-pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(59,130,246,0.50), 0 8px 40px rgba(59,130,246,0.25); }
    50%       { box-shadow: 0 0 0 12px rgba(59,130,246,0), 0 16px 60px rgba(59,130,246,0.45); }
}
@keyframes shimmer {
    0%   { background-position: -200% center; }
    100% { background-position:  200% center; }
}
@keyframes grid-breathe {
    0%, 100% { opacity: 0.028; }
    50%       { opacity: 0.055; }
}
@keyframes scan-line {
    0%   { top: -3px; opacity: 0.5; }
    100% { top: 100%;  opacity: 0.0; }
}

.hero-outer {
    position: relative;
    min-height: 100vh;
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    overflow-x: hidden;
    background:
        radial-gradient(ellipse at 18% 55%, rgba(59,130,246,0.07) 0%, transparent 55%),
        radial-gradient(ellipse at 82% 45%, rgba(139,92,246,0.06) 0%, transparent 55%),
        #0A0E1A;
    padding: 5rem 3rem;
    box-sizing: border-box;
}
/* grid overlay */
.hero-outer::before {
    content: '';
    position: absolute; inset: 0;
    background-image:
        linear-gradient(rgba(59,130,246,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(59,130,246,0.04) 1px, transparent 1px);
    background-size: 56px 56px;
    animation: grid-breathe 9s ease-in-out infinite;
    pointer-events: none;
}
/* scan-line sweep */
.hero-outer::after {
    content: '';
    position: absolute;
    left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(59,130,246,0.35), rgba(6,182,212,0.22), transparent);
    animation: scan-line 8s linear infinite;
    pointer-events: none;
}

.hero-blob {
    position: absolute;
    border-radius: 50%;
    filter: blur(90px);
    pointer-events: none;
}
.hero-blob-1 {
    width: 680px; height: 680px;
    background: radial-gradient(circle, rgba(59,130,246,0.20), rgba(139,92,246,0.09));
    top: -180px; left: -140px;
    animation: blob-drift-1 20s ease-in-out infinite;
}
.hero-blob-2 {
    width: 580px; height: 580px;
    background: radial-gradient(circle, rgba(6,182,212,0.18), rgba(59,130,246,0.07));
    bottom: -140px; right: -90px;
    animation: blob-drift-2 24s ease-in-out infinite;
}
.hero-blob-3 {
    width: 340px; height: 340px;
    background: radial-gradient(circle, rgba(139,92,246,0.14), rgba(245,158,11,0.04));
    top: 50%; left: 50%;
    animation: blob-drift-3 15s ease-in-out infinite;
}

/* ── Hero Content wrapper ──────────────────────────────────────────────── */
.hero-content {
    position: relative;
    z-index: 2;
    text-align: center;
    max-width: 860px;
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0;
}

/* ── Eyebrow badge ─────────────────────────────────────────────────────── */
.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: rgba(59,130,246,0.08);
    border: 1px solid rgba(59,130,246,0.28);
    color: #60A5FA;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.20em;
    padding: 7px 24px;
    border-radius: 999px;
    margin-bottom: 2.8rem;
    animation: hero-fade-up 0.8s cubic-bezier(.22,1,.36,1) 0.1s both;
}
.hero-eyebrow-dot {
    width: 7px; height: 7px;
    background: #3B82F6;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 8px rgba(59,130,246,0.8);
}

/* ── Título principal ──────────────────────────────────────────────────── */
.hero-title {
    font-size: clamp(48px, 7vw, 92px);
    font-weight: 800;
    letter-spacing: -0.05em;
    line-height: 1.0;
    background: linear-gradient(270deg, #3B82F6 0%, #06B6D4 28%, #8B5CF6 58%, #3B82F6 100%);
    background-size: 400% 400%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: hero-gradient-shift 7s ease infinite,
               hero-fade-up 0.8s cubic-bezier(.22,1,.36,1) 0.25s both;
    margin-bottom: 0;
}
.hero-title-thin {
    display: block;
    font-size: clamp(15px, 1.8vw, 24px);
    font-weight: 300;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #475569;
    -webkit-text-fill-color: #475569;
    margin-top: 0.9rem;
    margin-bottom: 2.6rem;
    animation: hero-fade-up 0.8s cubic-bezier(.22,1,.36,1) 0.4s both;
}

/* ── Descripción ───────────────────────────────────────────────────────── */
.hero-desc {
    font-size: clamp(14px, 1.05vw, 17px);
    color: #64748B;
    line-height: 1.9;
    max-width: 520px;
    margin: 0 auto 3.2rem;
    text-align: center !important;
    animation: hero-fade-up 0.8s cubic-bezier(.22,1,.36,1) 0.55s both;
}
[data-testid="stMarkdown"]:has(.hero-outer),
[data-testid="stMarkdown"]:has(.hero-desc),
.hero-outer [data-testid="stMarkdown"],
.hero-content p { text-align: center !important; }

/* ── Stats bar — Glassmorphism premium ─────────────────────────────────── */
.hero-stats-bar {
    display: flex;
    justify-content: center;
    align-items: stretch;
    gap: 0;
    margin: 0 auto 3.2rem;
    background: rgba(15, 23, 42, 0.55);
    border: 1px solid rgba(255,255,255,0.07);
    border-top: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px;
    backdrop-filter: blur(24px) saturate(180%);
    -webkit-backdrop-filter: blur(24px) saturate(180%);
    padding: 2rem 3.6rem;
    max-width: 560px;
    width: 100%;
    box-shadow:
        0 20px 60px rgba(0,0,0,0.50),
        0 4px 16px rgba(59,130,246,0.10),
        inset 0 1px 0 rgba(255,255,255,0.06),
        inset 0 -1px 0 rgba(0,0,0,0.20);
    animation: hero-fade-up 0.8s cubic-bezier(.22,1,.36,1) 0.7s both;
}
.hero-stat {
    flex: 1;
    text-align: center;
    padding: 0 2rem;
}
.hero-stat + .hero-stat {
    border-left: 1px solid rgba(255,255,255,0.06);
}
.hero-stat-val {
    font-size: clamp(26px, 3vw, 40px);
    font-weight: 800;
    color: #F1F5F9;
    letter-spacing: -0.05em;
    line-height: 1;
}
.hero-stat-val em {
    font-style: normal;
    font-size: 0.55em;
    font-weight: 700;
    color: #3B82F6;
    margin-left: 3px;
    letter-spacing: 0.02em;
}
.hero-stat-lbl {
    font-size: 0.60rem;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    font-weight: 600;
    margin-top: 8px;
}

/* ── Author badges ─────────────────────────────────────────────────────── */
.hero-authors {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    margin: 0 auto 3.2rem;
    animation: hero-fade-up 0.8s cubic-bezier(.22,1,.36,1) 0.85s both;
}
.hero-authors-label {
    font-size: 0.60rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.22em;
    color: #334155;
}
.hero-authors-names {
    display: flex;
    align-items: center;
    gap: 1rem;
}
.hero-author-chip {
    font-size: 0.80rem;
    font-weight: 600;
    color: #94A3B8;
    background: rgba(15,23,42,0.60);
    border: 1px solid rgba(255,255,255,0.08);
    border-top: 1px solid rgba(255,255,255,0.13);
    padding: 8px 22px;
    border-radius: 999px;
    letter-spacing: 0.06em;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.30), inset 0 1px 0 rgba(255,255,255,0.06);
    transition: color 0.25s, border-color 0.25s, background 0.25s, box-shadow 0.25s, transform 0.2s;
}
.hero-author-chip:hover {
    color: #E2E8F0;
    border-color: rgba(59,130,246,0.40);
    background: rgba(59,130,246,0.12);
    box-shadow: 0 6px 20px rgba(59,130,246,0.20), inset 0 1px 0 rgba(255,255,255,0.08);
    transform: translateY(-2px);
}
.hero-authors-sep {
    font-size: 0.65rem;
    color: #1E293B;
    font-weight: 700;
    letter-spacing: 0.10em;
}
.hero-authors-uni {
    font-size: 0.56rem;
    color: #1E293B;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    font-weight: 500;
}

/* ── Module tags ───────────────────────────────────────────────────────── */
.hero-tags {
    display: flex;
    justify-content: center;
    gap: 0.55rem;
    flex-wrap: wrap;
    margin-bottom: 3.6rem;
    animation: hero-fade-up 0.8s cubic-bezier(.22,1,.36,1) 1.0s both;
}
.hero-tag {
    background: rgba(15,23,42,0.70);
    border: 1px solid rgba(255,255,255,0.06);
    color: #475569;
    font-size: 0.66rem;
    font-weight: 600;
    padding: 6px 15px;
    border-radius: 999px;
    letter-spacing: 0.08em;
    transition: color 0.20s, border-color 0.20s, background 0.20s,
                transform 0.18s, box-shadow 0.20s;
    cursor: default;
}
.hero-tag:hover {
    color: #93C5FD;
    border-color: rgba(59,130,246,0.38);
    background: rgba(59,130,246,0.09);
    transform: translateY(-2px);
    box-shadow: 0 4px 14px rgba(59,130,246,0.14);
}

/* ── CTA container: integrado dentro del hero ──────────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"]:has(.hero-cta-marker),
[data-testid="stVerticalBlock"]:has(.hero-cta-marker) {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin-top: -4rem !important;
    position: relative;
    z-index: 10;
}

/* ── CTA Button — Premium SaaS ─────────────────────────────────────────── */
.hero-cta-col .stButton > button {
    background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 45%, #06B6D4 100%) !important;
    background-size: 200% 200% !important;
    border: none !important;
    border-radius: 999px !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    padding: 1rem 3rem !important;
    text-transform: uppercase !important;
    animation: hero-pulse 2.8s ease-in-out infinite !important;
    transition: transform 0.22s cubic-bezier(.22,1,.36,1),
                filter 0.22s, box-shadow 0.22s !important;
}
.hero-cta-col .stButton > button:hover {
    transform: translateY(-4px) scale(1.05) !important;
    filter: brightness(1.15) !important;
    box-shadow: 0 20px 50px rgba(59,130,246,0.45) !important;
}

/* ══════════════════════════════════════════════════════════════════════════
   CONTROL PANEL — Glassmorphism via :has()
   ══════════════════════════════════════════════════════════════════════════ */

/* Glass panel wraps the container that holds the .ctrl-panel-marker span */
[data-testid="stVerticalBlockBorderWrapper"]:has(.ctrl-panel-marker) {
    background: rgba(17,24,39,0.60) !important;
    border: 1px solid rgba(59,130,246,0.16) !important;
    border-radius: 16px !important;
    padding: 1.1rem 1.4rem 1.2rem !important;
    backdrop-filter: blur(14px);
    box-shadow: 0 4px 24px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.03);
    margin-bottom: 0.2rem !important;
}

/* Multiselect container */
.stMultiSelect [data-baseweb="select"] > div {
    background: #111827 !important;
    border: 1px solid rgba(59,130,246,0.22) !important;
    border-radius: 8px !important;
    color: #E2E8F0 !important;
    font-size: 0.92rem !important;
    min-height: 40px !important;
}
.stMultiSelect [data-baseweb="select"] > div:focus-within {
    border-color: rgba(59,130,246,0.55) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
}
.stMultiSelect label {
    color: #64748B !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
}
/* Ticker tags inside multiselect */
[data-baseweb="tag"] {
    background: rgba(59,130,246,0.18) !important;
    border: 1px solid rgba(59,130,246,0.35) !important;
    border-radius: 6px !important;
    color: #93C5FD !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
}
[data-baseweb="tag"] span { color: #93C5FD !important; }
[data-baseweb="tag"] button svg { fill: #60A5FA !important; }

/* Dropdown list items */
[data-baseweb="menu"] {
    background: #111827 !important;
    border: 1px solid rgba(59,130,246,0.2) !important;
    border-radius: 10px !important;
}
[data-baseweb="menu"] li {
    color: #CBD5E1 !important;
    font-size: 0.9rem !important;
}
[data-baseweb="menu"] li:hover,
[data-baseweb="menu"] li[aria-selected="true"] {
    background: rgba(59,130,246,0.12) !important;
    color: #E2E8F0 !important;
}


/* ── Reset & Base ──────────────────────────────────────────────────────── */
html {
    font-size: 22px !important;
}
html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}

/* ── Sidebar oculto ────────────────────────────────────────────────────── */
section[data-testid="stSidebar"]  { display: none !important; }
[data-testid="collapsedControl"]  { display: none !important; }
button[kind="headerNoPadding"]    { display: none !important; }

/* ── Header / toolbar de Streamlit oculto en la portada ───────────────── */
.stApp:has(.hero-outer) header[data-testid="stHeader"],
.stApp:has(.hero-outer) [data-testid="stToolbar"],
.stApp:has(.hero-outer) [data-testid="stDecoration"],
.stApp:has(.hero-outer) #MainMenu {
    display: none !important;
}

/* ── Contenedor principal ──────────────────────────────────────────────── */
.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 3rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}

/* Cuando el hero está activo: elimina todo el padding del block-container */
.block-container:has(.hero-outer) {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
    width: 100% !important;
    overflow: visible !important;
}
/* Anula también el padding del wrapper padre de stApp */
.stApp:has(.hero-outer) > div:first-child {
    padding: 0 !important;
}

/* ── Fondo ─────────────────────────────────────────────────────────────── */
.stApp {
    background: linear-gradient(135deg, #0A0E1A 0%, #0D1424 100%) !important;
}

/* ══════════════════════════════════════════════════════════════════════════
   ESCALA TIPOGRÁFICA
   ══════════════════════════════════════════════════════════════════════════ */

/* H1 — Brand header */
h1 {
    background: linear-gradient(90deg, #3B82F6, #06B6D4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 800 !important;
    font-size: 2.2rem !important;
    letter-spacing: -0.03em !important;
    line-height: 1.2 !important;
    margin-bottom: 0.2rem !important;
}

/* H2 — Encabezado de módulo (st.header) */
h2 {
    color: #F1F5F9 !important;
    font-weight: 700 !important;
    font-size: 1.6rem !important;
    letter-spacing: -0.015em !important;
    line-height: 1.3 !important;
    margin-top: 0.25rem !important;
    margin-bottom: 0.2rem !important;
    padding-bottom: 0 !important;
    padding-left: 0.85rem !important;
    border-bottom: none !important;
    border-left: 3px solid #3B82F6 !important;
}

/* H3 — Sección dentro de módulo (st.subheader) */
h3 {
    color: #CBD5E1 !important;
    font-weight: 600 !important;
    font-size: 1.2rem !important;
    letter-spacing: -0.01em !important;
    line-height: 1.4 !important;
    margin-top: 1.8rem !important;
    margin-bottom: 0.5rem !important;
    padding-bottom: 0.45rem !important;
    border-bottom: 1px solid rgba(59, 130, 246, 0.14) !important;
}

/* Párrafo / texto de cuerpo */
.stMarkdown p {
    color: #CBD5E1 !important;
    font-size: 1rem !important;
    line-height: 1.75 !important;
}

/* Subtítulo de módulo (clase usada por module_header()) */
.module-subtitle {
    color: #64748B;
    font-size: 0.95rem;
    font-weight: 400;
    line-height: 1.6;
    margin: 0.2rem 0 0 1.1rem;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* ── Separadores ────────────────────────────────────────────────────────── */
hr {
    height: 1px !important;
    background: linear-gradient(
        90deg, rgba(59,130,246,0.35), rgba(6,182,212,0.15), transparent
    ) !important;
    border: none !important;
    margin: 1.75rem 0 !important;
}

.section-divider {
    height: 1px;
    background: linear-gradient(
        90deg, rgba(59,130,246,0.4), rgba(6,182,212,0.2), transparent
    );
    margin: 1.25rem 0;
    border: none;
}


/* ── Divisor tras el header de módulo ──────────────────────────────────── */
.module-divider {
    height: 1px;
    background: linear-gradient(
        90deg, rgba(59,130,246,0.5), rgba(6,182,212,0.25), transparent
    );
    margin: 0.9rem 0 0 0;
    border: none;
}

/* ══════════════════════════════════════════════════════════════════════════
   MÉTRICAS (st.metric)
   ══════════════════════════════════════════════════════════════════════════ */
[data-testid="metric-container"] {
    background: #111827 !important;
    border: 1px solid rgba(59,130,246,0.18) !important;
    border-radius: 12px !important;
    padding: 1rem 1.2rem !important;
    transition: border-color 0.2s, transform 0.15s, box-shadow 0.2s;
}
[data-testid="metric-container"]:hover {
    border-color: rgba(59,130,246,0.4) !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 24px rgba(59,130,246,0.1);
}
[data-testid="metric-container"] label {
    color: #64748B !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #F1F5F9 !important;
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    line-height: 1.2 !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 0.88rem !important;
    font-weight: 500 !important;
}

/* ══════════════════════════════════════════════════════════════════════════
   DATAFRAMES / TABLAS
   ══════════════════════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(59,130,246,0.12) !important;
    border-radius: 10px !important;
    overflow: hidden;
}

/* ── Plotly ─────────────────────────────────────────────────────────────── */
.js-plotly-plot {
    border-radius: 10px !important;
    overflow: hidden;
}

/* ── Alertas / Info boxes ───────────────────────────────────────────────── */
.stAlert {
    border-radius: 10px !important;
    border-left-width: 3px !important;
    font-size: 0.98rem !important;
    line-height: 1.7 !important;
}
[data-testid="stNotification"] {
    border-radius: 10px !important;
}

/* ── Botones ────────────────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #2563EB, #3B82F6) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.01em !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.2s !important;
    box-shadow: 0 2px 8px rgba(59,130,246,0.25) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1D4ED8, #2563EB) !important;
    box-shadow: 0 4px 16px rgba(59,130,246,0.4) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1D4ED8, #3B82F6) !important;
    box-shadow: 0 2px 10px rgba(59,130,246,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #1E40AF, #1D4ED8) !important;
    box-shadow: 0 4px 18px rgba(59,130,246,0.45) !important;
    transform: translateY(-1px) !important;
}

/* ── Sliders ─────────────────────────────────────────────────────────────── */

/* Contenedor — sin márgenes extra, ocupa todo el ancho */
.stSlider {
    padding-left: 0 !important;
    padding-right: 0 !important;
    width: 100% !important;
}
.stSlider [data-baseweb="slider"] {
    padding-top: 0.3rem !important;
    padding-bottom: 0.1rem !important;
}

/* Riel vacío (gris) */
.stSlider [data-baseweb="slider"] > div:first-child {
    background: rgba(59,130,246,0.15) !important;
    height: 5px !important;
    border-radius: 999px !important;
}

/* Riel relleno (azul degradado) */
.stSlider [data-testid="stSliderTrackFill"] {
    background: linear-gradient(90deg, #3B82F6, #06B6D4) !important;
    height: 5px !important;
    border-radius: 999px !important;
}

/* Thumb (manija) */
.stSlider [role="slider"] {
    background: #ffffff !important;
    border: 3px solid #3B82F6 !important;
    width: 18px !important;
    height: 18px !important;
    border-radius: 50% !important;
    box-shadow: 0 0 0 4px rgba(59,130,246,0.18) !important;
    transition: box-shadow 0.2s, border-color 0.2s !important;
}
.stSlider [role="slider"]:hover,
.stSlider [role="slider"]:focus {
    border-color: #06B6D4 !important;
    box-shadow: 0 0 0 7px rgba(59,130,246,0.22) !important;
}

/* Valores min / max del tick bar */
.stSlider [data-testid="stTickBarMin"],
.stSlider [data-testid="stTickBarMax"] {
    color: #475569 !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
}

/* Label del slider */
.stSlider label {
    color: #64748B !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
}

/* ── Selectbox ──────────────────────────────────────────────────────────── */
.stSelectbox [data-baseweb="select"] > div {
    background: #111827 !important;
    border: 1px solid rgba(59,130,246,0.22) !important;
    border-radius: 8px !important;
    color: #E2E8F0 !important;
    font-size: 0.95rem !important;
}
.stSelectbox label {
    color: #64748B !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
}

/* ── Number / Text inputs ───────────────────────────────────────────────── */
.stNumberInput label, .stTextInput label {
    color: #64748B !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
}

/* ── Expander ───────────────────────────────────────────────────────────── */
details {
    border: 1px solid rgba(59,130,246,0.13) !important;
    border-radius: 10px !important;
    padding: 0.4rem 0.75rem !important;
    background: rgba(17,24,39,0.7) !important;
    margin-bottom: 0.75rem !important;
}
summary {
    color: #64748B !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    cursor: pointer;
}
summary:hover { color: #94A3B8 !important; }

/* ── Checkbox ───────────────────────────────────────────────────────────── */
.stCheckbox label {
    color: #94A3B8 !important;
    font-size: 0.92rem !important;
}

/* ── Spinner ────────────────────────────────────────────────────────────── */
.stSpinner div { border-top-color: #3B82F6 !important; }

/* ── Card helper ────────────────────────────────────────────────────────── */
.risklab-card {
    background: #111827;
    border: 1px solid rgba(59,130,246,0.16);
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}

/* ── Badges ─────────────────────────────────────────────────────────────── */
.badge-buy     { background:#064E3B; color:#34D399; border-radius:6px; padding:3px 12px; font-weight:600; font-size:0.85rem; letter-spacing:0.04em; }
.badge-sell    { background:#450A0A; color:#FCA5A5; border-radius:6px; padding:3px 12px; font-weight:600; font-size:0.85rem; letter-spacing:0.04em; }
.badge-neutral { background:#1E2433; color:#94A3B8; border-radius:6px; padding:3px 12px; font-weight:600; font-size:0.85rem; letter-spacing:0.04em; }

/* ══════════════════════════════════════════════════════════════════════════
   TABS — Pill style moderno
   ══════════════════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: rgba(17,24,39,0.9) !important;
    padding: 5px 6px !important;
    border-radius: 12px !important;
    border: 1px solid rgba(59,130,246,0.14) !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3);
    flex-wrap: nowrap;
    width: 100% !important;
    box-sizing: border-box !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: #64748B !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    padding: 8px 0 !important;
    border: none !important;
    outline: none !important;
    transition: color 0.18s, background 0.18s !important;
    white-space: nowrap;
    letter-spacing: 0.01em;
    flex: 1 1 0 !important;
    text-align: center !important;
    justify-content: center !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #94A3B8 !important;
    background: rgba(59,130,246,0.08) !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #1D4ED8 0%, #3B82F6 100%) !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 10px rgba(59,130,246,0.38) !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"]    { display: none !important; }
.stTabs [data-baseweb="tab-panel"]     { padding-top: 1.5rem !important; }
/* Focus ring para navegación con teclado */
.stTabs [data-baseweb="tab"]:focus-visible {
    outline: 2px solid #3B82F6 !important;
    outline-offset: 2px !important;
    border-radius: 8px !important;
}

/* ══════════════════════════════════════════════════════════════════════════
   CONTROLES — Date inputs, botón, toggle
   ══════════════════════════════════════════════════════════════════════════ */
.stDateInput > label {
    font-size: 0.78rem !important;
    color: #64748B !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    margin-bottom: 3px !important;
}
.stDateInput input {
    background: #111827 !important;
    border: 1px solid rgba(59,130,246,0.2) !important;
    border-radius: 8px !important;
    color: #E2E8F0 !important;
    font-size: 0.95rem !important;
    padding: 8px 11px !important;
    transition: border-color 0.2s !important;
}
.stDateInput input:focus {
    border-color: rgba(59,130,246,0.6) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important;
}

/* Toggle */
.stToggle label {
    color: #94A3B8 !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
}
[data-testid="stToggle"] span[aria-checked="true"] {
    background-color: #3B82F6 !important;
}

/* ══════════════════════════════════════════════════════════════════════════
   STATUS PILLS
   ══════════════════════════════════════════════════════════════════════════ */
.status-pill {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    float: right;
}
.status-ok {
    background: rgba(16,185,129,0.1);
    color: #10B981;
    border: 1px solid rgba(16,185,129,0.25);
}
.status-idle {
    background: rgba(71,85,105,0.1);
    color: #475569;
    border: 1px solid rgba(71,85,105,0.2);
}
"""


_JS = """
<script>
(function () {
    // Evitar registrar el listener más de una vez en re-runs de Streamlit
    if (window.__risklabNavInit) return;
    window.__risklabNavInit = true;

    document.addEventListener('keydown', function (e) {
        const el  = document.activeElement || {};
        const tag = (el.tagName || '').toUpperCase();
        const inInput = ['INPUT', 'TEXTAREA', 'SELECT'].includes(tag) || el.isContentEditable;

        // Escape → libera el foco de cualquier control y devuelve el foco a las pestañas
        if (e.key === 'Escape' && inInput) {
            el.blur();
            const active = document.querySelector('[data-baseweb="tab-list"] [aria-selected="true"]');
            if (active) active.focus();
            return;
        }

        const tabs = document.querySelectorAll('[data-baseweb="tab-list"] [role="tab"]');
        if (!tabs.length) return;

        // Ctrl+1-8 → salta al módulo desde CUALQUIER contexto (incluso dentro de inputs)
        if (e.ctrlKey && e.key >= '1' && e.key <= '8') {
            const idx = parseInt(e.key, 10) - 1;
            if (tabs[idx]) {
                e.preventDefault();
                tabs[idx].click();
                tabs[idx].focus();
            }
            return;
        }

        // Las teclas sin modificador solo funcionan cuando NO hay un input activo
        if (inInput) return;

        // Teclas 1-8 → saltar directamente al módulo
        if (e.key >= '1' && e.key <= '8') {
            const idx = parseInt(e.key, 10) - 1;
            if (tabs[idx]) {
                e.preventDefault();
                tabs[idx].click();
                tabs[idx].focus();
            }
            return;
        }

        // ← → navegar entre pestañas (con wrap-around)
        if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
            const active = document.querySelector('[data-baseweb="tab-list"] [aria-selected="true"]');
            if (!active) return;
            const cur = Array.from(tabs).indexOf(active);
            let next = e.key === 'ArrowRight' ? cur + 1 : cur - 1;
            if (next < 0) next = tabs.length - 1;
            if (next >= tabs.length) next = 0;
            e.preventDefault();
            tabs[next].click();
            tabs[next].focus();
        }
    });
})();
</script>
"""


def inject_styles():
    """
    Llama esta función UNA VEZ en app/main.py para aplicar
    el sistema de diseño global.
    """
    st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)
    st.markdown(_JS, unsafe_allow_html=True)


def module_header(title: str, subtitle: str = "") -> None:
    """
    Header de módulo con jerarquía visual clara.
    Reemplaza el patrón st.header() + st.markdown(subtítulo).

    Args:
        title:    Título del módulo (puede incluir emoji al inicio).
        subtitle: Descripción corta que aparece bajo el título.
    """
    subtitle_html = (
        f'<p class="module-subtitle">{subtitle}</p>' if subtitle else ""
    )
    st.markdown(
        f"""
        <div style="margin-bottom:0.25rem;">
            <div style="
                color:#F1F5F9;
                font-size:1.6rem;
                font-weight:700;
                letter-spacing:-0.015em;
                line-height:1.3;
                padding-left:0.85rem;
                border-left:3px solid #3B82F6;
            ">{title}</div>
            {subtitle_html}
            <div class="module-divider"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(text: str) -> None:
    """
    Título de sección dentro de un módulo.
    Alternativa estilizada a st.subheader() cuando se requiere
    más control visual (p.ej. antes de un bloque de gráficos).

    Args:
        text: Texto de la sección (puede incluir emoji).
    """
    st.markdown(
        f"""
        <div style="
            color:#CBD5E1;
            font-size:1.2rem;
            font-weight:600;
            letter-spacing:-0.01em;
            line-height:1.4;
            margin-top:1.8rem;
            margin-bottom:0.5rem;
            padding-bottom:0.45rem;
            border-bottom:1px solid rgba(59,130,246,0.14);
        ">{text}</div>
        """,
        unsafe_allow_html=True,
    )


def flashcard(titulo: str, texto: str, tipo: str = "info") -> None:
    """
    Renderiza una tarjeta de defensa académica compacta bajo un gráfico.

    Args:
        titulo: Etiqueta corta que aparece en la cabecera de la tarjeta.
        texto:  Explicación — máximo 2-3 líneas, puede incluir HTML básico.
        tipo:   'info' (azul) | 'success' (verde) | 'warning' (ámbar) | 'danger' (rojo).
    """
    paleta = {
        "info":    ("#3B82F6", "rgba(59,130,246,0.10)", "rgba(59,130,246,0.30)"),
        "success": ("#10B981", "rgba(16,185,129,0.10)", "rgba(16,185,129,0.30)"),
        "warning": ("#F59E0B", "rgba(245,158,11,0.10)",  "rgba(245,158,11,0.30)"),
        "danger":  ("#F87171", "rgba(248,113,113,0.10)", "rgba(248,113,113,0.30)"),
    }
    color, bg, border = paleta.get(tipo, paleta["info"])
    st.markdown(
        f"""
        <div style="
            background:{bg};
            border:1px solid {border};
            border-left:3px solid {color};
            border-radius:8px;
            padding:0.65rem 1rem;
            margin-top:0.5rem;
        ">
            <div style="font-size:0.75rem;color:{color};font-weight:700;
                        text-transform:uppercase;letter-spacing:0.09em;margin-bottom:5px;">
                🎓 Defensa · {titulo}
            </div>
            <div style="color:#CBD5E1;font-size:0.96rem;line-height:1.65;">{texto}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
