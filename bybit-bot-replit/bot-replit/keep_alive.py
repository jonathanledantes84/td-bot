"""
KEEP_ALIVE.PY — Mantiene el bot activo en Replit
Corre un servidor web minimo para que UptimeRobot lo pingee cada 5 minutos
"""
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot activo"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
