import streamlit as st
import pandas as pd
import numpy as np
import scipy.stats as scipy_stats
from src.analysis.volatility import compare_volatility_models, fit_garch_model
from app.style import COLORS, apply_chart_layout, flashcard, module_header


def render(prices, simple_ret, log_ret):
    module_header(
        "📉 Modelado de Volatilidad ARCH/GARCH",
        "Comparación de especificaciones por criterios AIC/BIC y estimación de la varianza condicional.",
    )

    with st.expander("📖 ¿Por qué GARCH?", expanded=True):
        st.info(
            "Los rendimientos reales presentan **volatility clustering**: la varianza actual depende de varianzas pasadas (efecto ARCH), lo que invalida el supuesto de varianza constante.\n\n"
            "GARCH modela esa dinámica capturando colas pesadas y memoria de largo plazo — necesario para calcular VaR sin sesgo."
        )

    if log_ret is None or log_ret.empty:
        st.info("⬅️ Carga el portafolio desde el panel lateral para comenzar.")
        return

    ticker = st.selectbox("Activo (se recomienda uno con volatility clustering visible)", log_ret.columns, key="m3_ticker")
    data_ret = log_ret[ticker].dropna()

    # ── Comparación de modelos ────────────────────────────────────────────
    st.subheader("📊 Comparación de Especificaciones")
    with st.spinner("Estimando ARCH/GARCH…"):
        try:
            df = compare_volatility_models(data_ret)
            st.dataframe(
                df.style.highlight_min(subset=["AIC", "BIC"], color="#064E3B"),
                use_container_width=True,
            )
            best = df["AIC"].idxmin()
            st.success(f"**Mejor modelo por AIC:** {best} · Un AIC/BIC menor implica mejor balance ajuste-parsimonia.")
        except Exception as e:
            st.error(f"Error al ajustar GARCH: {e}")

    st.markdown("---")

    # ── Detalle de modelo ─────────────────────────────────────────────────
    st.subheader("🔬 Estimación Detallada y Pronóstico")
    col1, col2, col3, col4 = st.columns(4)
    selected_model = col1.selectbox("Tipo", ["GARCH", "ARCH"], key="m3_model_type")
    p = col2.number_input("Rezago p", 1, 5, 1, key="m3_p")
    q = col3.number_input("Rezago q", 0, 5, 1, key="m3_q")
    n_steps = col4.number_input("Días", 1, 60, 5, help="Horizonte de pronóstico N-pasos", key="m3_nsteps")

    if st.button("Estimar modelo", key="m3_btn_estimar"):
        with st.spinner("Optimizando log-verosimilitud…"):
            try:
                res = fit_garch_model(data_ret, model_type=selected_model, p=p, q=q)
                mu_val = res.params.get("mu", 0.0)

                # Parámetros de varianza condicional
                omega = res.params.get("omega", 0)
                alpha_tex = "".join([
                    f" + {v:.4f}\\epsilon_{{t-{k.split('[')[1].replace(']','')}}}^2"
                    for k, v in res.params.items() if "alpha" in k
                ])
                beta_tex = "".join([
                    f" + {v:.4f}\\sigma_{{t-{k.split('[')[1].replace(']','')}}}^2"
                    for k, v in res.params.items() if "beta" in k
                ])
                st.latex(rf"r_t = {mu_val:.5f} + \epsilon_t")
                st.latex(rf"\sigma_t^2 = {omega:.6f} {alpha_tex} {beta_tex}")

                # Estacionariedad
                a_sum = sum(v for k, v in res.params.items() if "alpha" in k)
                b_sum = sum(v for k, v in res.params.items() if "beta" in k)
                persist = a_sum + b_sum
                if persist < 1:
                    st.success(f"Condición de estacionariedad: α+β = {persist:.4f} < 1 ✅ El proceso revierte a la media.")
                else:
                    st.warning(f"⚠️ α+β = {persist:.4f} ≥ 1 · La varianza tiende a explotar (IGARCH-like).")

                # Pronóstico N-Pasos
                st.markdown(f"#### Pronóstico de Volatilidad N-Pasos ({n_steps} días)")
                import plotly.graph_objects as go
                forecasts = res.forecast(horizon=n_steps)
                vol_forecast = np.sqrt(forecasts.variance.dropna().iloc[-1]) / 100  # Desescalar

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=[f"t+{i+1}" for i in range(n_steps)],
                    y=vol_forecast.values,
                    marker_color=COLORS["accent_blue"],
                    opacity=0.8,
                    name="Vol. Esperada",
                ))
                apply_chart_layout(fig, height=280, title=f"Varianza Condicional Futura ({n_steps}d)")
                st.plotly_chart(fig, use_container_width=True)

                # ── Diagnóstico de Residuos ───────────────────────────────────
                st.markdown("---")
                st.markdown("#### Diagnóstico sobre Residuos Estandarizados")
                std_resid = res.std_resid.dropna()
                
                col_res, col_jb = st.columns([2, 1])
                with col_res:
                    fig_res = go.Figure()
                    fig_res.add_trace(go.Scatter(
                        x=std_resid.index, y=std_resid, mode='markers', 
                        name='Residuos Est.', 
                        marker=dict(color=COLORS["accent_blue"], size=4, opacity=0.7)
                    ))
                    # Bandas de referencia
                    fig_res.add_hline(y=0, line_width=1, line_dash="solid", line_color="rgba(226,232,240,0.3)")
                    fig_res.add_hline(y=3, line_width=1, line_dash="dot", line_color="rgba(248,113,113,0.7)", annotation_text="+3σ")
                    fig_res.add_hline(y=-3, line_width=1, line_dash="dot", line_color="rgba(248,113,113,0.7)", annotation_text="-3σ")
                    
                    apply_chart_layout(fig_res, height=280, title="Dispersión de Residuos Estandarizados")
                    st.plotly_chart(fig_res, use_container_width=True)
                
                with col_jb:
                    # Test Jarque-Bera
                    jb_stat, p_value = scipy_stats.jarque_bera(std_resid)
                    is_normal = p_value > 0.05
                    icon = "✅" if is_normal else "❌"
                    conc = "Normales" if is_normal else "Anormales (Colas pesadas)"
                    st.markdown(f"""
                    <div style="background:#111827;border:1px solid rgba(59,130,246,0.2);border-radius:10px;padding:1rem;height:100%;">
                        <div style="font-size:0.7rem;color:#475569;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.5rem;">Jarque-Bera a Residuos</div>
                        <div style="font-size:1.15rem;font-weight:700;color:#E2E8F0;">{icon} {conc}</div>
                        <div style="font-size:0.78rem;color:#64748B;margin-top:0.4rem;">Stat: {jb_stat:.2f} · p: {p_value:.2e}</div>
                        <div style="font-size:0.75rem;color:#94A3B8;margin-top:1rem;">
                            <b>Nota:</b> Si el GARCH absorbió la varianza pero los residuos siguen anormales, la base teórica requiere una distribución <i>t-Student</i> en lugar de una <i>Normal</i>.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with st.expander("📋 Resumen econométrico completo del modelo"):
                    st.text(res.summary())

                if st.session_state.get("show_flashcards"):
                    h1, hn = vol_forecast.iloc[0], vol_forecast.iloc[-1]
                    tend = "creciente 📈" if hn > h1 else "decreciente 📉"
                    tipo_vol = "warning" if hn > h1 else "success"
                    flashcard(
                        f"GARCH — pronóstico de volatilidad",
                        f"Día 1: <b>{h1:.4f}</b> → Día {n_steps}: <b>{hn:.4f}</b> ({tend}). "
                        f"<b>α+β = {persist:.3f}</b>: cuanto más cerca de 1, más tiempo persiste el impacto de un shock — "
                        f"por eso el GARCH supera a la volatilidad histórica fija para calcular VaR.",
                        tipo_vol,
                    )

            except Exception as e:
                st.error(f"Error al estimar: {e}")
