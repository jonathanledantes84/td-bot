# -*- coding: utf-8 -*-
"""
AUTOBOT.PY - SuperTrend Bot para Bybit
Incluye: Stop Loss, Telegram, Log archivo, Horario, Perdida diaria, Multi-par, Auto-reinicio
"""

import time, sys, io, os, requests, threading
from datetime import datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from pybit.unified_trading import HTTP
import config

# ── CONFIGURACION SUPERTREND ─────────────────────────────
ATR_PERIOD     = 10
ATR_MULTIPLIER = 3.0
TIMEFRAME      = "60"
CHECK_INTERVAL = 60

# ── SESSION ──────────────────────────────────────────────
session = HTTP(
    testnet=config.TESTNET,
    api_key=config.API_KEY,
    api_secret=config.API_SECRET,
)

# ── ESTADO GLOBAL ────────────────────────────────────────
state = {
    "posiciones":       {},   # {"BTCUSDT": {"side":"Buy","precio_entrada":69000,"qty":"0.001"}}
    "ordenes_hoy":      0,
    "perdida_hoy_usd":  0.0,
    "saldo_inicio_dia": None,
    "dia_actual":       None,
    "detenido":         False,
}
state_lock = threading.Lock()

# ── LOG ──────────────────────────────────────────────────
def _log_dir():
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(d, exist_ok=True)
    return d

def log(msg, level="INFO"):
    linea = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{level}] {msg}"
    print(linea, flush=True)
    if config.SAVE_LOG:
        try:
            fname = os.path.join(_log_dir(), f"{datetime.now().strftime('%Y-%m-%d')}.txt")
            with open(fname, "a", encoding="utf-8") as f:
                f.write(linea + "\n")
        except Exception:
            pass

# ── TELEGRAM ─────────────────────────────────────────────
def telegram(msg):
    if not config.TELEGRAM_TOKEN or not config.TELEGRAM_CHAT_ID:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": config.TELEGRAM_CHAT_ID, "text": msg},
            timeout=5
        )
    except Exception as e:
        log(f"Telegram error: {e}", "WARN")

# ── HORARIO ──────────────────────────────────────────────
def dentro_de_horario():
    hora = datetime.now().hour
    return config.TRADING_HOUR_START <= hora < config.TRADING_HOUR_END

# ── SALDO ────────────────────────────────────────────────
def get_balance():
    try:
        r = session.get_wallet_balance(accountType="UNIFIED", coin="USDT")
        return float(r["result"]["list"][0]["coin"][0]["walletBalance"])
    except Exception:
        return None

# ── PRECIO ───────────────────────────────────────────────
def get_precio(symbol):
    try:
        r = session.get_tickers(category="spot", symbol=symbol)
        return float(r["result"]["list"][0]["lastPrice"])
    except Exception:
        return None

# ── VELAS ────────────────────────────────────────────────
def get_candles(symbol):
    try:
        result = session.get_kline(category="spot", symbol=symbol, interval=TIMEFRAME, limit=100)
        candles = sorted(result["result"]["list"], key=lambda x: int(x[0]))
        return (
            [float(c[2]) for c in candles],
            [float(c[3]) for c in candles],
            [float(c[4]) for c in candles],
        )
    except Exception as e:
        log(f"[{symbol}] Error velas: {e}", "ERROR")
        return None, None, None

# ── ATR ──────────────────────────────────────────────────
def calculate_atr(highs, lows, closes, period):
    trs = [max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1]))
           for i in range(1, len(closes))]
    atr = [sum(trs[:period]) / period]
    for i in range(period, len(trs)):
        atr.append((atr[-1] * (period-1) + trs[i]) / period)
    return atr

# ── SUPERTREND ───────────────────────────────────────────
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

