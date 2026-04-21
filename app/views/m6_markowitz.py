import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.analysis.portfolio import simulate_markowitz_portfolios, get_optimal_portfolios
from app.style import COLORS, apply_chart_layout, flashcard, module_header


def render(prices, simple_ret, log_ret):
    module_header(
        "🎯 Optimización de Portafolio – Markowitz",
        "Frontera eficiente vía simulación de Montecarlo · Portafolios de Mínima Varianza y Máximo Sharpe.",
    )

    if simple_ret is None or simple_ret.empty:
        st.info("⬅️ Carga el portafolio desde el panel lateral para comenzar.")
        return

    assets = [c for c in simple_ret.columns if c != "SPY"]
    data = simple_ret[assets]

    # ── Heatmap Correlación ───────────────────────────────────────────────
    st.subheader("🗂️ Matriz de Correlación")
    corr = data.corr()

    fig_corr = px.imshow(
        corr, text_auto=".2f",
        color_continuous_scale=[[0, "#1E3A5F"], [0.5, "#111827"], [1, "#7C3AED"]],
        zmin=-1, zmax=1,
        aspect="auto",
    )
    apply_chart_layout(fig_corr, height=380, title="Correlación de Activos del Portafolio")
    st.plotly_chart(fig_corr, use_container_width=True)

    # Diagnóstico automático
    c_mask = np.triu(np.ones(corr.shape), k=1).astype(bool)
    c_unstack = corr.where(c_mask).unstack().dropna()
    min_pair = c_unstack.idxmin()
    max_pair = c_unstack.idxmax()

    col_a, col_b = st.columns(2)
    col_a.markdown(f"""
    <div style="background:#111827;border:1px solid rgba(16,185,129,0.25);border-radius:10px;padding:1rem;">
        <div style="font-size:0.7rem;color:#475569;text-transform:uppercase;letter-spacing:0.06em;">🛡️ mejor par diversificador</div>
        <div style="font-size:1.1rem;font-weight:700;color:#34D399;margin:0.3rem 0;">{min_pair[0]} · {min_pair[1]}</div>
        <div style="font-size:0.8rem;color:#64748B;">Correlación: {c_unstack[min_pair]:.2f}</div>
    </div>
    """, unsafe_allow_html=True)
    col_b.markdown(f"""
    <div style="background:#111827;border:1px solid rgba(248,113,113,0.25);border-radius:10px;padding:1rem;">
        <div style="font-size:0.7rem;color:#475569;text-transform:uppercase;letter-spacing:0.06em;">⚠️ mayor riesgo de concentración</div>
        <div style="font-size:1.1rem;font-weight:700;color:#FCA5A5;margin:0.3rem 0;">{max_pair[0]} · {max_pair[1]}</div>
        <div style="font-size:0.8rem;color:#64748B;">Correlación: {c_unstack[max_pair]:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Frontera Eficiente ────────────────────────────────────────────────
    st.subheader("🚀 Frontera Eficiente")
    col_sim, col_target = st.columns(2)
    n_sims = col_sim.number_input("Portafolios a simular", 1000, 50000, 10000, 1000, help="Representan la nube de montecarlo", key="m6_nsims")
    target_ret = col_target.number_input("Rendimiento Objetivo Anualizado", 0.0, 2.0, 0.15, 0.01, help="Ej: 0.15 para buscar el portafolio ideal con 15% de retorno", key="m6_target")

    if st.button("Calcular Frontera de Markowitz", key="m6_btn_calc"):
        with st.spinner("Simulando portafolios aleatorios…"):
            portfolios = simulate_markowitz_portfolios(data, n_sims)
            optimal    = get_optimal_portfolios(portfolios)

            min_vol    = optimal["Minima Varianza"]
            max_sharpe = optimal["Maximo Sharpe"]

            fig = px.scatter(
                portfolios, x="Volatilidad", y="Rendimiento",
                color="Sharpe_Ratio",
                color_continuous_scale=[[0, "#1E293B"], [0.5, "#3B82F6"], [1, "#06B6D4"]],
                opacity=0.5,
                hover_data=portfolios.columns.tolist(),
                labels={"Volatilidad": "Volatilidad (Anual)", "Rendimiento": "Rendimiento (Anual)"},
            )

            fig.add_trace(go.Scatter(
                x=[min_vol["Volatilidad"]], y=[min_vol["Rendimiento"]],
                mode="markers+text",
                marker=dict(color=COLORS["danger"], size=16, symbol="star"),
                text=["Mín. Varianza"], textposition="top right",
                textfont=dict(color=COLORS["danger"], size=11),
                name="Mínima Varianza",
            ))
            fig.add_trace(go.Scatter(
                x=[max_sharpe["Volatilidad"]], y=[max_sharpe["Rendimiento"]],
                mode="markers+text",
                marker=dict(color=COLORS["warning"], size=16, symbol="star"),
                text=["Máx. Sharpe"], textposition="top right",
                textfont=dict(color=COLORS["warning"], size=11),
                name="Máximo Sharpe",
            ))

            # ── Búsqueda de Portafolio Objetivo ─────────────────────────────
            tolerance = 0.015  # Rango de +- 1.5%
            candidates = portfolios[np.abs(portfolios['Rendimiento'] - target_ret) < tolerance]
            
            if not candidates.empty:
                # El más eficiente (menor volatilidad) dentro de ese margen de retorno
                custom_opt = candidates.loc[candidates['Volatilidad'].idxmin()]
                
                fig.add_trace(go.Scatter(
                    x=[custom_opt["Volatilidad"]], y=[custom_opt["Rendimiento"]],
                    mode="markers+text",
                    marker=dict(color=COLORS["accent_teal"], size=16, symbol="diamond"),
                    text=[f"Objetivo ({target_ret*100:.0f}%)"], textposition="bottom right",
                    textfont=dict(color=COLORS["accent_teal"], size=11),
                    name="Portafolio Objetivo",
                ))
            else:
                custom_opt = None

            # ── Corrección de Leyenda (Evitar cruce con ColorBar) ────────────
            fig.update_layout(
                legend=dict(
                    yanchor="top", y=0.98,
                    xanchor="left", x=0.02,
                    bgcolor="rgba(17,24,39,0.7)", bordercolor="rgba(255,255,255,0.1)", borderwidth=1
                )
            )

            apply_chart_layout(fig, height=560, title="Frontera Eficiente de Markowitz")
            st.plotly_chart(fig, use_container_width=True)

            # Tabla de composición
            st.markdown("#### 📋 Composición de Portafolios Óptimos")
            pesos_cols = [c for c in portfolios.columns if "Peso_" in c]
            metric_cols = ["Rendimiento", "Volatilidad", "Sharpe_Ratio"]

            # Acoplar portafolio objetivo si existe
            if custom_opt is not None:
                summary = pd.DataFrame([min_vol, max_sharpe, custom_opt], index=["Mínima Varianza", "Máximo Sharpe", f"Objetivo (~{target_ret*100:.1f}%)"])
                st.success(f"Búsqueda exitosa: Se halló un portafolio eficiente con Rendimiento **{custom_opt['Rendimiento']*100:.2f}%** sujeto a la volatilidad óptima del **{custom_opt['Volatilidad']*100:.2f}%**.")
            else:
                summary = pd.DataFrame([min_vol, max_sharpe], index=["Mínima Varianza", "Máximo Sharpe"])
                st.warning(f"No se encontraron portafolios simulados cerca del {target_ret*100:.1f}%. Intenta aumentar el número de simulaciones o ajusta una tasa realista.")

            display_cols = metric_cols + pesos_cols
            st.dataframe(
                summary[display_cols].style.format({c: "{:.4f}" for c in display_cols}),
                use_container_width=True,
            )

            if st.session_state.get("show_flashcards"):
                flashcard(
                    "Frontera Eficiente de Markowitz",
                    f"La estrella roja señala la combinación de activos con menor riesgo posible (volatilidad {min_vol['Volatilidad']*100:.1f}%), mientras la estrella ámbar identifica la mejor relación retorno-riesgo con un índice de eficiencia de {max_sharpe['Sharpe_Ratio']:.2f}. Ningún portafolio puede posicionarse arriba y a la izquierda de esta curva — representa el límite matemático de lo que la diversificación puede lograr.",
                    "info",
                )
