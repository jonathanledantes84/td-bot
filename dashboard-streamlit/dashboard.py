# -*- coding: utf-8 -*-
import streamlit as st
import os, time, requests
from datetime import datetime
from pybit.unified_trading import HTTP

st.set_page_config(page_title="SuperTrend Bot", page_icon="⚡", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"], .stApp {
    background: #090b0f !important;
    color: #c8d6e8 !important;
    font-family: 'Space Mono', monospace !important;
}
.stApp { background: #090b0f !important; }
.stApp::before {
    content: '';
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background: repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,255,136,0.012) 2px,rgba(0,255,136,0.012) 4px);
}
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton, div[data-testid="stToolbar"], div[data-testid="stDecoration"], div[data-testid="stStatusWidget"] { display: none; }
.block-container { padding: 28px 32px !important; max-width: 100% !important; }

[data-testid="stSidebar"] { background: #0f1318 !important; border-right: 1px solid #1c2330 !important; }
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
    color: #c8d6e8 !important; font-family: 'Space Mono', monospace !important; font-size: 11px !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stNumberInput input {
    background: #0f1318 !important; border: 1px solid #1c2330 !important;
    color: #c8d6e8 !important; font-family: 'Space Mono', monospace !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: #0f1318 !important; border: 1px solid #1c2330 !important;
    color: #5c6b80 !important; font-family: 'Space Mono', monospace !important;
    font-size: 10px !important; letter-spacing: 1px !important;
    text-transform: uppercase !important; border-radius: 6px !important;
}
[data-testid="stSidebar"] .stButton > button:hover { border-color: #00ff88 !important; color: #00ff88 !important; }

.kpi-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin-bottom: 20px; }
.kpi {
    background: #0f1318; border: 1px solid #1c2330; border-radius: 12px;
    padding: 20px; position: relative; overflow: hidden; transition: all .25s;
}
.kpi:hover { border-color: #3a4455; transform: translateY(-1px); box-shadow: 0 4px 20px rgba(0,0,0,.3); }
.kpi::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }
.kpi.g::before { background: #00ff88; } .kpi.b::before { background: #4d9fff; }
.kpi.y::before { background: #ffd23f; } .kpi.r::before { background: #ff3d5a; }
.kpi-label { font-size: 10px; letter-spacing: 1.5px; text-transform: uppercase; color: #5c6b80; margin-bottom: 10px; }
.kpi-val { font-family: 'Syne',sans-serif; font-weight: 800; font-size: 26px; color: #fff; line-height: 1; }
.kpi-val.green{color:#00ff88} .kpi-val.red{color:#ff3d5a} .kpi-val.blue{color:#4d9fff} .kpi-val.yellow{color:#ffd23f}
.kpi-sub { font-size: 11px; color: #5c6b80; margin-top: 6px; }

.status-pill { display:inline-flex; align-items:center; gap:8px; padding:5px 14px; border-radius:100px;
    font-size:11px; font-weight:700; letter-spacing:1px; text-transform:uppercase; }
.status-pill.online  { background:rgba(0,255,136,.08); border:1px solid rgba(0,255,136,.3); color:#00ff88; }
.status-pill.offline { background:rgba(255,61,90,.08);  border:1px solid rgba(255,61,90,.3);  color:#ff3d5a; }
.status-pill.testnet { background:rgba(255,210,63,.08); border:1px solid rgba(255,210,63,.3); color:#ffd23f; }
.dot { width:6px; height:6px; border-radius:50%; background:currentColor; display:inline-block; animation:pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }

.app-header { display:flex; align-items:center; justify-content:space-between;
    margin-bottom:28px; padding-bottom:16px; border-bottom:1px solid #1c2330; }
.logo-wrap { display:flex; align-items:center; gap:12px; }
.logo-icon { width:36px; height:36px; background:#00ff88; border-radius:8px;
    display:flex; align-items:center; justify-content:center; font-size:18px; color:#090b0f; }
.logo-text { font-family:'Syne',sans-serif; font-weight:800; font-size:20px; color:#fff; letter-spacing:-.5px; }
.logo-text span { color:#00ff88; }

.panel { background:#0f1318; border:1px solid #1c2330; border-radius:12px; overflow:hidden; margin-bottom:16px; }
.panel-header { display:flex; align-items:center; justify-content:space-between;
    padding:12px 20px; border-bottom:1px solid #1c2330; background:#141920; }
.panel-title { font-size:10px; letter-spacing:1.5px; text-transform:uppercase; color:#5c6b80; font-weight:700; }

.trend-box { padding:28px 20px; text-align:center; }
.trend-label { font-size:10px; letter-spacing:2px; text-transform:uppercase; color:#5c6b80; margin-bottom:16px; }
.trend-arrow { font-size:48px; line-height:1; margin-bottom:8px; display:block; }
.trend-val { font-family:'Syne',sans-serif; font-weight:800; font-size:36px; letter-spacing:-1px; }
.trend-val.bull{color:#00ff88} .trend-val.bear{color:#ff3d5a} .trend-val.wait{color:#5c6b80}

.ci { display:flex; justify-content:space-between; align-items:center;
    padding:10px 20px; border-bottom:1px solid #1c2330; font-size:12px; }
.ci:last-child { border-bottom:none; }
.ck { color:#5c6b80; } .cv { color:#c8d6e8; font-weight:700; }

.order-row { display:flex; align-items:center; gap:0; padding:10px 20px;
    border-bottom:1px solid #141920; font-size:12px; transition:background .15s; }
.order-row:hover { background:rgba(255,255,255,.02); }
.order-row:last-child { border-bottom:none; }
.ot{min-width:80px;color:#5c6b80} .os{min-width:60px}
.os.buy{color:#00ff88;font-weight:700} .os.sell{color:#ff3d5a;font-weight:700}
.osy{min-width:90px;color:#c8d6e8} .oq{min-width:70px;color:#c8d6e8} .op{flex:1;color:#4d9fff}

.buy-btn .stButton > button {
    background: rgba(0,255,136,.08) !important; border: 1px solid rgba(0,255,136,.35) !important;
    color: #00ff88 !important; font-family: 'Space Mono',monospace !important;
    font-weight: 700 !important; font-size: 13px !important; letter-spacing: 2px !important;
    text-transform: uppercase !important; border-radius: 8px !important;
    height: 56px !important; width: 100% !important; transition: all .2s !important;
}
.buy-btn .stButton > button:hover { background: rgba(0,255,136,.15) !important; box-shadow: 0 0 20px rgba(0,255,136,.15) !important; }
.sell-btn .stButton > button {
    background: rgba(255,61,90,.08) !important; border: 1px solid rgba(255,61,90,.35) !important;
    color: #ff3d5a !important; font-family: 'Space Mono',monospace !important;
    font-weight: 700 !important; font-size: 13px !important; letter-spacing: 2px !important;
    text-transform: uppercase !important; border-radius: 8px !important;
    height: 56px !important; width: 100% !important; transition: all .2s !important;
}
.sell-btn .stButton > button:hover { background: rgba(255,61,90,.15) !important; box-shadow: 0 0 20px rgba(255,61,90,.15) !important; }

@media (max-width:768px) { .kpi-grid { grid-template-columns: repeat(2,1fr); } }
</style>
""", unsafe_allow_html=True)

# ── Config ────────────────────────────────────────────────────────────────
def get_config():
    ak = ask = tt = tc = ""
    tn = True
    try:
        import config as c
        ak, ask, tn = c.API_KEY, c.API_SECRET, c.TESTNET
        tt = getattr(c,"TELEGRAM_TOKEN",""); tc = getattr(c,"TELEGRAM_CHAT_ID","")
    except ImportError: pass
    return (os.environ.get("API_KEY",ak), os.environ.get("API_SECRET",ask),
            os.environ.get("TESTNET",str(tn)).lower()!="false",
            os.environ.get("TELEGRAM_TOKEN",tt), os.environ.get("TELEGRAM_CHAT_ID",tc))

API_KEY, API_SECRET, TESTNET, TELE_TOKEN, TELE_CHAT = get_config()
ATR_PERIOD, ATR_MULTIPLIER = 10, 3.0

@st.cache_resource
def get_session():
    return HTTP(testnet=TESTNET, api_key=API_KEY, api_secret=API_SECRET)
try:
    session = get_session()
    connected = bool(API_KEY and API_SECRET)
except Exception:
    session = None; connected = False

def send_tg(msg):
    if TELE_TOKEN and TELE_CHAT:
        try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",
                           json={"chat_id":TELE_CHAT,"text":msg},timeout=5)
        except: pass

def get_balance():
    try: return float(session.get_wallet_balance(accountType="UNIFIED",coin="USDT")["result"]["list"][0]["coin"][0]["walletBalance"])
    except: return None

def get_precio(symbol):
    try: return float(session.get_tickers(category="spot",symbol=symbol)["result"]["list"][0]["lastPrice"])
    except: return None

def get_candles(symbol):
    try:
        c = sorted(session.get_kline(category="spot",symbol=symbol,interval="D",limit=120)["result"]["list"],key=lambda x:int(x[0]))
        return [float(x[1]) for x in c],[float(x[2]) for x in c],[float(x[3]) for x in c],[float(x[4]) for x in c],[int(x[0]) for x in c]
    except: return None,None,None,None,None

def calc_st(highs,lows,closes):
    trs=[max(highs[i]-lows[i],abs(highs[i]-closes[i-1]),abs(lows[i]-closes[i-1])) for i in range(1,len(closes))]
    atr=[sum(trs[:ATR_PERIOD])/ATR_PERIOD]
    for i in range(ATR_PERIOD,len(trs)): atr.append((atr[-1]*(ATR_PERIOD-1)+trs[i])/ATR_PERIOD)
    ub,lb,tr=[],[],[]
    for i in range(len(atr)):
        idx=i+ATR_PERIOD; hl2=(highs[idx]+lows[idx])/2
        bu=hl2+ATR_MULTIPLIER*atr[i]; bl=hl2-ATR_MULTIPLIER*atr[i]
        if i==0: ub.append(bu);lb.append(bl);tr.append(-1 if closes[idx]<=bu else 1)
        else:
            u=bu if bu<ub[-1] or closes[idx-1]>ub[-1] else ub[-1]
            l=bl if bl>lb[-1] or closes[idx-1]<lb[-1] else lb[-1]
            ub.append(u);lb.append(l)
            if   tr[-1]==-1 and closes[idx]>u: tr.append(1)
            elif tr[-1]==1  and closes[idx]<l: tr.append(-1)
            else: tr.append(tr[-1])
    return tr,ub,lb

def place_order(symbol,side,qty,razon="MANUAL"):
    try:
        r=session.place_order(category="linear",symbol=symbol,side=side,orderType="Market",qty=str(qty),timeInForce="GTC")
        oid=r["result"]["orderId"]; precio=get_precio(symbol) or 0
        send_tg(f"[{side.upper()}] {razon}\nPar: {symbol}\nPrecio: {precio:.2f}\nCantidad: {qty}")
        return True,oid,precio
    except Exception as e: return False,str(e),0

def get_positions(symbol):
    try: return [p for p in session.get_positions(category="linear",symbol=symbol,settleCoin="USDT")["result"]["list"] if float(p.get("size",0))>0]
    except: return []

if "historial" not in st.session_state: st.session_state.historial=[]

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='margin-bottom:8px;font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#5c6b80'>⚙ CONFIG</div>", unsafe_allow_html=True)
    symbol = st.selectbox("Par", ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT"], label_visibility="collapsed")
    qty    = st.number_input("Cant", min_value=0.0001, value=0.001, step=0.001, format="%.4f", label_visibility="collapsed")
    st.markdown("<div style='font-size:10px;color:#5c6b80;margin-top:4px'>Símbolo  ·  Cantidad</div>", unsafe_allow_html=True)
    st.divider()
    if st.button("↻  ACTUALIZAR", use_container_width=True): st.cache_data.clear(); st.rerun()
    auto = st.checkbox("Auto-refresh 30s", value=False)
    st.divider()
    st.markdown(f"<div style='font-size:10px;color:#3a4455;font-family:Space Mono'>{datetime.now().strftime('%Y-%m-%d')}<br>{datetime.now().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────
with st.spinner(""):
    precio  = get_precio(symbol)  if connected else None
    balance = get_balance()       if connected else None
    opens,highs,lows,closes,timestamps = get_candles(symbol) if connected else (None,None,None,None,None)

trend_cur=trend_prev=st_line=trend=ub=lb=None
if closes and len(closes)>ATR_PERIOD+5:
    trend,ub,lb = calc_st(highs,lows,closes)
    trend_cur=trend[-1]; trend_prev=trend[-2]
    st_line = lb[-1] if trend_cur==1 else ub[-1]

# ── Header ────────────────────────────────────────────────────────────────
mc = "testnet" if TESTNET else "offline"
mt = "TESTNET" if TESTNET else "⚠ DINERO REAL"
cc = "online" if connected else "offline"
ct = "Conectado" if connected else "Sin API Keys"

st.markdown(f"""
<div class="app-header">
  <div class="logo-wrap">
    <div class="logo-icon">⚡</div>
    <div class="logo-text">Super<span>Trend</span> Bot</div>
  </div>
  <div style="display:flex;gap:10px;align-items:center">
    <div class="status-pill {mc}"><span class="dot"></span> {mt}</div>
    <div class="status-pill {cc}"><span class="dot"></span> {ct}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────
last_op = st.session_state.historial[-1] if st.session_state.historial else None
st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi g">
    <div class="kpi-label">Saldo USDT</div>
    <div class="kpi-val">{"%.2f"%balance if balance else "—"}</div>
    <div class="kpi-sub">Cuenta unificada</div>
  </div>
  <div class="kpi b">
    <div class="kpi-label">Precio {symbol[:3]}</div>
    <div class="kpi-val blue">{"$%s"%f"{precio:,.2f}" if precio else "—"}</div>
    <div class="kpi-sub">{symbol}</div>
  </div>
  <div class="kpi y">
    <div class="kpi-label">Órdenes sesión</div>
    <div class="kpi-val">{len(st.session_state.historial)}</div>
    <div class="kpi-sub">ejecutadas hoy</div>
  </div>
  <div class="kpi r">
    <div class="kpi-label">Última orden</div>
    <div class="kpi-val {'green' if last_op and last_op['t']=='BUY' else 'red' if last_op else ''}" style="font-size:{'20px' if last_op else '26px'}">{last_op["t"] if last_op else "—"}</div>
    <div class="kpi-sub">{last_op["h"] if last_op else "—"}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Layout ────────────────────────────────────────────────────────────────
col_main, col_right = st.columns([2.2, 1])

with col_main:
    # Chart
    st.markdown('<div class="panel"><div class="panel-header"><span class="panel-title">Gráfico · Diario · SuperTrend</span></div>', unsafe_allow_html=True)
    if closes and len(closes)>20:
        import plotly.graph_objects as go
        n = min(60,len(closes))
        ts = [datetime.fromtimestamp(t/1000) for t in timestamps[-n:]]
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=ts,open=opens[-n:],high=highs[-n:],low=lows[-n:],close=closes[-n:],
            increasing=dict(line=dict(color="#00ff88",width=1),fillcolor="rgba(0,255,136,.12)"),
            decreasing=dict(line=dict(color="#ff3d5a",width=1),fillcolor="rgba(255,61,90,.12)"),name=symbol))
        if trend and len(trend)>=n:
            for i in range(n-1):
                idx=len(trend)-n+i; col="#00ff88" if trend[idx]==1 else "#ff3d5a"
                v=lb[idx] if trend[idx]==1 else ub[idx]; v2=lb[idx+1] if trend[idx+1]==1 else ub[idx+1]
                fig.add_trace(go.Scatter(x=[ts[i],ts[i+1]],y=[v,v2],mode="lines",
                    line=dict(color=col,width=2),showlegend=False,hoverinfo="skip"))
        fig.update_layout(paper_bgcolor="#0f1318",plot_bgcolor="#090b0f",
            font=dict(color="#5c6b80",family="Space Mono",size=10),
            xaxis=dict(gridcolor="#141920",linecolor="#1c2330",showgrid=True,zeroline=False),
            yaxis=dict(gridcolor="#141920",linecolor="#1c2330",showgrid=True,zeroline=False,side="right"),
            margin=dict(l=0,r=60,t=16,b=0),height=340,xaxis_rangeslider_visible=False,
            showlegend=False,hovermode="x unified")
        st.plotly_chart(fig,use_container_width=True)
    else:
        st.markdown("<div style='padding:40px;text-align:center;color:#3a4455;font-size:12px'>Sin datos — configurar API keys en Secrets</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Trade buttons
    st.markdown(f'<div class="panel"><div class="panel-header"><span class="panel-title">Trading Manual</span><span style="font-size:11px;color:#5c6b80">Qty: {qty}</span></div><div style="padding:16px">', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="buy-btn">', unsafe_allow_html=True)
        if st.button(f"▲  COMPRAR  {symbol[:3]}", key="buy", use_container_width=True):
            if not connected: st.error("Configurá las API keys en Secrets")
            else:
                ok,res,p = place_order(symbol,"Buy",qty)
                if ok:
                    st.success(f"✓ Compra @ ${p:,.2f}  ·  ID: {res}")
                    st.session_state.historial.append({"t":"BUY","s":symbol,"q":qty,"p":p,"h":datetime.now().strftime("%H:%M:%S")})
                else: st.error(f"✗ {res}")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="sell-btn">', unsafe_allow_html=True)
        if st.button(f"▼  VENDER  {symbol[:3]}", key="sell", use_container_width=True):
            if not connected: st.error("Configurá las API keys en Secrets")
            else:
                ok,res,p = place_order(symbol,"Sell",qty)
                if ok:
                    st.success(f"✓ Venta @ ${p:,.2f}  ·  ID: {res}")
                    st.session_state.historial.append({"t":"SELL","s":symbol,"q":qty,"p":p,"h":datetime.now().strftime("%H:%M:%S")})
                else: st.error(f"✗ {res}")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    # History
    cnt = len(st.session_state.historial)
    st.markdown(f'<div class="panel"><div class="panel-header"><span class="panel-title">Historial · Esta sesión</span><span style="font-size:11px;color:#5c6b80">{cnt} órdenes</span></div>', unsafe_allow_html=True)
    if st.session_state.historial:
        rows="".join([f'<div class="order-row"><span class="ot">{op["h"]}</span><span class="os {"buy" if op["t"]=="BUY" else "sell"}">{op["t"]}</span><span class="osy">{op["s"]}</span><span class="oq">{op["q"]}</span><span class="op">${op["p"]:,.2f}</span></div>' for op in reversed(st.session_state.historial)])
        st.markdown(rows, unsafe_allow_html=True)
    else:
        st.markdown('<div style="padding:32px;text-align:center;color:#3a4455;font-size:12px">Sin órdenes en esta sesión</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    # Trend
    if trend_cur==1:   t_arr,t_txt,t_cls="↑","ALCISTA","bull"
    elif trend_cur==-1:t_arr,t_txt,t_cls="↓","BAJISTA","bear"
    else:              t_arr,t_txt,t_cls="—","ESPERANDO","wait"
    cambio = (trend_prev is not None and trend_cur != trend_prev)
    if cambio and trend_cur==1:   c_html='<span style="color:#00ff88;font-size:11px">▲ Señal COMPRA activa</span>'
    elif cambio and trend_cur==-1:c_html='<span style="color:#ff3d5a;font-size:11px">▼ Señal VENTA activa</span>'
    else: c_html='<span style="color:#3a4455;font-size:11px">Sin cambio en este cierre</span>'

    st.markdown(f"""
    <div class="panel">
      <div class="panel-header"><span class="panel-title">Tendencia actual</span></div>
      <div class="trend-box">
        <div class="trend-label">SuperTrend Signal</div>
        <span class="trend-arrow">{t_arr}</span>
        <div class="trend-val {t_cls}">{t_txt}</div>
        <div style="margin-top:12px">{c_html}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Positions
    st.markdown('<div class="panel"><div class="panel-header"><span class="panel-title">Posición abierta</span></div>', unsafe_allow_html=True)
    positions = get_positions(symbol) if connected else []
    if positions:
        for pos in positions:
            upnl=float(pos.get("unrealisedPnl",0)); entry=float(pos.get("avgPrice",0))
            sp=pos.get("side",""); col_p="#00ff88" if upnl>=0 else "#ff3d5a"; sgn="+" if upnl>=0 else ""
            st.markdown(f"""
            <div class="ci"><span class="ck">Lado</span><span class="cv" style="color:{'#00ff88' if sp=='Buy' else '#ff3d5a'}">{sp}</span></div>
            <div class="ci"><span class="ck">Tamaño</span><span class="cv">{pos.get("size","")}</span></div>
            <div class="ci"><span class="ck">Entrada</span><span class="cv">${entry:,.2f}</span></div>
            <div class="ci"><span class="ck">P&L</span><span class="cv" style="color:{col_p}">{sgn}${upnl:.2f}</span></div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div style="padding:24px;text-align:center;color:#3a4455;font-size:12px">Sin posición abierta</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Config panel
    st_fmt=f"${st_line:,.2f}" if st_line else "—"
    st.markdown(f"""
    <div class="panel">
      <div class="panel-header"><span class="panel-title">Configuración</span></div>
      <div class="ci"><span class="ck">Symbol</span><span class="cv">{symbol}</span></div>
      <div class="ci"><span class="ck">Cantidad</span><span class="cv">{qty}</span></div>
      <div class="ci"><span class="ck">Modo</span><span class="cv">{"TESTNET" if TESTNET else "REAL"}</span></div>
      <div class="ci"><span class="ck">Estrategia</span><span class="cv">SuperTrend</span></div>
      <div class="ci"><span class="ck">SuperTrend</span><span class="cv">{st_fmt}</span></div>
      <div class="ci"><span class="ck">ATR Period</span><span class="cv">{ATR_PERIOD}</span></div>
    </div>
    """, unsafe_allow_html=True)

if auto:
    time.sleep(30)
    st.rerun()
