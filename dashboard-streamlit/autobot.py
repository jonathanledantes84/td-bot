# -*- coding: utf-8 -*-
"""
AUTOBOT.PY - SuperTrend Bot para Bybit
Soporta --once para GitHub Actions (una pasada y termina)
Lee API keys desde variables de entorno si existen
"""

import time, os, sys, requests, threading
from datetime import datetime
from pybit.unified_trading import HTTP

# ── Modo: una pasada (GitHub Actions) o loop infinito (local) ──────────────
ONCE_MODE = "--once" in sys.argv

# ── Config: variables de entorno tienen prioridad sobre config.py ──────────
try:
    import config as _cfg
    _API_KEY    = os.environ.get("API_KEY")    or _cfg.API_KEY
    _API_SECRET = os.environ.get("API_SECRET") or _cfg.API_SECRET
    _TESTNET    = _cfg.TESTNET
    _SYMBOLS    = _cfg.SYMBOLS
    _STOP_LOSS_PCT        = _cfg.STOP_LOSS_PCT
    _DAILY_LOSS_LIMIT_PCT = _cfg.DAILY_LOSS_LIMIT_PCT
    _TRADING_HOUR_START   = _cfg.TRADING_HOUR_START
    _TRADING_HOUR_END     = _cfg.TRADING_HOUR_END
    _AUTO_RESTART         = _cfg.AUTO_RESTART
    _AUTO_RESTART_DELAY   = _cfg.AUTO_RESTART_DELAY
    _SAVE_LOG             = _cfg.SAVE_LOG
    _TELEGRAM_TOKEN    = os.environ.get("TELEGRAM_TOKEN")    or _cfg.TELEGRAM_TOKEN
    _TELEGRAM_CHAT_ID  = os.environ.get("TELEGRAM_CHAT_ID") or _cfg.TELEGRAM_CHAT_ID
except ImportError:
    # Sin config.py: solo variables de entorno (modo GitHub Actions puro)
    _API_KEY    = os.environ.get("API_KEY", "")
    _API_SECRET = os.environ.get("API_SECRET", "")
    _TESTNET    = os.environ.get("TESTNET", "true").lower() == "true"
    _SYMBOLS    = [{"symbol": os.environ.get("SYMBOL", "BTCUSDT"),
                    "qty":    os.environ.get("QTY", "0.001")}]
    _STOP_LOSS_PCT        = float(os.environ.get("STOP_LOSS_PCT", "2.0"))
    _DAILY_LOSS_LIMIT_PCT = float(os.environ.get("DAILY_LOSS_LIMIT_PCT", "5.0"))
    _TRADING_HOUR_START   = int(os.environ.get("TRADING_HOUR_START", "9"))
    _TRADING_HOUR_END     = int(os.environ.get("TRADING_HOUR_END", "22"))
    _AUTO_RESTART         = False
    _AUTO_RESTART_DELAY   = 30
    _SAVE_LOG             = False
    _TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_TOKEN", "")
    _TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

ATR_PERIOD     = 10
ATR_MULTIPLIER = 3.0
TIMEFRAME      = "D"
CHECK_INTERVAL = 3600

session = HTTP(testnet=_TESTNET, api_key=_API_KEY, api_secret=_API_SECRET)

state = {
    "posiciones": {}, "ordenes_hoy": 0,
    "saldo_inicio_dia": None, "dia_actual": None, "detenido": False,
}
state_lock = threading.Lock()

def _log_dir():
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(d, exist_ok=True)
    return d

def log(msg, level="INFO"):
    linea = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{level}] {msg}"
    print(linea, flush=True)
    if _SAVE_LOG:
        try:
            fname = os.path.join(_log_dir(), f"{datetime.now().strftime('%Y-%m-%d')}.txt")
            with open(fname, "a", encoding="utf-8") as f:
                f.write(linea + "\n")
        except Exception:
            pass

def telegram(msg):
    if not _TELEGRAM_TOKEN or not _TELEGRAM_CHAT_ID:
        return
    try:
        requests.post(f"https://api.telegram.org/bot{_TELEGRAM_TOKEN}/sendMessage",
                      json={"chat_id": _TELEGRAM_CHAT_ID, "text": msg}, timeout=5)
    except Exception as e:
        log(f"Telegram error: {e}", "WARN")

