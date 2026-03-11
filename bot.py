# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from flask import Flask, request, jsonify
from pybit.unified_trading import HTTP
from datetime import datetime
import config

app = Flask(__name__)

session = HTTP(
    testnet=config.TESTNET,
    api_key=config.API_KEY,
    api_secret=config.API_SECRET,
)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def set_leverage(symbol):
    try:
        session.set_leverage(
            category="linear", symbol=symbol,
            buyLeverage=str(config.DEFAULT_LEVERAGE),
            sellLeverage=str(config.DEFAULT_LEVERAGE),
        )
    except Exception:
        pass

def place_order(symbol, side, qty):
    try:
        set_leverage(symbol)
        result = session.place_order(
            category="linear", symbol=symbol,
            side=side, orderType="Market",
            qty=str(qty), timeInForce="GTC",
        )
        order_id = result["result"]["orderId"]
        log(f"[OK] Orden ejecutada: {side} {qty} {symbol} | ID: {order_id}")
        return {"ok": True, "order_id": order_id}
    except Exception as e:
        log(f"[ERROR] {e}")
        return {"ok": False, "error": str(e)}

def get_balance():
    try:
        result = session.get_wallet_balance(accountType="UNIFIED", coin="USDT")
        return float(result["result"]["list"][0]["coin"][0]["walletBalance"])
    except Exception:
        return None

@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "estado": "Bot activo",
        "modo": "TESTNET" if config.TESTNET else "REAL",
        "saldo_usdt": get_balance(),
        "symbol": config.DEFAULT_SYMBOL,
        "cantidad": config.DEFAULT_QTY,
    })

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Payload vacio"}), 400

        log(f"Alerta recibida: {data}")

        if data.get("secret") != config.WEBHOOK_SECRET:
            log("Acceso denegado - clave incorrecta")
            return jsonify({"error": "No autorizado"}), 403

        symbol   = data.get("symbol", config.DEFAULT_SYMBOL).upper()
        qty      = data.get("qty", config.DEFAULT_QTY)
        side_raw = data.get("side", "").lower()
        side_map = {"buy": "Buy", "sell": "Sell", "long": "Buy", "short": "Sell"}
        side     = side_map.get(side_raw)

        if not side:
            return jsonify({"error": f"side invalido: {side_raw}"}), 400

        result = place_order(symbol, side, qty)
        return jsonify({"estado": "ok" if result["ok"] else "error", **result}), 200 if result["ok"] else 500

    except Exception as e:
        log(f"Error inesperado: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/balance", methods=["GET"])
def balance():
    return jsonify({"saldo_usdt": get_balance()})

if __name__ == "__main__":
    log(f"Bot iniciado - Modo: {'TESTNET' if config.TESTNET else 'REAL'}")
    log(f"Symbol: {config.DEFAULT_SYMBOL} | Cantidad: {config.DEFAULT_QTY}")
    log(f"Escuchando en http://localhost:{config.PORT}/webhook")
    app.run(host="0.0.0.0", port=config.PORT, debug=False)
