# -*- coding: utf-8 -*-
"""
AUTOBOT.PY - SuperTrend Bot sin TradingView
Calcula SuperTrend directamente y opera en Bybit automaticamente.

Ejecutar: python autobot.py
"""

import time
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from pybit.unified_trading import HTTP
from datetime import datetime
import config

# ── CONFIGURACION SUPERTREND ─────────────────────────────
ATR_PERIOD     = 10       # Periodo ATR (igual que en TradingView)
ATR_MULTIPLIER = 3.0      # Multiplicador ATR
TIMEFRAME      = "60"     # Velas: "1"=1min "5"=5min "15"=15min "60"=1hora "D"=diario
CHECK_INTERVAL = 60       # Segundos entre cada verificacion (recomendado = 60)

# ────────────────────────────────────────────────────────
session = HTTP(
    testnet=config.TESTNET,
    api_key=config.API_KEY,
    api_secret=config.API_SECRET,
)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

# ── OBTENER VELAS ────────────────────────────────────────
def get_candles(symbol, interval, limit=100):
    try:
        result = session.get_kline(
            category="spot",
            symbol=symbol,
            interval=interval,
            limit=limit,
        )
        candles = result["result"]["list"]
        # Cada vela: [timestamp, open, high, low, close, volume, turnover]
        candles = sorted(candles, key=lambda x: int(x[0]))  # orden cronologico
        highs  = [float(c[2]) for c in candles]
        lows   = [float(c[3]) for c in candles]
        closes = [float(c[4]) for c in candles]
        return highs, lows, closes
    except Exception as e:
        log(f"[ERROR] Obteniendo velas: {e}")
        return None, None, None

# ── CALCULAR ATR ─────────────────────────────────────────
def calculate_atr(highs, lows, closes, period):
    trs = []
    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i-1]),
            abs(lows[i] - closes[i-1])
        )
        trs.append(tr)

    # ATR con media movil suavizada (Wilder)
    atr = [sum(trs[:period]) / period]
    for i in range(period, len(trs)):
        atr.append((atr[-1] * (period - 1) + trs[i]) / period)
    return atr

# ── CALCULAR SUPERTREND ──────────────────────────────────
def calculate_supertrend(highs, lows, closes, period, multiplier):
    atr = calculate_atr(highs, lows, closes, period)
    offset = period  # los primeros 'period' valores no tienen ATR

    upper_band = []
    lower_band = []
    supertrend = []
    trend = []

    for i in range(len(atr)):
        idx = i + offset
        hl2 = (highs[idx] + lows[idx]) / 2
        basic_upper = hl2 + multiplier * atr[i]
        basic_lower = hl2 - multiplier * atr[i]

        if i == 0:
            upper_band.append(basic_upper)
            lower_band.append(basic_lower)
            if closes[idx] <= basic_upper:
                supertrend.append(basic_upper)
                trend.append(-1)
            else:
                supertrend.append(basic_lower)
                trend.append(1)
        else:
            # Upper band
            ub = basic_upper if basic_upper < upper_band[-1] or closes[idx-1] > upper_band[-1] else upper_band[-1]
            upper_band.append(ub)
            # Lower band
            lb = basic_lower if basic_lower > lower_band[-1] or closes[idx-1] < lower_band[-1] else lower_band[-1]
            lower_band.append(lb)
            # Trend
            if trend[-1] == -1 and closes[idx] > upper_band[-1]:
                trend.append(1)
            elif trend[-1] == 1 and closes[idx] < lower_band[-1]:
                trend.append(-1)
            else:
                trend.append(trend[-1])

            supertrend.append(lower_band[-1] if trend[-1] == 1 else upper_band[-1])

    return trend

# ── COLOCAR ORDEN ────────────────────────────────────────
def place_order(symbol, side, qty):
    try:
        result = session.place_order(
            category="linear",
            symbol=symbol,
            side=side,
            orderType="Market",
            qty=str(qty),
            timeInForce="GTC",
        )
        order_id = result["result"]["orderId"]
        log(f"[OK] Orden ejecutada: {side} {qty} {symbol} | ID: {order_id}")
        return True
    except Exception as e:
        log(f"[ERROR] Orden fallida: {e}")
        return False

# ── LOOP PRINCIPAL ───────────────────────────────────────
def run():
    symbol     = config.DEFAULT_SYMBOL
    qty        = config.DEFAULT_QTY
    last_trend = None

    modo = "TESTNET" if config.TESTNET else "REAL"
    log(f"Bot SuperTrend iniciado | Modo: {modo} | {symbol} | TF: {TIMEFRAME}min")
    log(f"Verificando cada {CHECK_INTERVAL} segundos...")
    log("Presiona Ctrl+C para detener")
    print("-" * 50)

    while True:
        try:
            highs, lows, closes = get_candles(symbol, TIMEFRAME)

            if closes is None or len(closes) < ATR_PERIOD + 5:
                log("[WARN] No hay suficientes datos, reintentando...")
                time.sleep(CHECK_INTERVAL)
                continue

            trend = calculate_supertrend(highs, lows, closes, ATR_PERIOD, ATR_MULTIPLIER)
            current_trend = trend[-1]
            prev_trend    = trend[-2]

            precio_actual = closes[-1]
            estado = "ALCISTA (BUY)" if current_trend == 1 else "BAJISTA (SELL)"
            log(f"Precio: {precio_actual:.2f} | Tendencia: {estado}")

            # Solo opera cuando hay CAMBIO de tendencia
            if last_trend is not None:
                if prev_trend == -1 and current_trend == 1:
                    log("[SENAL] Cambio a ALCISTA -> BUY")
                    place_order(symbol, "Buy", qty)
                elif prev_trend == 1 and current_trend == -1:
                    log("[SENAL] Cambio a BAJISTA -> SELL")
                    place_order(symbol, "Sell", qty)
                else:
                    log("Sin cambio de tendencia, esperando...")
            else:
                log("Primera lectura, esperando cambio de tendencia...")

            last_trend = current_trend
            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            log("Bot detenido por el usuario.")
            break
        except Exception as e:
            log(f"[ERROR] {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    run()
