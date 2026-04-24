import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import scipy.stats as scipy_stats
from src.analysis.returns import calculate_descriptive_stats, run_normality_tests
from app.style import COLORS, apply_chart_layout, flashcard, module_header


def render(prices, simple_ret, log_ret):
    module_header(
        "📊 Rendimientos y Propiedades Empíricas",
        "Análisis estadístico de log-rendimientos, pruebas de normalidad y hechos estilizados.",
    )

    if log_ret is None or log_ret.empty:
        st.info("⬅️ Carga el portafolio desde el panel lateral para comenzar.")
        return

    ticker = st.selectbox("Activo", log_ret.columns, key="m2_ticker")
    
    # ── Series de Rendimientos ───────────────────────────────────────────
    st.subheader("🧮 Cálculo de Rendimientos (Simples vs Logarítmicos)")
    
    col_chart, col_data = st.columns([2, 1])
    
    with col_chart:
        fig_rets = go.Figure()
        fig_rets.add_trace(go.Scatter(x=simple_ret.index, y=simple_ret[ticker], mode='lines', name='Rentabilidad Simple', line=dict(color=COLORS['accent_blue'], width=1), opacity=0.8))
        fig_rets.add_trace(go.Scatter(x=log_ret.index, y=log_ret[ticker], mode='lines', name='Log-Rendimiento', line=dict(color=COLORS['warning'], width=1), opacity=0.8))
        apply_chart_layout(fig_rets, height=300, title=f"Evolución Diaria - {ticker}")
        st.plotly_chart(fig_rets, use_container_width=True)

    with col_data:
        df_preview = pd.DataFrame({
            "Precio":     prices[ticker],
            "Ret. Simple": simple_ret[ticker],
            "Log-Ret":    log_ret[ticker]
        }).dropna()
        st.dataframe(df_preview.tail(10).style.format("{:.4f}"), use_container_width=True, height=300)
    
    st.markdown("---")

    stats = calculate_descriptive_stats(log_ret[ticker])

    # ── Estadísticas Descriptivas ──────────────────────────────────────────
    st.subheader("📋 Estadísticas Descriptivas")
    
    # Mostrar tabla como lo solicitó el usuario
    stats_df = pd.DataFrame({
        "Métrica": ["Media Diaria", "Volatilidad (Desv. Std)", "Asimetría (Skewness)", "Curtosis Exceso", "Mínimo", "Máximo"],
        "Valor": [
            f"{stats['Media']*100:.4f}%", 
            f"{stats['Volatilidad (Desv. Std)']*100:.4f}%", 
            f"{stats['Asimetría (Skewness)']:.4f}", 
            f"{stats['Curtosis']:.4f}",
            f"{stats['Mínimo']*100:.4f}%",
            f"{stats['Máximo']*100:.4f}%"
        ]
    }).set_index("Métrica")
    
    col_kpi, col_table = st.columns([2, 1])
    
    with col_kpi:
        c1, c2 = st.columns(2)
        c3, c4 = st.columns(2)
        c1.metric("Media Log-Ret", f"{stats['Media']*100:.4f}%")
        c2.metric("Volatilidad Diaria", f"{stats['Volatilidad (Desv. Std)']*100:.4f}%")
        c3.metric("Asimetría (Skewness)", f"{stats['Asimetría (Skewness)']:.3f}")
        c4.metric("Curtosis Exceso", f"{stats['Curtosis']:.3f}")
        
    with col_table:
        st.dataframe(stats_df, use_container_width=True)

    st.markdown("---")

    # ── Histograma ────────────────────────────────────────────────────────
    st.subheader("📐 Distribución de Log-Rendimientos")
    data_ret = log_ret[ticker].dropna()

    df_t = st.slider(
        "Grados de libertad — distribución t-Student (ν)",
        min_value=2, max_value=50, value=5, step=1,
        key="m2_df_t",
        help="Valores bajos de ν producen colas más pesadas. ν → ∞ converge a la Normal.",
    )

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=data_ret, nbinsx=120,
        marker_color=COLORS["accent_blue"], opacity=0.55,
        name="Empírico",
    ))

    x_val = np.linspace(stats["Mínimo"], stats["Máximo"], 300)
    mu, sigma = stats["Media"], stats["Volatilidad (Desv. Std)"]
    scale = len(data_ret) * (stats["Máximo"] - stats["Mínimo"]) / 120

    # Curva Normal teórica
    pdf_norm = scipy_stats.norm.pdf(x_val, loc=mu, scale=sigma)
    fig.add_trace(go.Scatter(
        x=x_val, y=pdf_norm * scale, mode="lines",
        name="Normal Teórica",
        line=dict(color=COLORS["danger"], width=2, dash="dash"),
    ))

    # Curva t-Student ajustada a misma media y desv. estándar
    pdf_t = scipy_stats.t.pdf(x_val, df=df_t, loc=mu, scale=sigma)
    fig.add_trace(go.Scatter(
        x=x_val, y=pdf_t * scale, mode="lines",
        name=f"t-Student (ν={df_t})",
        line=dict(color=COLORS["accent_teal"], width=2),
    ))

    apply_chart_layout(fig, height=420, title=f"Log-rendimientos {ticker}")
    st.plotly_chart(fig, use_container_width=True)

    if st.session_state.get("show_flashcards"):
        kurt = stats["Curtosis"]
        skew = stats["Asimetría (Skewness)"]
        tail_desc = "los eventos extremos ocurren con mayor frecuencia de la esperada" if kurt > 0 else "la distribución presenta variabilidad más contenida que la normal"
        skew_desc = "con caídas que tienden a ser más bruscas que los rebotes" if skew < 0 else "con rebotes que tienden a superar las caídas en magnitud"
        flashcard(
            "Distribución de rendimientos",
            f"Los datos muestran que {tail_desc}, {skew_desc}. Este comportamiento — conocido como 'colas pesadas' — justifica el uso de modelos que van más allá de la estadística clásica.",
            "warning",
        )

    st.markdown("---")

    # ── Q-Q Plot y Boxplot ────────────────────────────────────────────────
    st.subheader("🔎 Análisis de Normalidad Visual y Atípicos")
    col_qq, col_box = st.columns(2)

    with col_qq:
        qq_val = scipy_stats.probplot(data_ret, dist="norm", fit=True)
        fig_qq = go.Figure()
        fig_qq.add_trace(go.Scatter(
            x=qq_val[0][0], y=qq_val[0][1], mode='markers',
            name='Cuantiles Empíricos', marker=dict(color=COLORS['accent_blue'], opacity=0.7)
        ))
        
        x_trend = np.array([min(qq_val[0][0]), max(qq_val[0][0])])
        y_trend = qq_val[1][1] + qq_val[1][0] * x_trend
        fig_qq.add_trace(go.Scatter(
            x=x_trend, y=y_trend, mode='lines',
            name='Ref. Normal', line=dict(color=COLORS['danger'], dash='dash', width=2)
        ))
        apply_chart_layout(fig_qq, height=350, title=f"Gráfico Q-Q contra Normal")
        st.plotly_chart(fig_qq, use_container_width=True)

    with col_box:
        fig_box = go.Figure()
        fig_box.add_trace(go.Box(
            y=data_ret, name=ticker,
            marker_color=COLORS['accent_violet'],
            boxpoints='outliers' # Resalta los valores atípicos
        ))
        apply_chart_layout(fig_box, height=350, title=f"Boxplot (Detección de Outliers)")
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("---")

    # ── Tests de normalidad ───────────────────────────────────────────────
    st.subheader("🧪 Pruebas de Normalidad")
    tests = run_normality_tests(data_ret)

    col_jb, col_sw = st.columns(2)
    jb = tests.get("Jarque-Bera", {})
    if jb:
        icon = "✅" if jb["is_normal"] else "❌"
        conclusion = "No se rechaza H0 (Sigue Normal)" if jb["is_normal"] else "Se rechaza H0 (No normal) al 95%"
        col_jb.markdown(f"""
        <div style="background:#111827;border:1px solid rgba(59,130,246,0.2);border-radius:10px;padding:1rem;">
            <div style="font-size:0.7rem;color:#475569;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.5rem;">Jarque-Bera</div>
            <div style="font-size:1.15rem;font-weight:700;color:#E2E8F0;">{icon} {conclusion}</div>
            <div style="font-size:0.78rem;color:#64748B;margin-top:0.4rem;">Estadístico: {jb['statistic']:.2f} · p-valor: {jb['p_value']:.2e}</div>
        </div>
        """, unsafe_allow_html=True)

    sw = tests.get("Shapiro-Wilk", {})
    if sw:
        icon = "✅" if sw["is_normal"] else "❌"
        conclusion = "No se rechaza H0 (Sigue Normal)" if sw["is_normal"] else "Se rechaza H0 (No normal) al 95%"
        col_sw.markdown(f"""
        <div style="background:#111827;border:1px solid rgba(59,130,246,0.2);border-radius:10px;padding:1rem;">
            <div style="font-size:0.7rem;color:#475569;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.5rem;">Shapiro-Wilk{sw.get('note','')}</div>
            <div style="font-size:1.15rem;font-weight:700;color:#E2E8F0;">{icon} {conclusion}</div>
            <div style="font-size:0.78rem;color:#64748B;margin-top:0.4rem;">Estadístico: {sw['statistic']:.4f} · p-valor: {sw['p_value']:.2e}</div>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.get("show_flashcards"):
        flashcard(
            "Tests de normalidad",
            "Las pruebas estadísticas rechazan que los rendimientos sigan una distribución normal, lo que significa que los modelos clásicos subestiman el riesgo real. Esto valida directamente el uso de métodos históricos y de simulación en el análisis de riesgo del Módulo 5.",
            "danger",
        )

    # ── Hechos Estilizados ────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📖 Hechos Estilizados")
    st.info(
        "**Colas pesadas (Fat Tails):** Los eventos extremos ocurren con mayor frecuencia de lo que predice la Normal — visible en el Q-Q y en la curtosis en exceso.\n\n"
        "**Clustering de volatilidad:** Periodos de alta volatilidad se agrupan; los choques negativos amplifican la varianza más que los positivos (efecto apalancamiento, skewness < 0)."
    )
