# =============================================
#   CONFIG.PY — Edita solo este archivo
# =============================================

# --- Bybit API ---
# Obtén tus claves en: https://bybit.com → Account → API Management
API_KEY    = "PEGA_TU_API_KEY_AQUI"
API_SECRET = "PEGA_TU_API_SECRET_AQUI"

# --- Modo ---
# True  = Testnet (dinero ficticio, para practicar) ✅ EMPIEZA AQUÍ
# False = Real (dinero real) ⚠️ solo cuando estés seguro
TESTNET = True

# --- Seguridad del webhook ---
# Una contraseña cualquiera para que solo TradingView pueda enviarte alertas
WEBHOOK_SECRET = "mi_clave_secreta_123"

# --- Configuración por defecto ---
DEFAULT_SYMBOL = "BTCUSDT"   # Par de trading
DEFAULT_QTY    = "0.001"     # Cantidad por orden
DEFAULT_LEVERAGE = 1         # Apalancamiento (1 = sin apalancamiento)

# --- Puerto del servidor ---
PORT = 5000
