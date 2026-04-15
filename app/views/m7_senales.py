import streamlit as st
import pandas as pd
from src.analysis.technical import (
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_sma, calculate_stochastic, evaluate_signals,
)
from app.style import COLORS, flashcard, module_header


def render(prices, simple_ret, log_ret):
    module_header(
        "⚡ Señales y Alertas de Trading",
        "Motor de señales automático: consolida RSI, MACD, Bollinger, Golden Cross y Estocástico para el último día hábil.",
    )

    if prices is None or prices.empty:
        st.info("⬅️ Carga el portafolio desde el panel lateral para comenzar.")
        return

    # ── Calibración ───────────────────────────────────────────────────────
    with st.expander("⚙️ Calibrar umbrales", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        rsi_ob  = c1.number_input("RSI Sobrecompra",   50, 100, 70,  key="m7_rsi_ob")
        rsi_os  = c1.number_input("RSI Sobreventa",     0,  50, 30,  key="m7_rsi_os")
        stoc_ob = c2.number_input("Estocástico SC",    50, 100, 80,  key="m7_stoc_ob")
        stoc_os = c2.number_input("Estocástico SV",     0,  50, 20,  key="m7_stoc_os")
        fast_ma = c3.number_input("Media Rápida (d)",   5, 100, 50,  key="m7_fast_ma")
        slow_ma = c4.number_input("Media Lenta (d)",  100, 300, 200, key="m7_slow_ma")

    # ── Cálculo señales ───────────────────────────────────────────────────
    results = []
    for ticker in prices.columns:
        if ticker == "SPY":
            continue
        data = prices[ticker].dropna()
        if len(data) < slow_ma:
            continue

        rsi_val = calculate_rsi(data).iloc[-1]
        _, _, macd_hist = calculate_macd(data)
        hist_val = macd_hist.iloc[-1]
        up, low = calculate_bollinger_bands(data)
        price_val = data.iloc[-1]
        sma_f = calculate_sma(data, fast_ma).iloc[-1]
        sma_s = calculate_sma(data, slow_ma).iloc[-1]
        k, d  = calculate_stochastic(data, data, data)

        signal = evaluate_signals(
            price_val, rsi_val, hist_val, up.iloc[-1], low.iloc[-1],
            sma_f, sma_s, k.iloc[-1], d.iloc[-1],
            rsi_overbought=rsi_ob, rsi_oversold=rsi_os,
            stoch_overbought=stoc_ob, stoch_oversold=stoc_os,
        )

        bb_eval = "🔴 Toca Sup" if price_val > up.iloc[-1] else ("🟢 Toca Inf" if price_val < low.iloc[-1] else "⚪ Medio")
        
        results.append({
            "Activo":     ticker,
            "Precio":     f"${price_val:.2f}",
            "RSI":        round(rsi_val, 1),
            "MACD Hist":  round(hist_val, 4),
            "MA Cross":   "🟢 Golden" if sma_f > sma_s else "🔴 Death",
            "Estocástico":f"K:{k.iloc[-1]:.0f} / D:{d.iloc[-1]:.0f}",
            "Bollinger":  bb_eval,
            "Bollinger_val": (price_val, up.iloc[-1], low.iloc[-1]),
            "Señal":      signal,
        })

    if not results:
        st.warning("Datos insuficientes para calcular medias lentas. Reduce la ventana lenta o amplía el rango de fechas.")
        return

    df = pd.DataFrame(results).set_index("Activo")

    # ── Tablero visual ────────────────────────────────────────────────────
    st.subheader("📋 Tablero de Señales Multi-Indicador")

    def badge(signal: str) -> str:
        if "Fuerte Compra" in signal:
            return f'<span style="background:#064E3B;color:#34D399;padding:3px 10px;border-radius:6px;font-weight:600;font-size:0.78rem;">{signal}</span>'
        if "Comprar" in signal:
            return f'<span style="background:#052E16;color:#6EE7B7;padding:3px 10px;border-radius:6px;font-weight:600;font-size:0.78rem;">{signal}</span>'
        if "Fuerte Venta" in signal:
            return f'<span style="background:#450A0A;color:#FCA5A5;padding:3px 10px;border-radius:6px;font-weight:600;font-size:0.78rem;">{signal}</span>'
        if "Vender" in signal:
            return f'<span style="background:#3B0000;color:#FECACA;padding:3px 10px;border-radius:6px;font-weight:600;font-size:0.78rem;">{signal}</span>'
        return f'<span style="background:#1E2433;color:#94A3B8;padding:3px 10px;border-radius:6px;font-weight:600;font-size:0.78rem;">{signal}</span>'

    # Tabla HTML con badges
    html_rows = ""
    for row in results:
        ticker = row["Activo"]
        html_rows += f"<tr>"
        html_rows += f"<td style='font-weight:600;color:#E2E8F0;padding:8px 12px;'>{ticker}</td>"
        html_rows += f"<td style='color:#94A3B8;padding:8px 12px;'>{row['Precio']}</td>"
        html_rows += f"<td style='color:#94A3B8;padding:8px 12px;'>{row['RSI']}</td>"
        html_rows += f"<td style='color:#94A3B8;padding:8px 12px;'>{row['MACD Hist']}</td>"
        html_rows += f"<td style='color:#94A3B8;padding:8px 12px;'>{row['MA Cross']}</td>"
        html_rows += f"<td style='color:#94A3B8;padding:8px 12px;'>{row['Estocástico']}</td>"
        html_rows += f"<td style='color:#94A3B8;padding:8px 12px;'>{row['Bollinger']}</td>"
        html_rows += f"<td style='padding:8px 12px;'>{badge(row['Señal'])}</td>"
        html_rows += f"</tr>"

    table_html = f"<div style='overflow-x:auto;'><table style='width:100%;border-collapse:collapse;font-size:0.875rem;'><thead><tr style='border-bottom:1px solid rgba(59,130,246,0.2);'>"
    table_html += "<th style='text-align:left;padding:8px 12px;color:#475569;font-weight:600;font-size:0.72rem;uppercase'>Activo</th>"
    table_html += "<th style='text-align:left;padding:8px 12px;color:#475569;font-weight:600;font-size:0.72rem;uppercase'>Precio</th>"
    table_html += "<th style='text-align:left;padding:8px 12px;color:#475569;font-weight:600;font-size:0.72rem;uppercase'>RSI</th>"
    table_html += "<th style='text-align:left;padding:8px 12px;color:#475569;font-weight:600;font-size:0.72rem;uppercase'>MACD</th>"
    table_html += "<th style='text-align:left;padding:8px 12px;color:#475569;font-weight:600;font-size:0.72rem;uppercase'>MA Cross</th>"
    table_html += "<th style='text-align:left;padding:8px 12px;color:#475569;font-weight:600;font-size:0.72rem;uppercase'>Estocástico</th>"
    table_html += "<th style='text-align:left;padding:8px 12px;color:#475569;font-weight:600;font-size:0.72rem;uppercase'>Bollinger</th>"
    table_html += "<th style='text-align:left;padding:8px 12px;color:#475569;font-weight:600;font-size:0.72rem;uppercase'>Señal Final</th>"
    table_html += f"</tr></thead><tbody>{html_rows}</tbody></table></div>"

    st.markdown(table_html, unsafe_allow_html=True)

    # ── Desglose individual ───────────────────────────────────────────────
    st.subheader("🔍 Desglose por Activo")
    for row in results:
        s = row["Señal"]
        s_ma   = "🟢 Golden Cross (alcista)" if "Golden" in row["MA Cross"] else "🔴 Death Cross (bajista)"
        s_rsi  = f"🔴 Sobrecompra ({row['RSI']})" if row["RSI"] > rsi_ob else (f"🟢 Sobreventa ({row['RSI']})" if row["RSI"] < rsi_os else f"⚪ Neutro ({row['RSI']})")
        s_macd = "🟢 Momentum Alcista (+)" if row["MACD Hist"] > 0 else "🔴 Momentum Bajista (-)"
        
        pval, pup, plow = row["Bollinger_val"]
        if pval > pup:
            s_bb = "🔴 Precio tocando/rompiendo Banda Bollinger Superior"
        elif pval < plow:
            s_bb = "🟢 Precio tocando/rompiendo Banda Bollinger Inferior"
        else:
            s_bb = "⚪ Precio fluyendo dentro de Bandas"

        msg = f"**{row['Activo']} · {row['Precio']}** → `{s}`\n- **Tendencia (MA):** {s_ma}\n- **Fuerza Relativa (RSI):** {s_rsi}\n- **Aceleración (MACD):** {s_macd}\n- **Oscilador Estocástico:** {row['Estocástico']}\n- **Volatilidad Extrema (Bollinger):** {s_bb}"

        if "Compra" in s:
            st.success(msg)
        elif "Venta" in s:
            st.error(msg)
        else:
            st.warning(msg)

    if st.session_state.get("show_flashcards"):
        compras = sum(1 for r in results if "Compra" in r["Señal"])
        ventas  = sum(1 for r in results if "Venta"  in r["Señal"])
        flashcard(
            "Motor de señales multi-indicador",
            f"Resumen actual: <b>{compras} señal(es) de compra</b> · <b>{ventas} señal(es) de venta</b> sobre {len(results)} activos. "
            f"Un solo indicador genera cruces falsos frecuentes. Al exigir confluencia de 5 indicadores simultáneos, "
            f"el motor solo activa señal cuando hay consenso técnico real.",
            "success" if compras > ventas else ("danger" if ventas > compras else "info"),
        )
