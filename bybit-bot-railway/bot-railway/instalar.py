"""
En Replit ejecuta en la terminal:
  pip install pybit requests flask

En Windows ejecuta:
  python instalar.py
"""
import subprocess, sys
print("Instalando dependencias...")
r = subprocess.run([sys.executable, "-m", "pip", "install", "pybit", "requests", "flask", "-q"], capture_output=True, text=True)
print("Listo." if r.returncode == 0 else f"Error: {r.stderr}")
