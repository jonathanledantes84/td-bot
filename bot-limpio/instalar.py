"""
INSTALAR.PY — Instalador automático
=====================================
Ejecuta esto PRIMERO:  python instalar.py
"""

import subprocess
import sys
import os

def run(cmd, descripcion):
    print(f"\n⏳ {descripcion}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ {descripcion} — OK")
    else:
        print(f"❌ Error: {result.stderr}")
        return False
    return True

print("=" * 55)
print("  INSTALADOR DEL BOT TRADINGVIEW → BYBIT")
print("=" * 55)

# 1. Verificar Python
version = sys.version_info
if version.major < 3 or version.minor < 10:
    print(f"❌ Necesitas Python 3.10+. Tienes: {sys.version}")
    print("   Descarga en: https://python.org")
    sys.exit(1)
print(f"✅ Python {version.major}.{version.minor} detectado")

# 2. Instalar dependencias
run(f"{sys.executable} -m pip install --upgrade pip", "Actualizando pip")
run(f"{sys.executable} -m pip install flask pybit requests", "Instalando librerías (flask, pybit, requests)")

# 3. Verificar ngrok
print("\n⏳ Verificando ngrok...")
result = subprocess.run("ngrok version", shell=True, capture_output=True)
if result.returncode == 0:
    print("✅ ngrok ya está instalado")
else:
    print("⚠️  ngrok NO encontrado.")
    print("   📥 Descárgalo gratis en: https://ngrok.com/download")
    print("   (Lo necesitas para exponer el bot a internet)")

# 4. Instrucciones finales
print("\n" + "=" * 55)
print("  ✅ INSTALACIÓN COMPLETA")
print("=" * 55)
print("""
PRÓXIMOS PASOS:

  1. Edita config.py con tus datos de Bybit
     → API_KEY, API_SECRET, WEBHOOK_SECRET

  2. Inicia el bot:
     python bot.py

  3. En otra terminal, expón el bot con ngrok:
     ngrok http 5000

  4. Copia la URL de ngrok (ej: https://abc123.ngrok.io)
     Tu webhook URL será: https://abc123.ngrok.io/webhook

  5. En TradingView → Crear alerta → Webhook URL → pega la URL
     Mensaje JSON:
     {
       "secret":  "tu_clave_secreta",
       "symbol":  "{{ticker}}",
       "side":    "{{strategy.order.action}}",
       "qty":     "0.001"
     }

  6. Prueba todo localmente (con bot.py corriendo):
     python test.py
""")
