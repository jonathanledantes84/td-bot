"""
TEST.PY — Prueba el bot localmente antes de conectar TradingView
================================================================
Ejecuta: python test.py
"""

import requests
import json
import config

BASE = f"http://localhost:{config.PORT}"

def separador(titulo):
    print(f"\n{'='*50}")
    print(f"  {titulo}")
    print('='*50)

# ── 1. Health check ──────────────────────────────────────
separador("1. Verificar que el bot está activo")
try:
    r = requests.get(BASE)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"❌ Bot no responde. ¿Está corriendo bot.py? Error: {e}")
    exit(1)

# ── 2. Saldo ─────────────────────────────────────────────
separador("2. Consultar saldo")
r = requests.get(f"{BASE}/balance")
print(json.dumps(r.json(), indent=2, ensure_ascii=False))

# ── 3. Orden de COMPRA ───────────────────────────────────
separador("3. Simular alerta BUY de TradingView")
payload = {
    "secret": config.WEBHOOK_SECRET,
    "symbol": config.DEFAULT_SYMBOL,
    "side":   "buy",
    "qty":    config.DEFAULT_QTY,
}
print(f"Enviando: {json.dumps(payload, indent=2)}")
r = requests.post(f"{BASE}/webhook", json=payload)
print(f"\nRespuesta ({r.status_code}):")
print(json.dumps(r.json(), indent=2, ensure_ascii=False))

# ── 4. Orden de VENTA ────────────────────────────────────
separador("4. Simular alerta SELL de TradingView")
payload["side"] = "sell"
print(f"Enviando: {json.dumps(payload, indent=2)}")
r = requests.post(f"{BASE}/webhook", json=payload)
print(f"\nRespuesta ({r.status_code}):")
print(json.dumps(r.json(), indent=2, ensure_ascii=False))

# ── 5. Clave incorrecta ──────────────────────────────────
separador("5. Probar seguridad (clave incorrecta)")
payload["secret"] = "clave_mala"
r = requests.post(f"{BASE}/webhook", json=payload)
print(f"Respuesta ({r.status_code}): {r.json()}")
if r.status_code == 403:
    print("✅ Seguridad OK — rechazó la clave incorrecta")

print("\n✅ Pruebas completadas")
