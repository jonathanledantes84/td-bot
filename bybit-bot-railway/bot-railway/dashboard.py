# -*- coding: utf-8 -*-
"""
DASHBOARD.PY — Panel visual con Streamlit
Ejecutar: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, glob
from datetime import datetime
from pybit.unified_trading import HTTP
import config

# ── CONFIGURACION PAGINA ─────────────────────────────────
st.set_page_config(
    page_title="SuperTrend Bot",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── ESTILOS ──────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: #1e2130;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        border: 1px solid #2d3250;
    }
    .big-number { font-size: 2rem; font-weight: bold; }
    .green { color: #00c853; }
    .red   { color: #ff1744; }
    .gray  { color: #9e9e9e; }
</style>
""", unsafe_allow_html=True)

# ── SESSION BYBIT ────────────────────────────────────────
@st.cache_resource
def get_session():
    return HTTP(
        testnet=config.TESTNET,
        api_key=config.API_KEY,
        api_secret=config.API_SECRET,
    )

session = get_session()

# ── FUNCIONES DE DATOS ───────────────────────────────────
def get_balance():
    try:
        r = session.get_wallet_balance(accountType="UNIFIED", coin="USDT")
        return float(r["result"]["list"][0]["coin"][0]["walletBalance"])
    except Exception:
        return None

def get_precio(symbol):
    try:
        r = session.get_tickers(category="spot", symbol=symbol)
        return float(r["result"]["list"][0]["lastPrice"])
    except Exception:
        return None

def get_ordenes_recientes(symbol, limit=20):
    try:
        r = session.get_order_history(
            category="linear", symbol=symbol, limit=limit
        )
        orders = r["result"]["list"]
        if not orders:
            return pd.DataFrame()
        rows = []
        for o in orders:
            rows.append({
                "Hora":     datetime.fromtimestamp(int(o["createdTime"]) / 1000).strftime("%Y-%m-%d %H:%M"),
                "Par":      o["symbol"],
                "Lado":     o["side"],
                "Cantidad": o["qty"],
                "Precio":   o.get("avgPrice", "—"),
                "Estado":   o["orderStatus"],
            })
        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame()

def get_candles_df(symbol, interval="D", limit=60):
    try:
        result = session.get_kline(
            category="spot", symbol=symbol,
            interval=interval, limit=limit
        )
        candles = sorted(result["result"]["list"], key=lambda x: int(x[0]))
        df = pd.DataFrame(candles, columns=["ts","open","high","low","close","vol","turnover"])
        df["ts"]    = pd.to_datetime(df["ts"].astype(int), unit="ms")
        df["open"]  = df["open"].astype(float)
        df["high"]  = df["high"].astype(float)
        df["low"]   = df["low"].astype(float)
        df["close"] = df["close"].astype(float)
        return df
    except Exception:
        return pd.DataFrame()

def get_logs_hoy():
    try:
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        fname   = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.txt")
        if not os.path.exists(fname):
            return []
        with open(fname, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return [l.strip() for l in lines[-50:]]  # ultimas 50 lineas
    except Exception:
        return []

# ── HEADER ───────────────────────────────────────────────
modo  = "TESTNET" if config.TESTNET else "REAL"
color = "🟡" if config.TESTNET else "🔴"
st.title(f"📈 SuperTrend Bot — {color} {modo}")
st.caption(f"Actualizado: {datetime.now().strftime('%H:%M:%S')} | Auto-refresh cada 60s")

# ── METRICAS PRINCIPALES ─────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

balance = get_balance()
symbol_principal = config.SYMBOLS[0]["symbol"]
precio  = get_precio(symbol_principal)

with col1:
    st.metric("Saldo USDT", f"{balance:.2f}" if balance else "—", delta=None)
with col2:
    st.metric(f"Precio {symbol_principal}", f"{precio:,.2f}" if precio else "—")
with col3:
    pares = ", ".join(s["symbol"] for s in config.SYMBOLS)
    st.metric("Pares activos", pares)
with col4:
    st.metric("Stop Loss", f"{config.STOP_LOSS_PCT}%")

st.divider()

# ── GRAFICO DE VELAS ────────────────────────────────────
st.subheader(f"Grafico {symbol_principal} — Diario")
df = get_candles_df(symbol_principal)

if not df.empty:
    fig = go.Figure(data=[go.Candlestick(
        x=df["ts"],
        open=df["open"], high=df["high"],
        low=df["low"],   close=df["close"],
        increasing_line_color="#00c853",
        decreasing_line_color="#ff1744",
        name=symbol_principal
    )])
    fig.update_layout(
        template="plotly_dark",
        height=400,
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis_rangeslider_visible=False,
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No se pudieron cargar las velas")

st.divider()

# ── ORDENES Y LOGS ───────────────────────────────────────
col_ord, col_log = st.columns([1, 1])

with col_ord:
    st.subheader("Ordenes recientes")
    df_ord = get_ordenes_recientes(symbol_principal)
    if not df_ord.empty:
        def color_lado(val):
            color = "color: #00c853" if val == "Buy" else "color: #ff1744"
            return color
        st.dataframe(
            df_ord.style.applymap(color_lado, subset=["Lado"]),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No hay ordenes recientes")

with col_log:
    st.subheader("Log de hoy")
    logs = get_logs_hoy()
    if logs:
        log_text = "\n".join(reversed(logs))
        st.code(log_text, language=None)
    else:
        st.info("No hay logs todavia — inicia el bot primero")

st.divider()

# ── CONFIGURACION ACTUAL ─────────────────────────────────
with st.expander("Ver configuracion actual"):
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("**Trading**")
        for s in config.SYMBOLS:
            st.write(f"- {s['symbol']}: qty {s['qty']}")
        st.write(f"- Timeframe: Diario")
        st.write(f"- Stop Loss: {config.STOP_LOSS_PCT}%")
        st.write(f"- Limite diario: {config.DAILY_LOSS_LIMIT_PCT}%")
    with col_b:
        st.write("**Sistema**")
        st.write(f"- Horario: {config.TRADING_HOUR_START}h - {config.TRADING_HOUR_END}h")
        st.write(f"- Auto-reinicio: {config.AUTO_RESTART}")
        st.write(f"- Telegram: {'activado' if config.TELEGRAM_TOKEN else 'desactivado'}")
        st.write(f"- Log en archivo: {config.SAVE_LOG}")

# ── AUTO REFRESH ─────────────────────────────────────────
st.markdown("---")
if st.button("Actualizar ahora"):
    st.rerun()

# Auto-refresh cada 60 segundos
st.markdown("""
<script>
setTimeout(function() { window.location.reload(); }, 60000);
</script>
""", unsafe_allow_html=True)
