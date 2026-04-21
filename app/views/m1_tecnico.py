import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.analysis.technical import (
    calculate_sma, calculate_ema, calculate_rsi,
    calculate_macd, calculate_bollinger_bands, calculate_stochastic,
)
from app.style import COLORS, apply_chart_layout, flashcard, module_header


def render(prices, simple_ret, log_ret):
    module_header(
        "📈 Análisis Técnico",
        "Indicadores técnicos en tiempo real: medias móviles, RSI, MACD y Bandas de Bollinger.",
    )

    if prices is None or prices.empty:
        st.info("⬅️ Carga el portafolio desde el panel lateral para comenzar.")
        return

    ticker = st.selectbox("Activo", prices.columns, key="m1_ticker")
    data = prices[ticker].dropna()

    st.markdown("---")

    # ── Price Action + Bollinger ──────────────────────────────────────────
    st.subheader("💹 Price Action · Medias Móviles · Bollinger Bands")
    with st.expander("📖 Bollinger · MA", expanded=False):
        st.info(
            "**Bollinger:** Canal de ±σ alrededor de la MA. Precio en banda sup. = sobrecompra; en banda inf. = sobreventa; canal estrecho anticipa movimiento brusco.\n\n"
            "**SMA / EMA:** Tendencia dominante. EMA reacciona más rápido a cambios recientes que la SMA."
        )
    col1, col2 = st.columns(2)
    with col1:
        ma_window = st.slider("Ventana MA", 5, 200, 20, key="ma_w")
    with col2:
        bb_std = st.slider("Std. Bollinger", 1.0, 4.0, 2.0, 0.1, key="bb_s")

    sma = calculate_sma(data, ma_window)
    ema = calculate_ema(data, ma_window)
    upper_band, lower_band = calculate_bollinger_bands(data, ma_window, bb_std)

    fig = go.Figure()

    # Relleno Bollinger
    fig.add_trace(go.Scatter(
        x=list(data.index) + list(data.index[::-1]),
        y=list(upper_band) + list(lower_band[::-1]),
        fill="toself",
        fillcolor="rgba(59,130,246,0.06)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Canal Bollinger",
        showlegend=True,
    ))
    fig.add_trace(go.Scatter(
        x=data.index, y=upper_band, mode="lines",
        line=dict(color="rgba(59,130,246,0.35)", width=1, dash="dot"),
        name="Banda Sup.",
    ))
    fig.add_trace(go.Scatter(
        x=data.index, y=lower_band, mode="lines",
        line=dict(color="rgba(59,130,246,0.35)", width=1, dash="dot"),
        name="Banda Inf.",
    ))
    fig.add_trace(go.Scatter(
        x=data.index, y=data, mode="lines",
        name="Precio", line=dict(color=COLORS["accent_teal"], width=2),
    ))
    fig.add_trace(go.Scatter(
        x=data.index, y=sma, mode="lines",
        name=f"SMA {ma_window}", line=dict(color=COLORS["accent_violet"], width=1.5, dash="dot"),
    ))
    fig.add_trace(go.Scatter(
        x=data.index, y=ema, mode="lines",
        name=f"EMA {ma_window}", line=dict(color=COLORS["warning"], width=1.5, dash="dash"),
    ))
    apply_chart_layout(fig, height=480)
    st.plotly_chart(fig, use_container_width=True)

    if st.session_state.get("show_flashcards"):
        ultimo = data.iloc[-1]
        if ultimo > upper_band.iloc[-1]:
            estado = "ha superado el límite estadístico superior — señal de agotamiento alcista"
            tipo_fc = "danger"
        elif ultimo < lower_band.iloc[-1]:
            estado = "ha caído por debajo del límite estadístico inferior — zona técnica de sobreventa"
            tipo_fc = "success"
        else:
            estado = "se mantiene dentro del canal de volatilidad — en fase de consolidación"
            tipo_fc = "info"
        flashcard(
            "Bollinger Bands",
            f"{ticker} a ${ultimo:.2f} {estado}. Cuando el precio alcanza los extremos de este canal, la tendencia pierde fuerza y estadísticamente tiende a revertirse.",
            tipo_fc,
        )

    # ── RSI & MACD ────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("⚡ Osciladores: RSI y MACD")
    col_rsi, col_macd = st.columns(2)

    with col_rsi:
        with st.expander("📖 RSI", expanded=False):
            st.info("Oscila 0–100. **>70** = sobrecompra (posible corrección). **<30** = sobreventa (posible rebote).")
        rsi_window = st.number_input("Ventana RSI", 2, 100, 14, key="m1_rsi_w")
        rsi = calculate_rsi(data, rsi_window)

        fig_rsi = go.Figure()
        fig_rsi.add_hrect(y0=70, y1=100, fillcolor="rgba(248,113,113,0.07)", line_width=0)
        fig_rsi.add_hrect(y0=0, y1=30,  fillcolor="rgba(16,185,129,0.07)",  line_width=0)
        fig_rsi.add_trace(go.Scatter(
            x=data.index, y=rsi, name="RSI",
            line=dict(color=COLORS["accent_violet"], width=1.8),
        ))
        fig_rsi.add_hline(y=70, line_dash="dot", line_color="rgba(248,113,113,0.6)", annotation_text="70")
        fig_rsi.add_hline(y=30, line_dash="dot", line_color="rgba(16,185,129,0.6)",  annotation_text="30")
        apply_chart_layout(fig_rsi, height=280, title="RSI")
        st.plotly_chart(fig_rsi, use_container_width=True)

        if st.session_state.get("show_flashcards"):
            v = rsi.iloc[-1]
            if v > 70:
                s = f"registra {v:.1f} — el mercado acumula presión compradora insostenible, anticipando una corrección"
                t = "danger"
            elif v < 30:
                s = f"cayó a {v:.1f} — el activo está siendo vendido de forma excesiva, generando una oportunidad de rebote"
                t = "success"
            else:
                s = f"registra {v:.1f} — la tendencia mantiene momentum equilibrado, sin señal de agotamiento"
                t = "info"
            flashcard(
                "RSI",
                f"{ticker} {s}. Este indicador mide el agotamiento de la tendencia: valores por encima de 70 o por debajo de 30 son zonas de alerta crítica.",
                t,
            )

    with col_macd:
        with st.expander("📖 MACD", expanded=False):
            st.info("Diferencia entre dos MAs. MACD cruza sobre Signal = alcista; cruza abajo = bajista. Histograma positivo = momentum alcista.")
        macd_line, signal_line, macd_hist = calculate_macd(data)
        colors_bar = [COLORS["success"] if v >= 0 else COLORS["danger"] for v in macd_hist]

        fig_macd = go.Figure()
        fig_macd.add_trace(go.Bar(
            x=data.index, y=macd_hist, name="Histograma",
            marker_color=colors_bar, opacity=0.7,
        ))
        fig_macd.add_trace(go.Scatter(
            x=data.index, y=macd_line, name="MACD",
            line=dict(color=COLORS["accent_blue"], width=1.8),
        ))
        fig_macd.add_trace(go.Scatter(
            x=data.index, y=signal_line, name="Signal",
            line=dict(color=COLORS["warning"], width=1.5, dash="dash"),
        ))
        apply_chart_layout(fig_macd, height=280, title="MACD")
        st.plotly_chart(fig_macd, use_container_width=True)

        if st.session_state.get("show_flashcards"):
            v = macd_hist.iloc[-1]
            s = "confirma momentum alcista — la tendencia gana fuerza" if v > 0 else "señala presión bajista — la tendencia pierde impulso"
            t = "success" if v > 0 else "danger"
            flashcard(
                "MACD",
                f"El histograma de {ticker} {s}. Cuando las barras crecen en un mismo sentido, la aceleración del precio está siendo respaldada por convicción del mercado.",
                t,
            )

    # ── Oscilador Estocástico ─────────────────────────────────────────────
    st.markdown("---")
    st.subheader("⚖️ Oscilador Estocástico (%K y %D)")
    with st.expander("📖 Estocástico", expanded=False):
        st.info("Compara el precio de cierre con su rango histórico. **>80** = sobrecompra, **<20** = sobreventa. Cruce %K sobre %D en zona extrema = señal de compra.")

    col_stoch_1, col_stoch_2 = st.columns([1, 3])
    with col_stoch_1:
        stoch_window = st.number_input("Ventana %K", 5, 50, 14, key="stoch_kw")
        stoch_d_window = st.number_input("Ventana %D (Suavizado)", 2, 20, 3, key="stoch_dw")

    with col_stoch_2:
        k_stoch, d_stoch = calculate_stochastic(data, data, data, k_window=stoch_window, d_window=stoch_d_window)

        fig_stoch = go.Figure()
        fig_stoch.add_hrect(y0=80, y1=100, fillcolor="rgba(248,113,113,0.07)", line_width=0)
        fig_stoch.add_hrect(y0=0, y1=20,  fillcolor="rgba(16,185,129,0.07)",  line_width=0)

        fig_stoch.add_trace(go.Scatter(
            x=data.index, y=k_stoch, name="%K",
            line=dict(color=COLORS["accent_blue"], width=1.8),
        ))
        fig_stoch.add_trace(go.Scatter(
            x=data.index, y=d_stoch, name="%D",
            line=dict(color=COLORS["warning"], width=1.5, dash="dash"),
        ))

        fig_stoch.add_hline(y=80, line_dash="dot", line_color="rgba(248,113,113,0.6)", annotation_text="80")
        fig_stoch.add_hline(y=20, line_dash="dot", line_color="rgba(16,185,129,0.6)",  annotation_text="20")
        apply_chart_layout(fig_stoch, height=280, title=f"Estocástico (%K, %D) - {ticker}")
        st.plotly_chart(fig_stoch, use_container_width=True)

        if st.session_state.get("show_flashcards"):
            k_val = k_stoch.iloc[-1]
            d_val = d_stoch.iloc[-1]
            if k_val > 80 and d_val > 80:
                stoc_alert = "ambas líneas confirman sobrecompra — la presión compradora está estadísticamente agotada"
                t = "danger"
            elif k_val < 20 and d_val < 20:
                stoc_alert = "ambas líneas confirman sobreventa — el mercado ha castigado este activo en exceso"
                t = "success"
            else:
                stoc_alert = "se encuentran en zona neutral — sin señal de agotamiento claro"
                t = "info"
            flashcard(
                "Estocástico",
                f"{ticker}: %K={k_val:.0f} y %D={d_val:.0f} — {stoc_alert}. La señal más confiable ocurre cuando ambas líneas convergen simultáneamente en una zona extrema.",
                t,
            )