def dentro_de_horario():
    return _TRADING_HOUR_START <= datetime.now().hour < _TRADING_HOUR_END

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
        result = session.get_kline(category="spot", symbol=symbol, interval=TIMEFRAME, limit=100)
        candles = sorted(result["result"]["list"], key=lambda x: int(x[0]))
        return ([float(c[2]) for c in candles],
                [float(c[3]) for c in candles],
                [float(c[4]) for c in candles])
    except Exception as e:
        log(f"[{symbol}] Error velas: {e}", "ERROR")
        return None, None, None

def calculate_atr(highs, lows, closes, period):
    trs = [max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1]))
           for i in range(1, len(closes))]
    atr = [sum(trs[:period]) / period]
    for i in range(period, len(trs)):
        atr.append((atr[-1] * (period-1) + trs[i]) / period)
    return atr

def calculate_supertrend(highs, lows, closes):
    atr = calculate_atr(highs, lows, closes, ATR_PERIOD)
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
    return trend

def place_order(symbol, side, qty, razon="SENAL"):
    try:
        result = session.place_order(category="linear", symbol=symbol, side=side,
                                     orderType="Market", qty=str(qty), timeInForce="GTC")
        order_id = result["result"]["orderId"]
        precio   = get_precio(symbol) or 0
        log(f"[{symbol}] {razon} | {side} {qty} @ {precio:.2f} | ID: {order_id}", "TRADE")
        with state_lock:
            state["ordenes_hoy"] += 1
            if razon != "STOP LOSS":
                state["posiciones"][symbol] = {"side": side, "precio_entrada": precio, "qty": qty}
            else:
                state["posiciones"].pop(symbol, None)
        modo = "TESTNET" if _TESTNET else "REAL"
        telegram(f"[{side.upper()}] {razon}\nPar: {symbol}\nPrecio: {precio:.2f}\nCantidad: {qty}\nModo: {modo}")
        return True
    except Exception as e:
        log(f"[{symbol}] Orden fallida: {e}", "ERROR")
        telegram(f"ERROR orden {side} {symbol}:\n{e}")
        return False

def check_stop_loss(symbol):
    pos = state["posiciones"].get(symbol)
    if not pos or _STOP_LOSS_PCT <= 0: return False
    precio = get_precio(symbol)
    if not precio: return False
    entrada = pos["precio_entrada"]
    pct = (entrada-precio)/entrada*100 if pos["side"]=="Buy" else (precio-entrada)/entrada*100
    if pct >= _STOP_LOSS_PCT:
        log(f"[{symbol}] STOP LOSS! Perdida: {pct:.2f}%", "WARN")
        place_order(symbol, "Sell" if pos["side"]=="Buy" else "Buy", pos["qty"], razon="STOP LOSS")
        return True
    return False

def check_daily_limit():
    if _DAILY_LOSS_LIMIT_PCT <= 0 or not state["saldo_inicio_dia"]: return False
    saldo_actual = get_balance()
    if not saldo_actual: return False
    perdida_pct = (state["saldo_inicio_dia"] - saldo_actual) / state["saldo_inicio_dia"] * 100
    if perdida_pct >= _DAILY_LOSS_LIMIT_PCT:
        log(f"LIMITE DIARIO alcanzado! Perdida: {perdida_pct:.2f}%", "WARN")
        telegram(f"LIMITE DIARIO alcanzado!\nPerdida: {perdida_pct:.2f}%\nBot detenido por hoy.")
        with state_lock: state["detenido"] = True
        return True
    return False

last_trends = {}  # persistente en --once via archivo

def run_symbol(sym_cfg):
    global last_trends
    symbol = sym_cfg["symbol"]
    qty    = sym_cfg["qty"]
    if check_stop_loss(symbol): return
    if state["detenido"]: log(f"[{symbol}] Detenido por limite diario", "WARN"); return
    if not dentro_de_horario(): log(f"[{symbol}] Fuera de horario"); return

    highs, lows, closes = get_candles(symbol)
    if closes is None or len(closes) < ATR_PERIOD + 5:
        log(f"[{symbol}] Sin datos suficientes", "WARN"); return

    trend = calculate_supertrend(highs, lows, closes)
    current_trend = trend[-1]; prev_trend = trend[-2]
    precio = closes[-1]
    estado = "ALCISTA" if current_trend == 1 else "BAJISTA"

    pos = state["posiciones"].get(symbol)
    pnl = ""
    if pos:
        entrada = pos["precio_entrada"]
        p = (precio-entrada)/entrada*100 if pos["side"]=="Buy" else (entrada-precio)/entrada*100
        pnl = f" | P&L: {p:+.2f}%"
    log(f"[{symbol}] Precio: {precio:.2f} | {estado}{pnl}")

    last = last_trends.get(symbol)
    if last is not None:
        if   prev_trend==-1 and current_trend==1:  log(f"[{symbol}] BUY");  place_order(symbol,"Buy", qty,"SuperTrend BUY")
        elif prev_trend==1  and current_trend==-1: log(f"[{symbol}] SELL"); place_order(symbol,"Sell",qty,"SuperTrend SELL")
        else: log(f"[{symbol}] Sin cambio, tendencia {estado}")
    else:
        log(f"[{symbol}] Primera lectura: {estado}")
    last_trends[symbol] = current_trend

