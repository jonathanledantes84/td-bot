"""
INSTALAR.PY — Instala las dependencias del bot
Ejecutar UNA SOLA VEZ:  python instalar.py
"""

import subprocess, sys

print("=" * 50)
print("  INSTALADOR — SuperTrend Bot para Bybit")
print("=" * 50)

version = sys.version_info
if version.major < 3 or version.minor < 10:
    print(f"Necesitas Python 3.10 o superior. Tienes: {sys.version}")
    print("Descarga en: https://python.org")
    sys.exit(1)

print(f"Python {version.major}.{version.minor} OK")
print("Instalando dependencias...")

result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "pybit", "requests", "-q"],
    capture_output=True, text=True
)

if result.returncode == 0:
    print("Dependencias instaladas correctamente.")
else:
    print(f"Error al instalar: {result.stderr}")
    sys.exit(1)

print()
print("=" * 50)
print("  LISTO — Proximos pasos:")
print("=" * 50)
print("""
  1. Abre config.py y pega tus API keys de Bybit
  2. Doble clic en INICIAR_AUTOBOT.bat para iniciar
  3. Abre dashboard.html en el navegador
""")
