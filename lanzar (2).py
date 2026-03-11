# -*- coding: utf-8 -*-
"""
LANZAR.PY - Inicia el bot y ngrok automaticamente
"""
import subprocess, sys, time, requests, os, webbrowser

NGROK_PATH = r"C:\Users\Usuario\AppData\Local\Microsoft\WindowsApps\ngrok.exe"

def log(msg):
    print(msg, flush=True)

os.system("cls")
print("=" * 46)
print("   BOT TRADINGVIEW -> BYBIT")
print("   Inicio automatico completo")
print("=" * 46)

# PASO 1: Instalar dependencias
log("\n[1/3] Instalando dependencias...")
result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "flask", "pybit", "requests", "-q"],
    capture_output=True
)
if result.returncode == 0:
    log("    OK - Dependencias listas")
else:
    log(f"    ERROR: {result.stderr.decode()}")
    input("Presiona Enter para salir...")
    sys.exit(1)

# PASO 2: Iniciar el bot
log("\n[2/3] Iniciando el bot...")
bot_dir  = os.path.dirname(os.path.abspath(__file__))
bot_proc = subprocess.Popen(
    [sys.executable, os.path.join(bot_dir, "bot.py")],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

bot_ok = False
for i in range(20):
    time.sleep(1)
    print(f"    Esperando... {i+1}s", end="\r")
    try:
        requests.get("http://localhost:5000", timeout=2)
        bot_ok = True
        break
    except Exception:
        pass

if not bot_ok:
    log("\n    ERROR: El bot no respondio.")
    err = bot_proc.stderr.read(3000).decode(errors="ignore")
    if err:
        log(f"    Detalle: {err}")
    bot_proc.terminate()
    input("Presiona Enter para salir...")
    sys.exit(1)

log("\n    OK - Bot activo en http://localhost:5000")

# PASO 3: Iniciar ngrok
log("\n[3/3] Iniciando ngrok...")

if not os.path.exists(NGROK_PATH):
    log(f"    ERROR: No se encontro ngrok en: {NGROK_PATH}")
    log("    Descargalo en https://ngrok.com/download")
    bot_proc.terminate()
    input("Presiona Enter para salir...")
    sys.exit(1)

ngrok_proc = subprocess.Popen(
    [NGROK_PATH, "http", "5000"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

webhook_url = None
for i in range(20):
    time.sleep(1)
    print(f"    Esperando ngrok... {i+1}s", end="\r")
    try:
        r = requests.get("http://localhost:4040/api/tunnels", timeout=2)
        for t in r.json().get("tunnels", []):
            if t.get("proto") == "https":
                webhook_url = t["public_url"] + "/webhook"
                break
        if webhook_url:
            break
    except Exception:
        pass

if not webhook_url:
    log("\n    ERROR: ngrok no respondio.")
    log("    Asegurate de haber ejecutado: ngrok config add-authtoken TU_TOKEN")
    bot_proc.terminate()
    ngrok_proc.terminate()
    input("Presiona Enter para salir...")
    sys.exit(1)

# MOSTRAR RESULTADO
import config
os.system("cls")
print("=" * 50)
print("   BOT ACTIVO - TODO LISTO")
print("=" * 50)
print(f"""
  Modo    : {'TESTNET (papel)' if config.TESTNET else '*** REAL ***'}
  Symbol  : {config.DEFAULT_SYMBOL}
  Cantidad: {config.DEFAULT_QTY}

  URL PARA TRADINGVIEW:
  {webhook_url}

  Mensaje JSON para TradingView:
  {{
    "secret": "{config.WEBHOOK_SECRET}",
    "symbol": "{{{{ticker}}}}",
    "side":   "{{{{strategy.order.action}}}}",
    "qty":    "{config.DEFAULT_QTY}"
  }}

  Monitor ngrok: http://localhost:4040
  Presiona Ctrl+C para detener el bot
""")

webbrowser.open("http://localhost:4040")

try:
    while True:
        time.sleep(1)
        if bot_proc.poll() is not None:
            log("AVISO: El bot se detuvo inesperadamente")
            break
        if ngrok_proc.poll() is not None:
            log("AVISO: ngrok se detuvo inesperadamente")
            break
except KeyboardInterrupt:
    log("\nDeteniendo bot y ngrok...")
finally:
    bot_proc.terminate()
    ngrok_proc.terminate()
    log("Detenido. Hasta luego!")
    time.sleep(2)