def run_once():
    """Una pasada — para GitHub Actions"""
    # Cargar estado previo desde archivo (para detectar cambio de tendencia)
    state_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".bot_state.txt")
    global last_trends
    if os.path.exists(state_file):
        try:
            with open(state_file) as f:
                for line in f:
                    parts = line.strip().split("=")
                    if len(parts) == 2:
                        last_trends[parts[0]] = int(parts[1])
            log(f"Estado previo cargado: {last_trends}")
        except Exception:
            pass

    modo  = "TESTNET" if _TESTNET else "REAL"
    pares = ", ".join(s["symbol"] for s in _SYMBOLS)
    log(f"Bot ejecutado (--once) | Modo: {modo} | Pares: {pares}")

    saldo = get_balance()
    state["saldo_inicio_dia"] = saldo
    if saldo:
        log(f"Saldo: {saldo:.2f} USDT")

    if check_daily_limit():
        log("Limite diario alcanzado, saliendo.")
        return

    hilos = [threading.Thread(target=run_symbol, args=(s,)) for s in _SYMBOLS]
    for t in hilos: t.start()
    for t in hilos: t.join()

    # Guardar estado para la proxima ejecucion
    try:
        with open(state_file, "w") as f:
            for sym, tr in last_trends.items():
                f.write(f"{sym}={tr}\n")
        log(f"Estado guardado: {last_trends}")
    except Exception:
        pass
    log("Pasada completada.")

def run():
    """Loop continuo — para uso local"""
    global last_trends
    modo  = "TESTNET" if _TESTNET else "REAL"
    pares = ", ".join(s["symbol"] for s in _SYMBOLS)
    log(f"Bot iniciado | Modo: {modo} | Pares: {pares} | TF: Diario")
    log(f"Horario: {_TRADING_HOUR_START}h-{_TRADING_HOUR_END}h | SL: {_STOP_LOSS_PCT}% | Limite diario: {_DAILY_LOSS_LIMIT_PCT}%")
    print("-" * 60)
    telegram(f"Bot iniciado\nModo: {modo}\nPares: {pares}\nSL: {_STOP_LOSS_PCT}%")

    while True:
        try:
            hoy = datetime.now().date()
            if state["dia_actual"] != hoy:
                saldo = get_balance()
                with state_lock:
                    state["dia_actual"] = hoy; state["ordenes_hoy"] = 0
                    state["detenido"] = False; state["saldo_inicio_dia"] = saldo
                log(f"Nuevo dia | Saldo: {saldo:.2f} USDT" if saldo else "Nuevo dia")
                telegram(f"Nuevo dia\nSaldo: {saldo:.2f} USDT" if saldo else "Nuevo dia")

            if check_daily_limit(): time.sleep(CHECK_INTERVAL); continue

            hilos = [threading.Thread(target=run_symbol, args=(s,)) for s in _SYMBOLS]
            for t in hilos: t.start()
            for t in hilos: t.join()

            log(f"Ordenes hoy: {state['ordenes_hoy']} | Proxima verificacion en {CHECK_INTERVAL//60} min")
            print("-" * 60)
            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            log("Bot detenido."); telegram("Bot detenido."); break
        except Exception as e:
            log(f"Error: {e}", "ERROR"); time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    if ONCE_MODE:
        run_once()
    elif _AUTO_RESTART:
        while True:
            try:
                run(); break
            except Exception as e:
                log(f"Bot caido: {e} — reiniciando en {_AUTO_RESTART_DELAY}s...", "ERROR")
                telegram(f"Bot caido:\n{e}\nReiniciando en {_AUTO_RESTART_DELAY}s...")
                time.sleep(_AUTO_RESTART_DELAY)
    else:
        run()
