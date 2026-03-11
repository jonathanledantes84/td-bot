# =============================================
#   CONFIG.PY — Edita solo este archivo
# =============================================

# --- Bybit API ---
API_KEY    = "PEGA_TU_API_KEY_AQUI"
API_SECRET = "PEGA_TU_API_SECRET_AQUI"
TESTNET    = True   # True = practica | False = dinero real

# --- Pares a operar ---
# Podes agregar o quitar pares. El bot los corre todos al mismo tiempo.
SYMBOLS = [
    {"symbol": "BTCUSDT", "qty": "0.001"},
    # {"symbol": "ETHUSDT", "qty": "0.01"},
    # {"symbol": "SOLUSDT", "qty": "0.1"},
]

# --- Apalancamiento ---
DEFAULT_LEVERAGE = 1   # 1 = sin apalancamiento (recomendado para empezar)

# --- Stop Loss por operacion ---
# Cierra la posicion si la perdida supera este porcentaje
# Ejemplo: 2.0 = cierra si pierde 2%
# Poner 0 para desactivar
STOP_LOSS_PCT = 2.0

# --- Limite de perdida diaria ---
# El bot se detiene si la perdida del dia supera este % del saldo inicial
# Poner 0 para desactivar
DAILY_LOSS_LIMIT_PCT = 5.0

# --- Horario de trading ---
# El bot solo opera dentro de este rango (formato 24hs)
# Para operar siempre: START = 0 | END = 24
TRADING_HOUR_START = 9    # 9am
TRADING_HOUR_END   = 22   # 10pm

# --- Reinicio automatico ---
# Si el bot falla por error, se reinicia solo
AUTO_RESTART       = True
AUTO_RESTART_DELAY = 30   # segundos antes de reiniciar

# --- Telegram (opcional) ---
# Para recibir notificaciones en el celular:
# 1. Habla con @BotFather en Telegram → /newbot → copia el TOKEN
# 2. Habla con @userinfobot en Telegram → copia tu CHAT_ID
# Dejar vacios ("") para desactivar
TELEGRAM_TOKEN   = ""
TELEGRAM_CHAT_ID = ""

# --- Log en archivo ---
# Guarda todos los mensajes en la carpeta /logs, un archivo por dia
SAVE_LOG = True

# --- Seguridad webhook (no tocar) ---
WEBHOOK_SECRET = "mi_clave_secreta_123"
DEFAULT_SYMBOL = "BTCUSDT"
DEFAULT_QTY    = "0.001"
PORT           = 5000
