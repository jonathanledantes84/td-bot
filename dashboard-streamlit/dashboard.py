# -*- coding: utf-8 -*-
"""
DASHBOARD.PY — Panel de control SuperTrend Bot
- Bot automático (SuperTrend)
- Compra/venta manual
- Desplegable en Streamlit Cloud (gratis)
"""

import streamlit as st
import os, time, requests, json
from datetime import datetime
from pybit.unified_trading import HTTP

# ── Configuración ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SuperTrend Bot",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Estilos ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0d0f14;
    color: #e2e8f0;
}
.stApp { background-color: #0d0f14; }

h1, h2, h3 { font-family: 'Space Mono', monospace; }

.metric-card {
    background: #161b26;
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
.metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    margin: 8px 0;
}
.metric-label {
    font-size: 0.75rem;
    color: #718096;
    text-transform: uppercase;
    letter-spacing: 1.5px;
}
.green { color: #48bb78; }
.red   { color: #fc8181; }
.blue  { color: #63b3ed; }
.yellow { color: #f6e05e; }

.trade-row {
    background: #161b26;
    border: 1px solid #2d3748;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 6px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.signal-alcista {
    background: linear-gradient(135deg, #1a2e1a, #1f3d1f);
    border: 1px solid #276749;
    border-radius: 8px;
    padding: 16px;
    text-align: center;
}
.signal-bajista {
    background: linear-gradient(135deg, #2d1515, #3d1f1f);
    border: 1px solid #9b2c2c;
    border-radius: 8px;
    padding: 16px;
    text-align: center;
}
.buy-btn button {
    background: linear-gradient(135deg, #276749, #2f855a) !important;
    color: white !important;
    border: none !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    letter-spacing: 2px !important;
    border-radius: 8px !important;
    width: 100% !important;
    padding: 12px !important;
}
.sell-btn button {
    background: linear-gradient(135deg, #9b2c2c, #c53030) !important;
    color: white !important;
    border: none !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    letter-spacing: 2px !important;
    border-radius: 8px !important;
    width: 100% !important;
    padding: 12px !important;
}
div[data-testid="stAlert"] {
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ── Parámetros SuperTrend ─────────────────────────────────────────────────
ATR_PERIOD     = 10
ATR_MULTIPLIER = 3.0
TIMEFRAME      = "D"

# ── Leer config ───────────────────────────────────────────────────────────
def get_config():
    api_key    = os.environ.get("API_KEY", "")
    api_secret = os.environ.get("API_SECRET", "")
    testnet    = os.environ.get("TESTNET", "true").lower() == "true"
    telegram_token   = os.environ.get("TELEGRAM_TOKEN", "")
    telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    try:
        import config as c
        if not api_key:    api_key    = c.API_KEY
        if not api_secret: api_secret = c.API_SECRET
        testnet = c.TESTNET
        if not telegram_token:   telegram_token   = c.TELEGRAM_TOKEN
        if not telegram_chat_id: telegram_chat_id = c.TELEGRAM_CHAT_ID
    except ImportError:
        pass
    return api_key, api_secret, testnet, telegram_token, telegram_chat_id

API_KEY, API_SECRET, TESTNET, TELE_TOKEN, TELE_CHAT = get_config()

@st.cache_resource
def get_session():
    return HTTP(testnet=TESTNET, api_key=API_KEY, api_secret=API_SECRET)

session = get_session()

# ── Helpers ───────────────────────────────────────────────────────────────
def send_telegram(msg):
    if not TELE_TOKEN or not TELE_CHAT: return
    try:
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",
                      json={"chat_id": TELE_CHAT, "text": msg}, timeout=5)
    except Exception: pass

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

def get_candles(symbol):
    try:
        result = session.get_kline(category="spot", symbol=symbol, interval=TIMEFRAME, limit=120)
        candles = sorted(result["result"]["list"], key=lambda x: int(x[0]))
        return (
            [float(c[1]) for c in candles],  # open
            [float(c[2]) for c in candles],  # high
            [float(c[3]) for c in candles],  # low
            [float(c[4]) for c in candles],  # close
            [int(c[0])   for c in candles],  # timestamps
        )
    except Exception:
        return None, None, None, None, None

def calculate_supertrend(highs, lows, closes):
    trs = [max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1]))
           for i in range(1, len(closes))]
    atr = [sum(trs[:ATR_PERIOD]) / ATR_PERIOD]
    for i in range(ATR_PERIOD, len(trs)):
        atr.append((atr[-1] * (ATR_PERIOD-1) + trs[i]) / ATR_PERIOD)

    upper_band, lower_band, trend = [], [], []
    for i in range(len(atr)):
        idx = i + ATR_PERIOD
        hl2 = (highs[idx] + lows[idx]) / 2
        bu  = hl2 + ATR_MULTIPLIER * atr[i]
        bl  = hl2 - ATR_MULTIPLIER * atr[i]
        if i == 0:
            upper_band.append(bu); lower_band.append(bl)
            trend.append(-1 if closes[idx] <= bu else 1)
        else:
            ub = bu if bu < upper_band[-1] or closes[idx-1] > upper_band[-1] else upper_band[-1]
            lb = bl if bl > lower_band[-1] or closes[idx-1] < lower_band[-1] else lower_band[-1]
            upper_band.append(ub); lower_band.append(lb)
            if   trend[-1]==-1 and closes[idx]>ub: trend.append(1)
            elif trend[-1]==1  and closes[idx]<lb: trend.append(-1)
            else:                                   trend.append(trend[-1])
    return trend, upper_band, lower_band

def place_order(symbol, side, qty, razon="MANUAL"):
    try:
        result = session.place_order(
            category="linear", symbol=symbol, side=side,
            orderType="Market", qty=str(qty), timeInForce="GTC"
        )
        order_id = result["result"]["orderId"]
        precio   = get_precio(symbol) or 0
        modo = "TESTNET" if TESTNET else "REAL"
        send_telegram(f"[{side.upper()}] {razon}\nPar: {symbol}\nPrecio: {precio:.2f}\nCantidad: {qty}\nModo: {modo}")
        return True, order_id, precio
    except Exception as e:
        return False, str(e), 0

def get_open_orders(symbol):
    try:
        r = session.get_open_orders(category="linear", symbol=symbol)
        return r["result"]["list"]
    except Exception:
        return []

def get_positions(symbol):
    try:
        r = session.get_positions(category="linear", symbol=symbol, settleCoin="USDT")
        return [p for p in r["result"]["list"] if float(p.get("size", 0)) > 0]
    except Exception:
        return []

# ── Estado de sesión ──────────────────────────────────────────────────────
if "historial" not in st.session_state:
    st.session_state.historial = []
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now()
if "symbol" not in st.session_state:
    st.session_state.symbol = "BTCUSDT"

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Config")
    modo_txt = "🟡 TESTNET" if TESTNET else "🔴 REAL"
    st.markdown(f"**Modo:** {modo_txt}")
    st.divider()

    symbol = st.selectbox("Par", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"],
                           index=0)
    st.session_state.symbol = symbol

    qty = st.number_input("Cantidad", min_value=0.0001, value=0.001,
                           step=0.001, format="%.4f")

    st.divider()
    st.markdown("### 🔄 Actualizar")
    auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)
    if st.button("🔃 Actualizar ahora", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    st.markdown(f"<small style='color:#718096'>Última actualización:<br>{st.session_state.last_refresh.strftime('%H:%M:%S')}</small>",
                unsafe_allow_html=True)

# ── Título ────────────────────────────────────────────────────────────────
st.markdown(f"""
<h1 style='font-family:Space Mono,monospace; font-size:1.8rem; margin-bottom:0'>
📈 SuperTrend Bot
<span style='font-size:0.9rem; color:#718096; font-weight:400'> — {symbol}</span>
</h1>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Cargar datos ──────────────────────────────────────────────────────────
with st.spinner("Cargando datos..."):
    precio_actual = get_precio(symbol)
    balance       = get_balance()
    opens, highs, lows, closes, timestamps = get_candles(symbol)

# ── Señal SuperTrend ──────────────────────────────────────────────────────
trend_actual = None
trend_prev   = None
supertrend_line = None

if closes and len(closes) > ATR_PERIOD + 5:
    trend, upper_band, lower_band = calculate_supertrend(highs, lows, closes)
    trend_actual = trend[-1]
    trend_prev   = trend[-2]
    supertrend_line = lower_band[-1] if trend_actual == 1 else upper_band[-1]

# ── Métricas principales ──────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    precio_fmt = f"${precio_actual:,.2f}" if precio_actual else "—"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Precio {symbol[:3]}</div>
        <div class="metric-value blue">{precio_fmt}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    balance_fmt = f"${balance:,.2f}" if balance else "—"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Saldo USDT</div>
        <div class="metric-value">{balance_fmt}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    if trend_actual is not None:
        color  = "green" if trend_actual == 1 else "red"
        estado = "▲ ALCISTA" if trend_actual == 1 else "▼ BAJISTA"
    else:
        color, estado = "yellow", "— SIN DATOS"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Tendencia</div>
        <div class="metric-value {color}">{estado}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st_fmt = f"${supertrend_line:,.2f}" if supertrend_line else "—"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">SuperTrend</div>
        <div class="metric-value yellow">{st_fmt}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Señal del bot ─────────────────────────────────────────────────────────
if trend_actual is not None and trend_prev is not None:
    cambio = trend_prev != trend_actual
    if cambio and trend_actual == 1:
        st.success("🚀 **SEÑAL BOT: COMPRAR** — El SuperTrend acaba de cambiar a ALCISTA")
    elif cambio and trend_actual == -1:
        st.error("🔻 **SEÑAL BOT: VENDER** — El SuperTrend acaba de cambiar a BAJISTA")
    elif trend_actual == 1:
        st.info("✅ Tendencia ALCISTA activa — el bot mantiene posición larga")
    else:
        st.warning("⏸️ Tendencia BAJISTA activa — el bot no compra")

st.markdown("---")

# ── Gráfico de velas ──────────────────────────────────────────────────────
st.markdown("### 📊 Gráfico")

if closes and len(closes) > 20:
    import plotly.graph_objects as go

    n = min(60, len(closes))
    ts  = [datetime.fromtimestamp(t/1000) for t in timestamps[-n:]]
    op  = opens[-n:]
    hi  = highs[-n:]
    lo  = lows[-n:]
    cl  = closes[-n:]

    # SuperTrend line para el gráfico
    st_values = []
    if len(trend) >= n:
        for i in range(n):
            idx = len(trend) - n + i
            if trend[idx] == 1:
                st_values.append(lower_band[idx])
            else:
                st_values.append(upper_band[idx])

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=ts, open=op, high=hi, low=lo, close=cl,
        name=symbol,
        increasing_line_color="#48bb78",
        decreasing_line_color="#fc8181",
        increasing_fillcolor="#48bb78",
        decreasing_fillcolor="#fc8181",
    ))

    if st_values:
        # Color de la línea SuperTrend según tendencia
        colors_st = []
        for i in range(n):
            idx = len(trend) - n + i
            colors_st.append("#48bb78" if trend[idx] == 1 else "#fc8181")

        for i in range(len(st_values) - 1):
            fig.add_trace(go.Scatter(
                x=[ts[i], ts[i+1]],
                y=[st_values[i], st_values[i+1]],
                mode="lines",
                line=dict(color=colors_st[i], width=2),
                showlegend=False,
                hoverinfo="skip"
            ))

    fig.update_layout(
        paper_bgcolor="#0d0f14",
        plot_bgcolor="#0d0f14",
        font=dict(color="#e2e8f0", family="DM Sans"),
        xaxis=dict(gridcolor="#1a202c", showgrid=True),
        yaxis=dict(gridcolor="#1a202c", showgrid=True),
        margin=dict(l=0, r=0, t=20, b=0),
        height=380,
        xaxis_rangeslider_visible=False,
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Sin datos suficientes para el gráfico")

st.markdown("---")

# ── Panel de trading manual ───────────────────────────────────────────────
st.markdown("### 🎯 Trading Manual")

col_buy, col_sell = st.columns(2)

with col_buy:
    st.markdown('<div class="buy-btn">', unsafe_allow_html=True)
    if st.button(f"▲  COMPRAR  {symbol}", key="btn_buy", use_container_width=True):
        ok, result, precio_op = place_order(symbol, "Buy", qty, "MANUAL BUY")
        if ok:
            st.success(f"✅ Orden de COMPRA enviada — ID: {result} @ ${precio_op:,.2f}")
            st.session_state.historial.append({
                "hora": datetime.now().strftime("%H:%M:%S"),
                "tipo": "BUY",
                "symbol": symbol,
                "qty": qty,
                "precio": precio_op,
                "id": result
            })
        else:
            st.error(f"❌ Error: {result}")
    st.markdown('</div>', unsafe_allow_html=True)

with col_sell:
    st.markdown('<div class="sell-btn">', unsafe_allow_html=True)
    if st.button(f"▼  VENDER  {symbol}", key="btn_sell", use_container_width=True):
        ok, result, precio_op = place_order(symbol, "Sell", qty, "MANUAL SELL")
        if ok:
            st.success(f"✅ Orden de VENTA enviada — ID: {result} @ ${precio_op:,.2f}")
            st.session_state.historial.append({
                "hora": datetime.now().strftime("%H:%M:%S"),
                "tipo": "SELL",
                "symbol": symbol,
                "qty": qty,
                "precio": precio_op,
                "id": result
            })
        else:
            st.error(f"❌ Error: {result}")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Posiciones abiertas ───────────────────────────────────────────────────
st.markdown("### 📂 Posiciones Abiertas")

positions = get_positions(symbol)
if positions:
    for pos in positions:
        side_pos = pos.get("side", "")
        size_pos = pos.get("size", "0")
        entry    = float(pos.get("avgPrice", 0))
        upnl     = float(pos.get("unrealisedPnl", 0))
        pnl_color = "green" if upnl >= 0 else "red"
        pnl_sign  = "+" if upnl >= 0 else ""
        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("Par", symbol)
        col_b.metric("Lado", side_pos)
        col_c.metric("Entrada", f"${entry:,.2f}")
        col_d.metric("P&L no realizado", f"{pnl_sign}${upnl:.2f}")
else:
    st.markdown("<small style='color:#718096'>Sin posiciones abiertas en este par</small>",
                unsafe_allow_html=True)

st.markdown("---")

# ── Historial de esta sesión ───────────────────────────────────────────────
st.markdown("### 🕒 Órdenes de esta sesión")

if st.session_state.historial:
    for op in reversed(st.session_state.historial):
        color = "#48bb78" if op["tipo"] == "BUY" else "#fc8181"
        st.markdown(f"""
        <div class="trade-row">
            <span style="color:{color}; font-family:'Space Mono',monospace; font-weight:700">{op['tipo']}</span>
            <span>{op['symbol']}</span>
            <span>{op['qty']}</span>
            <span>${op['precio']:,.2f}</span>
            <span style="color:#718096">{op['hora']}</span>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("<small style='color:#718096'>Sin operaciones en esta sesión</small>",
                unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
modo_label = "TESTNET (práctica)" if TESTNET else "⚠️ DINERO REAL"
st.markdown(f"<center><small style='color:#4a5568'>SuperTrend Bot · Modo: {modo_label} · {datetime.now().strftime('%Y-%m-%d %H:%M')}</small></center>",
            unsafe_allow_html=True)

# ── Auto-refresh ──────────────────────────────────────────────────────────
if auto_refresh:
    st.session_state.last_refresh = datetime.now()
    time.sleep(30)
    st.rerun()