# ── ORDEN ────────────────────────────────────────────────
def place_order(symbol, side, qty, razon="SENAL"):
    try:
        result = session.place_order(
            category="linear", symbol=symbol,
            side=side, orderType="Market",
            qty=str(qty), timeInForce="GTC",
        )
        order_id = result["result"]["orderId"]
        precio   = get_precio(symbol) or 0
        log(f"[{symbol}] {razon} | {side} {qty} @ {precio:.2f} | ID: {order_id}", "TRADE")

        with state_lock:
            state["ordenes_hoy"] += 1
            if razon != "STOP LOSS":
                state["posiciones"][symbol] = {"side": side, "precio_entrada": precio, "qty": qty}
            else:
                state["posiciones"].pop(symbol, None)

        modo = "TESTNET" if config.TESTNET else "REAL"
        telegram(f"[{side.upper()}] {razon}\nPar: {symbol}\nPrecio: {precio:.2f}\nCantidad: {qty}\nModo: {modo}")
        return True
    except Exception as e:
        log(f"[{symbol}] Orden fallida: {e}", "ERROR")
        telegram(f"ERROR orden {side} {symbol}: {e}")
        return False

# ── STOP LOSS ────────────────────────────────────────────
def check_stop_loss(symbol):
    pos = state["posiciones"].get(symbol)
    if not pos or config.STOP_LOSS_PCT <= 0:
        return False
    precio = get_precio(symbol)
    if not precio:
        return False
    entrada = pos["precio_entrada"]
    pct = (entrada-precio)/entrada*100 if pos["side"]=="Buy" else (precio-entrada)/entrada*100
    if pct >= config.STOP_LOSS_PCT:
        log(f"[{symbol}] STOP LOSS! Perdida: {pct:.2f}%", "WARN")
        close_side = "Sell" if pos["side"]=="Buy" else "Buy"
        place_order(symbol, close_side, pos["qty"], razon="STOP LOSS")
        with state_lock:
            state["perdida_hoy_usd"] += pct / 100 * float(pos["qty"]) * entrada
        return True
    return False

# ── LIMITE DIARIO ────────────────────────────────────────
def check_daily_limit():
    if config.DAILY_LOSS_LIMIT_PCT <= 0 or not state["saldo_inicio_dia"]:
        return False
    saldo_actual = get_balance()
    if not saldo_actual:
        return False
    perdida_pct = (state["saldo_inicio_dia"] - saldo_actual) / state["saldo_inicio_dia"] * 100
    if perdida_pct >= config.DAILY_LOSS_LIMIT_PCT:
        log(f"LIMITE DIARIO alcanzado! Perdida: {perdida_pct:.2f}% | Bot detenido por hoy.", "WARN")
        telegram(f"LIMITE DIARIO alcanzado!\nPerdida: {perdida_pct:.2f}%\nBot detenido por hoy.")
        with state_lock:
            state["detenido"] = True
        return True
    return False

# ── LOOP POR PAR ─────────────────────────────────────────
def run_symbol(sym_cfg, last_trends):
    symbol = sym_cfg["symbol"]
    qty    = sym_cfg["qty"]

    if check_stop_loss(symbol):
        return
    if state["detenido"]:
        log(f"[{symbol}] Bot detenido por limite diario, saltando...", "WARN")
        return
    if not dentro_de_horario():
        log(f"[{symbol}] Fuera de horario ({config.TRADING_HOUR_START}h-{config.TRADING_HOUR_END}h), esperando...")
        return

    highs, lows, closes = get_candles(symbol)
    if closes is None or len(closes) < ATR_PERIOD + 5:
        log(f"[{symbol}] Sin datos suficientes", "WARN")
        return

    trend         = calculate_supertrend(highs, lows, closes)
    current_trend = trend[-1]
    prev_trend    = trend[-2]
    precio        = closes[-1]
    estado        = "ALCISTA" if current_trend == 1 else "BAJISTA"

    pos = state["posiciones"].get(symbol)
    pnl = ""
    if pos and config.STOP_LOSS_PCT > 0:
        entrada = pos["precio_entrada"]
        p = (precio-entrada)/entrada*100 if pos["side"]=="Buy" else (entrada-precio)/entrada*100
        pnl = f" | P&L: {p:+.2f}%"

    log(f"[{symbol}] Precio: {precio:.2f} | {estado}{pnl}")

    last = last_trends.get(symbol)
    if last is not None:
        if prev_trend == -1 and current_trend == 1:
            log(f"[{symbol}] Cambio ALCISTA -> BUY")
            place_order(symbol, "Buy", qty, razon="SuperTrend BUY")
        elif prev_trend == 1 and current_trend == -1:
            log(f"[{symbol}] Cambio BAJISTA -> SELL")
            place_order(symbol, "Sell", qty, razon="SuperTrend SELL")
        else:
            log(f"[{symbol}] Sin cambio, esperando...")
    else:
        log(f"[{symbol}] Primera lectura, esperando senal...")

    last_trends[symbol] = current_trend

