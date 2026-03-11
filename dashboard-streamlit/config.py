# =============================================
#   CONFIG.PY — Edita solo este archivo
# =============================================

# --- Bybit API ---
# ⚠️ En Streamlit Cloud usar Secrets (no poner keys aqui)
API_KEY    = ""
API_SECRET = ""
TESTNET    = True

# --- Pares a operar ---
SYMBOLS = [
    {"symbol": "BTCUSDT", "qty": "0.001"},
]

STOP_LOSS_PCT        = 2.0
DAILY_LOSS_LIMIT_PCT = 5.0
TRADING_HOUR_START   = 0
TRADING_HOUR_END     = 24
AUTO_RESTART         = True
AUTO_RESTART_DELAY   = 30
TELEGRAM_TOKEN       = ""
TELEGRAM_CHAT_ID     = ""
SAVE_LOG             = False
WEBHOOK_SECRET       = ""
DEFAULT_SYMBOL       = "BTCUSDT"
DEFAULT_QTY          = "0.001"
PORT                 = 5000
