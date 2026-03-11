# SuperTrend Bot — Bybit

Bot de trading automatico para Bybit. Calcula el indicador SuperTrend en Python y ejecuta ordenes sin TradingView ni intervencion manual.

---

## Como funciona

```
Bybit API → Velas OHLC → SuperTrend → Cambio de tendencia → Orden BUY/SELL
```

- Tendencia cambia a ALCISTA → **BUY**
- Tendencia cambia a BAJISTA → **SELL**
- Sin cambio → espera y vuelve a verificar

---

## Funcionalidades

- Multi-par en paralelo (BTC, ETH, SOL, etc.)
- Stop Loss automatico por operacion
- Limite de perdida diaria
- Horario de trading configurable
- Notificaciones por Telegram
- Log en archivo por fecha
- Auto-reinicio si el bot falla
- Dashboard con Streamlit + graficos Plotly
- Compatible con Railway, Replit y Windows local

---

## Archivos

```
bot-railway/
  ├── config.py         → API keys y configuracion (el unico que editas)
  ├── autobot.py        → bot principal
  ├── dashboard.py      → panel visual con Streamlit
  ├── requirements.txt  → dependencias
  └── Procfile          → para deploy en Railway
```

---

## Instalacion rapida (Windows)

```bash
# 1. Instalar dependencias
python instalar.py

# 2. Editar config.py con tus API keys de Bybit

# 3. Iniciar el bot
python autobot.py

# 4. Iniciar el dashboard (opcional)
streamlit run dashboard.py
```

---

## Configuracion principal (config.py)

```python
API_KEY    = "tu api key"
API_SECRET = "tu secret key"
TESTNET    = True   # True = practica | False = dinero real

SYMBOLS = [
    {"symbol": "BTCUSDT", "qty": "0.001"},
]

STOP_LOSS_PCT        = 2.0   # % maximo de perdida por operacion
DAILY_LOSS_LIMIT_PCT = 5.0   # % maximo de perdida diaria
TRADING_HOUR_START   = 9     # hora de inicio
TRADING_HOUR_END     = 22    # hora de fin
AUTO_RESTART         = True

TELEGRAM_TOKEN   = ""   # dejar vacio para desactivar
TELEGRAM_CHAT_ID = ""
```

### Parametros del bot (autobot.py)

```python
ATR_PERIOD     = 10     # periodo SuperTrend
ATR_MULTIPLIER = 3.0    # multiplicador
TIMEFRAME      = "D"    # "D"=diario | "60"=1hora | "15"=15min
CHECK_INTERVAL = 3600   # segundos entre verificaciones
```

---

## Deploy en Railway (24/7)

1. Crear proyecto en [railway.app](https://railway.app)
2. Subir los archivos de `bot-railway/`
3. Configurar variables de entorno: `API_KEY`, `API_SECRET`
4. Railway detecta el `Procfile` y arranca automaticamente

---

## Deploy en Replit

1. Subir archivos a [replit.com](https://replit.com)
2. En la terminal: `pip install pybit requests flask`
3. Click en Run
4. Usar [UptimeRobot](https://uptimerobot.com) para mantenerlo activo gratis

---

## Configurar Telegram

1. Habla con **@BotFather** → `/newbot` → copia el TOKEN
2. Habla con **@userinfobot** → copia tu CHAT_ID
3. Pegalos en `config.py`

---

## Cuentas necesarias

| Cuenta | URL |
|--------|-----|
| Bybit Testnet (practica) | https://testnet.bybit.com |
| Bybit Real | https://bybit.com |
| Railway (nube) | https://railway.app |

---

## Advertencias

- Empieza siempre con `TESTNET = True`
- Nunca subas `config.py` con tus API keys a GitHub
- Los bots pueden perder dinero — solo arriesga lo que puedas perder
- Usa variables de entorno para las keys en produccion

---

## TradingView — como usarlo junto al bot

El bot calcula SuperTrend solo, sin necesitar TradingView. Pero TradingView es util para:

### 1. Backtesting antes de cambiar parametros
Antes de modificar `ATR_PERIOD` o `ATR_MULTIPLIER`, probarlo visualmente en TradingView con datos historicos para ver rentabilidad y cantidad de senales.

Configuracion que coincide con el bot:
- Indicador: **SuperTrend Strategy** (KivancOzbilgic)
- ATR Period: `10`
- ATR Multiplier: `3.0`
- Timeframe: `1D`

### 2. Validar que el bot calcula igual
Tener abierto TradingView con el mismo SuperTrend para confirmar que las senales del bot coinciden con el grafico.

### 3. Alertas de contexto macro
Configurar alertas manuales para eventos que el bot no monitorea — ruptura de soporte, RSI extremo, volumen inusual — y decidir si pausar el bot manualmente.

> El bot NO necesita webhooks de TradingView. Calcula todo directamente desde la API de Bybit.

---

## Herramientas recomendadas

| Herramienta | Para que |
|-------------|----------|
| [Cursor](https://cursor.com) | Editar el bot con IA |
| [Railway](https://railway.app) | Correr 24/7 en la nube |
| [UptimeRobot](https://uptimerobot.com) | Monitorear que este activo |
| [TradingView](https://tradingview.com) | Backtesting y validacion visual |
| [Streamlit](https://streamlit.io) | Dashboard en Python |