# ── MAIN ─────────────────────────────────────────────────
def run():
    last_trends = {}
    modo = "TESTNET" if config.TESTNET else "REAL"
    pares = ", ".join(s["symbol"] for s in config.SYMBOLS)

    log(f"Bot iniciado | Modo: {modo} | Pares: {pares}")
    log(f"Horario: {config.TRADING_HOUR_START}h-{config.TRADING_HOUR_END}h | SL: {config.STOP_LOSS_PCT}% | Perdida diaria max: {config.DAILY_LOSS_LIMIT_PCT}%")
    log(f"Telegram: {'activado' if config.TELEGRAM_TOKEN else 'desactivado'} | Auto-reinicio: {'activado' if config.AUTO_RESTART else 'desactivado'}")
    print("-" * 55)

    telegram(f"Bot iniciado\nModo: {modo}\nPares: {pares}\nHorario: {config.TRADING_HOUR_START}h-{config.TRADING_HOUR_END}h")

    while True:
        try:
            hoy = datetime.now().date()

            # Reset diario
            if state["dia_actual"] != hoy:
                with state_lock:
                    state["dia_actual"]       = hoy
                    state["ordenes_hoy"]      = 0
                    state["perdida_hoy_usd"]  = 0.0
                    state["detenido"]         = False
                    state["saldo_inicio_dia"] = get_balance()
                log(f"Nuevo dia | Saldo inicial: {state['saldo_inicio_dia']:.2f} USDT")
                telegram(f"Nuevo dia de trading\nSaldo: {state['saldo_inicio_dia']:.2f} USDT")

            # Verificar limite diario
            if check_daily_limit():
                time.sleep(CHECK_INTERVAL)
                continue

            # Correr cada par en hilo separado
            hilos = []
            for sym_cfg in config.SYMBOLS:
                t = threading.Thread(target=run_symbol, args=(sym_cfg, last_trends))
                t.start()
                hilos.append(t)
            for t in hilos:
                t.join()

            log(f"Ordenes hoy: {state['ordenes_hoy']} | Proxima verificacion en {CHECK_INTERVAL}s")
            print("-" * 55)
            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            log("Bot detenido por el usuario.")
            telegram("Bot detenido manualmente.")
            break
        except Exception as e:
            log(f"Error inesperado: {e}", "ERROR")
            time.sleep(CHECK_INTERVAL)

# ── ARRANQUE CON AUTO-REINICIO ───────────────────────────
if __name__ == "__main__":
    if not config.AUTO_RESTART:
        run()
    else:
        while True:
            try:
                run()
                break  # salida normal (Ctrl+C)
            except Exception as e:
                log(f"Bot caido: {e} — reiniciando en {config.AUTO_RESTART_DELAY}s...", "ERROR")
                telegram(f"Bot caido: {e}\nReiniciando en {config.AUTO_RESTART_DELAY}s...")
                time.sleep(config.AUTO_RESTART_DELAY)
