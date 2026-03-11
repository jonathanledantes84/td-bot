# =============================================
#   CONFIG.PY — Edita solo este archivo
# =============================================

# --- Bybit API ---
API_KEY    = "PEGA_TU_API_KEY_AQUI"
API_SECRET = "PEGA_TU_API_SECRET_AQUI"
TESTNET    = True   # True = practica | False = dinero real

# --- Seguridad webhook ---
WEBHOOK_SECRET = "mi_clave_secreta_123"

# --- Pares a operar (pueden ser varios) ---
# El bot corre cada par en paralelo
SYMBOLS = [
    {"symbol": "BTCUSDT", "qty": "0.001"},
    {"symbol": "ETHUSDT", "qty": "0.01"},
    {"symbol": "SOLUSDT", "qty": "0.1"},
]

# --- Apalancamiento ---
DEFAULT_LEVERAGE = 1

# --- Stop Loss por operacion ---
# Porcentaje de perdida maxima por operacion (ej: 2.0 = 2%)
# Poner en 0 para desactivar
STOP_LOSS_PCT = 2.0

# --- Limite de perdida diaria ---
# El bot se detiene si la perdida del dia supera este % del saldo inicial
# Poner en 0 para desactivar
DAILY_LOSS_LIMIT_PCT = 5.0

# --- Horario de trading ---
# El bot solo opera dentro de este rango horario
# Usar formato 24hs. Ej: 9 = 9am, 18 = 6pm
# Poner TRADING_HOUR_START = 0 y TRADING_HOUR_END = 24 para operar siempre
TRADING_HOUR_START = 9    # hora de inicio (9am)
TRADING_HOUR_END   = 22   # hora de fin (10pm)

# --- Reinicio automatico ---
# Si el bot falla, se reinicia automaticamente despues de X segundos
AUTO_RESTART        = True
AUTO_RESTART_DELAY  = 30   # segundos antes de reiniciar

# --- Telegram (opcional) ---
# 1. Habla con @BotFather en Telegram → /newbot → copia el TOKEN
# 2. Habla con @userinfobot → copia tu CHAT_ID
# Dejar vacios ("") para desactivar
TELEGRAM_TOKEN   = ""
TELEGRAM_CHAT_ID = ""

# --- Log en archivo ---
SAVE_LOG = True   # guarda logs en carpeta /logs

# --- Puerto ---
PORT = 5000
