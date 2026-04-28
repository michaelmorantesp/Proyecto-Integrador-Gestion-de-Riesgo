import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from src.analysis.risk_models import (
    compare_risk_models, calculate_kupiec_test
)


def _calculate_christoffersen_test_local(series: pd.Series, var: float) -> dict:
    """Función local para evitar problemas de caché en el módulo de riesgo."""
    from scipy import stats
    clean = series.dropna()
    hit = (clean < var).astype(int).values
    n00 = n01 = n10 = n11 = 0
    for i in range(len(hit) - 1):
        if hit[i] == 0 and hit[i+1] == 0: n00 += 1
        elif hit[i] == 0 and hit[i+1] == 1: n01 += 1
        elif hit[i] == 1 and hit[i+1] == 0: n10 += 1
        elif hit[i] == 1 and hit[i+1] == 1: n11 += 1
    p01 = n01 / (n00 + n01) if (n00 + n01) > 0 else 0
    p11 = n11 / (n10 + n11) if (n10 + n11) > 0 else 0
    p = (n01 + n11) / (n00 + n11 + n01 + n10) if (n00 + n11 + n01 + n10) > 0 else 0
    try:
        l_null = (n00 + n10) * np.log(1 - p) + (n01 + n11) * np.log(p)
        l_alt = n00 * np.log(1 - p01) + n01 * np.log(p01) + n10 * np.log(1 - p11) + n11 * np.log(p11)
        lr_ind = -2 * (l_null - l_alt)
        p_value = 1 - stats.chi2.cdf(lr_ind, df=1)
    except:
        lr_ind = 0.0; p_value = 1.0
    return {'LR Independencia': round(lr_ind, 4), 'P-Value': round(p_value, 4), 'Independiente': p_value > 0.05, 'Rachas (n11)': n11}

from app.style import COLORS, apply_chart_layout, flashcard, module_header


def render(prices, simple_ret, log_ret):
    module_header(
        "📉 Valor en Riesgo (VaR) y CVaR",
        "Cuantificación del riesgo de cola: paramétrico, histórico, Montecarlo, KDE Epanechnikov y Backtesting Kupiec.",
    )

    if log_ret is None or log_ret.empty:
        st.info("⬅️ Carga el portafolio desde el panel lateral para comenzar.")
        return

    asset = st.selectbox("Activo", simple_ret.columns, key="m5_ticker")
    data = simple_ret[asset].dropna()

    col_c1, col_c2, col_c3 = st.columns(3)
    conf_1   = col_c1.slider("Confianza estándar", 0.90, 0.99, 0.95, 0.01, key="m5_conf1")
    conf_2   = col_c2.slider("Confianza stress",   0.90, 0.99, 0.99, 0.01, key="m5_conf2")
    num_sims = col_c3.number_input("Sim. Montecarlo", 10000, 100000, 10000, 5000, key="m5_numsims")

    # ── Tabla comparativa ─────────────────────────────────────────────────
    st.subheader("📊 Tabla Comparativa de Modelos de Riesgo")
    with st.spinner("Calculando VaR y CVaR…"):
        try:
            risk_df = compare_risk_models(data, conf_1, conf_2, num_sims)
            styled = (risk_df * 100).style.format("{:.3f}%").map(
                lambda x: "color:#F87171" if pd.notna(x) and x < 0 else "color:#94A3B8"
            )
            st.dataframe(styled, use_container_width=True)
        except Exception as e:
            st.error(f"Error: {e}")
            return

    st.markdown("---")

    # ── Backtesting por Modelo (Kupiec + Christoffersen) ──────────────────
    st.subheader("🔬 Backtesting Comparativo")
    
    models_to_test = ["Paramétrico Diario", "Histórico Diario", "Montecarlo Diario"]
    bt_results = []
    row_label = f"Riesgo {int(conf_1*100)}%"
    
    for m_name in models_to_test:
        v_val = risk_df.loc[row_label, m_name]
        kup = calculate_kupiec_test(data, v_val, conf_1)
        chr_test = _calculate_christoffersen_test_local(data, v_val)
        
        is_robust = kup["Aceptado"] and chr_test["Independiente"]
        veredicto = "✅ Robusto" if is_robust else ("⚠️ Cobertura OK" if kup["Aceptado"] else "❌ Inválido")
        
        bt_results.append({
            "Modelo": m_name.replace(" Diario", ""),
            "Fallos Obs": kup["Fallos Observados"],
            "Fallos Esp": kup["Fallos Esperados"],
            "Kupiec (p-val)": kup["P-Value"],
            "Indep (p-val)": chr_test["P-Value"],
            "Veredicto": veredicto
        })
    
    bt_df = pd.DataFrame(bt_results)
    st.dataframe(bt_df, use_container_width=True, hide_index=True)

    # Nota explicativa
    st.caption("ℹ️ **Kupiec:** Evalúa si la cantidad de fallos es correcta. **Indep:** Evalúa si los fallos ocurren en rachas (clusters).")

    # Necesitamos var_param para el gráfico de serie temporal siguiente
    var_param = risk_df.loc[row_label, "Paramétrico Diario"]

    st.markdown("---")

    # ── Gráfico de Backtesting (Serie Temporal) ──────────────────────────
    st.subheader("🎞️ Serie de Tiempo: Violaciones de VaR (Excedencias)")
    
    fig_bt = go.Figure()
    # Rendimientos
    fig_bt.add_trace(go.Scatter(
        x=data.index, y=data * 100,
        mode="lines", name="Rendimientos Reales",
        line=dict(color=COLORS["accent_indigo"], width=1),
        opacity=0.4
    ))
    # Línea de VaR
    fig_bt.add_trace(go.Scatter(
        x=data.index, y=[var_param * 100] * len(data),
        mode="lines", name=f"Límite VaR ({int(conf_1*100)}%)",
        line=dict(color=COLORS["danger"], dash="dash", width=2)
    ))
    # Hits (Violaciones)
    hits = data[data < var_param]
    fig_bt.add_trace(go.Scatter(
        x=hits.index, y=hits * 100,
        mode="markers", name="Fallo (Excedencia)",
        marker=dict(color=COLORS["danger"], size=8, symbol="x")
    ))
    
    apply_chart_layout(fig_bt, height=400, title="Backtesting Histórico: Puntos de Ruptura del Modelo")
    st.plotly_chart(fig_bt, use_container_width=True)

    st.markdown("---")
