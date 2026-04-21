import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from src.analysis.portfolio import calculate_beta, CAPM_expected_return
from src.ingestion.macro_api import fetch_risk_free_rate
from app.style import COLORS, apply_chart_layout, flashcard, module_header


def render(prices, simple_ret, log_ret):
    module_header(
        "🛡️ Riesgo Sistemático (Beta) y CAPM",
        "Regresión CAPM, cálculo de Betas, e inferencia del riesgo sistemático para todo el portafolio.",
    )

    if log_ret is None or log_ret.empty:
        st.info("⬅️ Carga el portafolio desde el panel lateral para comenzar.")
        return

    benchmark = "SPY"
    if benchmark not in simple_ret.columns:
        st.error("El benchmark SPY no está en los datos.")
        return

    # ── Macro ─────────────────────────────────────────────────────────────
    st.subheader("🌐 Entorno Macro")
    try:
        rf_series = fetch_risk_free_rate("2023-01-01", "2024-01-01")
        rf_rate = float(rf_series.iloc[-1])
    except Exception:
        rf_rate = 0.045

    bench_data = simple_ret[benchmark].dropna()
    market_return = float(bench_data.mean() * 252)

    c1, c2, c3 = st.columns(3)
    c1.metric("Tasa Libre de Riesgo (Rf)", f"{rf_rate*100:.2f}%", help="DGS10 USA – último disponible")
    c2.metric("Rendimiento Mercado (Anual)", f"{market_return*100:.2f}%", help="SPY anualizado")
    c3.metric("Prima de Riesgo (Rm - Rf)", f"{(market_return - rf_rate)*100:.2f}%")

    st.markdown("---")

    # ── Beta individual ───────────────────────────────────────────────────
    st.subheader("📐 Beta y Rendimiento Esperado CAPM")
    asset = st.selectbox("Activo a evaluar", [c for c in simple_ret.columns if c != benchmark], key="m4_asset")
    asset_data = simple_ret[asset].dropna()

    beta = calculate_beta(asset_data, bench_data)
    beta = calculate_beta(asset_data, bench_data)
    # Convert scalar references if they come out of pandas slightly differently
    beta_val = float(beta) if not isinstance(beta, pd.Series) else float(beta.iloc[0]) 
    capm = CAPM_expected_return(beta_val, rf_rate, market_return)

    ca, cb, cc = st.columns(3)
    ca.metric("Beta (β)", f"{beta_val:.4f}")
    cb.metric("Retorno Esperado CAPM", f"{capm*100:.2f}%")
    cc.metric("Retorno Real (Anual)", f"{asset_data.mean()*252*100:.2f}%")

    if beta_val < 0.8:
        st.success(f"**{asset} es DEFENSIVO** (β={beta_val:.2f} < 1) · Mitiga el riesgo sistémico del mercado.")
    elif beta_val > 1.2:
        st.warning(f"**{asset} es AGRESIVO** (β={beta_val:.2f} > 1) · Amplifica movimientos del mercado.")
    else:
        st.info(f"**{asset} es NEUTRO** (β≈1) · Se mueve en línea con el mercado.")

    # ── Scatter OLS ───────────────────────────────────────────────────────
    st.markdown("---")
    fig = px.scatter(
        x=bench_data, y=asset_data, opacity=0.4,
        labels={"x": f"Rendimiento {benchmark}", "y": f"Rendimiento {asset}"},
        trendline="ols",
        color_discrete_sequence=[COLORS["accent_blue"]],
    )
    # Mejorar línea de tendencia
    for trace in fig.data:
        if trace.mode == "lines":
            trace.line.color = COLORS["accent_teal"]
            trace.line.width = 2

    apply_chart_layout(fig, height=480, title=f"Dispersión CAPM: {asset} vs {benchmark} (pendiente = β)")
    st.plotly_chart(fig, use_container_width=True)

    if st.session_state.get("show_flashcards"):
        lost_pct = beta_val * 10
        tipo_beta = "danger" if beta_val > 1.2 else ("success" if beta_val < 0.8 else "info")
        flashcard(
            "Dispersión CAPM (β)",
            f"Con β = {beta_val:.2f}, si el mercado cae 10%, {asset} cae aproximadamente {lost_pct:.1f}% — evidenciando su nivel de exposición al riesgo de mercado. La dispersión vertical alrededor de la línea representa el riesgo propio de la empresa, que la teoría financiera establece que no debería ser compensado por el mercado.",
            tipo_beta,
        )

    # ── Tabla Resumen del Portafolio ──────────────────────────────────────
    st.markdown("---")
    st.subheader("📋 Tabla Resumen del Portafolio")
    summary_data = []
    for col in simple_ret.columns:
        if col == benchmark:
            continue
        c_data = simple_ret[col].dropna()
        c_beta = float(calculate_beta(c_data, bench_data))
        c_capm = CAPM_expected_return(c_beta, rf_rate, market_return)
        c_real = float(c_data.mean() * 252)
        
        if c_beta < 0.8:
            cls = "Defensivo 🛡️"
        elif c_beta > 1.2:
            cls = "Agresivo 🚀"
        else:
            cls = "Neutro ⚖️"
            
        summary_data.append({
            "Activo": col,
            "Beta (β)": round(c_beta, 4),
            "E(R) CAPM": f"{c_capm*100:.2f}%",
            "Retorno Real (Anual)": f"{c_real*100:.2f}%",
            "Clasificación": cls
        })
    
    df_summary = pd.DataFrame(summary_data).set_index("Activo")
    st.dataframe(df_summary, use_container_width=True)

    # ── Discusión de Riesgo Sistemático ───────────────────────────────────
    st.markdown("---")
    st.subheader("📖 Riesgo Sistemático vs. Idiosincrático")
    st.info(
        "**Sistemático (β):** Riesgo del mercado global (inflación, recesiones). No se diversifica — es el único que el mercado compensa con mayor rendimiento esperado.\n\n"
        "**Idiosincrático:** Riesgo propio de cada empresa. Se elimina diversificando; el mercado no lo compensa. En el gráfico: la línea de regresión es el riesgo sistemático; la nube vertical es el idiosincrático."
    )
