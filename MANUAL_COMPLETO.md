# MANUAL COMPLETO — SuperTrend Bot para Bybit
### Guia definitiva: desarrollo, uso, deploy y herramientas

---

## INDICE

1. [Que hace el bot](#1-que-hace-el-bot)
2. [Cuentas necesarias](#2-cuentas-necesarias)
3. [Archivos del proyecto](#3-archivos-del-proyecto)
4. [Instalacion local (Windows)](#4-instalacion-local-windows)
5. [Configuracion completa](#5-configuracion-completa)
6. [Como funciona SuperTrend](#6-como-funciona-supertrend)
7. [Funcionalidades incluidas](#7-funcionalidades-incluidas)
8. [Uso diario](#8-uso-diario)
9. [Dashboard Streamlit](#9-dashboard-streamlit)
10. [Deploy en Railway (24/7)](#10-deploy-en-railway-247)
11. [Deploy en Replit (alternativa)](#11-deploy-en-replit-alternativa)
12. [Configurar Telegram](#12-configurar-telegram)
13. [Pasar a dinero real](#13-pasar-a-dinero-real)
14. [Herramientas recomendadas](#14-herramientas-recomendadas)
15. [Prompts para IA](#15-prompts-para-ia)
16. [Problemas comunes](#16-problemas-comunes)
17. [Proximas mejoras sugeridas](#17-proximas-mejoras-sugeridas)
18. [Seguridad](#18-seguridad)

---

## 1. Que hace el bot

El bot descarga velas de Bybit cada hora, calcula el indicador SuperTrend
en timeframe diario, y ejecuta ordenes automaticamente cuando detecta un
cambio de tendencia.

**Flujo completo:**

```
Bybit API → Velas OHLC → Calculo SuperTrend → Cambio de tendencia?
                                                      |
                                          SI          |        NO
                                           |                    |
                               Ejecuta BUY o SELL        Espera 1 hora
                                           |
                               Notifica por Telegram
                               Guarda en log
                               Verifica Stop Loss
```

**Reglas de operacion:**
- Tendencia cambia a ALCISTA → ejecuta **BUY**
- Tendencia cambia a BAJISTA → ejecuta **SELL**
- Perdida supera STOP_LOSS_PCT → cierra posicion automaticamente
- Perdida diaria supera DAILY_LOSS_LIMIT_PCT → bot se detiene hasta el dia siguiente
- Fuera del horario configurado → no opera
- Bot se cae por error → se reinicia automaticamente

---

## 2. Cuentas necesarias

| Cuenta | Para que | URL |
|--------|----------|-----|
| Bybit Testnet | Practicar con dinero ficticio | https://testnet.bybit.com |
| Bybit Real | Operar con dinero real | https://bybit.com |
| Railway | Correr el bot 24/7 en la nube | https://railway.app |
| Telegram | Recibir notificaciones | https://telegram.org |
| UptimeRobot | Monitorear que el bot este activo | https://uptimerobot.com |

Solo necesitas Bybit Testnet para empezar. Las demas son opcionales o para etapas posteriores.

---

## 3. Archivos del proyecto

### Version local (Windows)

```
trading/
  ├── config.py            → tus API keys y configuracion (el unico que editas)
  ├── autobot.py           → bot principal
  ├── INICIAR_AUTOBOT.bat  → doble clic para iniciar
  ├── dashboard.html       → panel visual basico en el navegador
  └── instalar.py          → instalar dependencias (solo la primera vez)
```

### Version Railway/Replit (nube)

```
trading/
  ├── config.py            → configuracion
  ├── autobot.py           → bot principal
  ├── dashboard.py         → panel Streamlit con graficos reales
  ├── requirements.txt     → dependencias para la nube
  ├── Procfile             → instrucciones de arranque para Railway
  └── instalar.py          → para uso local
```

---

## 4. Instalacion local (Windows)

### Paso 1 — Instalar Python

1. Entra a https://python.org → descarga Python 3.10 o superior
2. Durante la instalacion marca **"Add Python to PATH"**
3. Verifica la instalacion abriendo cmd y escribiendo: `python --version`

### Paso 2 — Crear API Keys en Bybit Testnet

1. Entra a https://testnet.bybit.com
2. Registrate gratis
3. Ve a **Account → API Management → Crear nueva clave**
4. Selecciona "Claves API generadas por el sistema"
5. Nombre: `mi-bot`
6. Permisos: Lectura + Editar | Trading Unificado activado
7. Guarda el **API Key** y **Secret Key** en un lugar seguro

### Paso 3 — Configurar el bot

Abre `config.py` con el Bloc de notas y pega tus claves:

```python
API_KEY    = "tu api key aqui"
API_SECRET = "tu secret key aqui"
TESTNET    = True
```

### Paso 4 — Instalar dependencias

Abre una terminal en la carpeta del bot y ejecuta:

```
python instalar.py
```

### Paso 5 — Iniciar

Doble clic en `INICIAR_AUTOBOT.bat`

---

## 5. Configuracion completa

Todos los ajustes estan en `config.py`:

```python
# --- Bybit API ---
API_KEY    = "PEGA_TU_API_KEY_AQUI"
API_SECRET = "PEGA_TU_API_SECRET_AQUI"
TESTNET    = True   # True = practica | False = dinero real

# --- Pares a operar ---
SYMBOLS = [
    {"symbol": "BTCUSDT", "qty": "0.001"},
    # {"symbol": "ETHUSDT", "qty": "0.01"},   # descomentar para agregar
    # {"symbol": "SOLUSDT", "qty": "0.1"},
]

# --- Stop Loss por operacion ---
STOP_LOSS_PCT = 2.0   # cierra si pierde 2% | 0 = desactivado

# --- Limite de perdida diaria ---
DAILY_LOSS_LIMIT_PCT = 5.0   # detiene el bot si pierde 5% en el dia | 0 = desactivado

# --- Horario de trading ---
TRADING_HOUR_START = 9    # 9am
TRADING_HOUR_END   = 22   # 10pm
# Para operar siempre: START = 0 | END = 24

# --- Reinicio automatico ---
AUTO_RESTART       = True
AUTO_RESTART_DELAY = 30   # segundos antes de reiniciar

# --- Telegram ---
TELEGRAM_TOKEN   = ""   # dejar vacio para desactivar
TELEGRAM_CHAT_ID = ""

# --- Log en archivo ---
SAVE_LOG = True   # guarda logs en carpeta /logs
```

### Ajustes en autobot.py

```python
ATR_PERIOD     = 10     # periodo del indicador SuperTrend
ATR_MULTIPLIER = 3.0    # multiplicador (mayor = menos senales, mas seguras)
TIMEFRAME      = "D"    # "D"=diario | "60"=1hora | "15"=15min | "5"=5min
CHECK_INTERVAL = 3600   # segundos entre verificaciones (3600 = 1 hora)
```

**Recomendacion de timeframe:**

| Timeframe | Senales por mes | Seguridad | Para quien |
|-----------|----------------|-----------|------------|
| Diario (D) | 2-4 | Alta | Principiantes |
| 1 hora (60) | 20-40 | Media | Intermedio |
| 15 min (15) | 80-150 | Baja | Avanzado |

---

## 6. Como funciona SuperTrend

SuperTrend es un indicador de tendencia basado en el ATR (Average True Range).

**Calculo simplificado:**
1. Calcula el ATR (volatilidad promedio de las ultimas N velas)
2. Crea una banda superior: `HL2 + (multiplicador x ATR)`
3. Crea una banda inferior: `HL2 - (multiplicador x ATR)`
4. Si el precio cierra por encima de la banda superior → **tendencia ALCISTA**
5. Si el precio cierra por debajo de la banda inferior → **tendencia BAJISTA**

**El bot opera solo cuando cambia la tendencia**, no en cada vela.

**Parametros del grafico TradingView que coinciden con el bot:**
- ATR Period: 10
- ATR Multiplier: 3.0
- Timeframe: Daily (1D)

---

## 7. Funcionalidades incluidas

### Stop Loss automatico
- Verifica el precio actual vs precio de entrada cada ciclo
- Si la perdida supera `STOP_LOSS_PCT` → cierra la posicion automaticamente
- Envia notificacion por Telegram

### Limite de perdida diaria
- Al iniciar cada dia guarda el saldo inicial
- Si el saldo actual cae mas de `DAILY_LOSS_LIMIT_PCT` → detiene el bot
- Se reactiva automaticamente al dia siguiente

### Horario de trading
- Solo opera entre `TRADING_HOUR_START` y `TRADING_HOUR_END`
- Fuera del horario el bot sigue corriendo pero no ejecuta ordenes

### Multi-par en paralelo
- Cada par corre en un hilo separado (threading)
- Puedes agregar o quitar pares en `config.py`
- Cada par tiene su propia cantidad configurada

### Notificaciones Telegram
- Se envia mensaje cuando: bot inicia, ejecuta orden, stop loss, limite diario, bot cae
- Configuracion: `TELEGRAM_TOKEN` y `TELEGRAM_CHAT_ID` en config.py

### Log en archivo
- Guarda todos los mensajes en la carpeta `/logs`
- Un archivo por dia con formato: `2026-03-11.txt`
- Incluye nivel: INFO, WARN, ERROR, TRADE

### Auto-reinicio
- Si el bot cae por cualquier error → espera `AUTO_RESTART_DELAY` segundos → reinicia solo
- Envia notificacion por Telegram cuando se cae y cuando reinicia

### P&L en tiempo real
- Muestra el porcentaje de ganancia/perdida de la posicion abierta en cada log
- Formato: `[BTCUSDT] Precio: 69500.00 | ALCISTA | P&L: +1.23%`

---

## 8. Uso diario

### Iniciar el bot

**Windows:**
```
Doble clic en INICIAR_AUTOBOT.bat
```

**Terminal:**
```
python autobot.py
```

**Lo que veras en la terminal:**
```
[2026-03-11 09:00:01] [INFO] Bot iniciado | Modo: TESTNET | Pares: BTCUSDT | TF: Diario
[2026-03-11 09:00:01] [INFO] Horario: 9h-22h | SL: 2.0% | Limite diario: 5.0%
------------------------------------------------------------
[2026-03-11 09:00:05] [INFO] [BTCUSDT] Precio: 69635.50 | BAJISTA
[2026-03-11 09:00:05] [INFO] [BTCUSDT] Sin cambio, esperando...
[2026-03-11 09:00:05] [INFO] Ordenes hoy: 0 | Proxima verificacion en 60 min
------------------------------------------------------------
```

### Detener el bot

Presiona `Ctrl+C` en la terminal.

### Ver el panel visual

Abre `dashboard.html` en el navegador (version local) o ejecuta:
```
streamlit run dashboard.py
```

---

## 9. Dashboard Streamlit

El dashboard (`dashboard.py`) muestra en tiempo real:

- **Saldo USDT** actual en Bybit
- **Precio** del par principal
- **Grafico de velas** interactivo con Plotly (diario, ultimos 60 dias)
- **Tabla de ordenes** recientes con colores por lado (verde=buy, rojo=sell)
- **Log del dia** en tiempo real
- **Configuracion actual** del bot

**Iniciar el dashboard:**
```
streamlit run dashboard.py
```

Se abre automaticamente en: `http://localhost:8501`

**Auto-refresh:** cada 60 segundos (o click en "Actualizar ahora")

---

## 10. Deploy en Railway (24/7)

Railway corre el bot en la nube sin necesitar tu PC encendida.

### Paso 1 — Crear cuenta
1. Entra a https://railway.app
2. Registrate con GitHub (recomendado)

### Paso 2 — Nuevo proyecto
1. Click en **New Project**
2. Selecciona **Deploy from GitHub repo** o **Empty Project**
3. Si usas Empty Project: arrastra todos los archivos del ZIP

### Paso 3 — Variables de entorno (recomendado)
En lugar de poner las API keys en config.py, configuralas como variables:
1. En Railway → tu proyecto → **Variables**
2. Agrega: `API_KEY`, `API_SECRET`, `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`
3. En config.py cambia a:
```python
import os
API_KEY    = os.environ.get("API_KEY", "")
API_SECRET = os.environ.get("API_SECRET", "")
```

### Paso 4 — Deploy
Railway detecta el `Procfile` automaticamente y arranca el bot.

### Paso 5 — Monitoreo con UptimeRobot
1. Entra a https://uptimerobot.com → cuenta gratis
2. New Monitor → tipo HTTP
3. URL: la URL publica de tu Railway
4. Intervalo: 5 minutos
5. Recibes email si el bot se cae

**Costo Railway:** plan Hobby u$s5/mes. Plan gratis tiene 500hs/mes.

---

## 11. Deploy en Replit (alternativa)

### Paso 1
1. Entra a https://replit.com → cuenta gratis
2. New Repl → Python → nombre: bybit-bot
3. Sube los archivos del ZIP (arrastralos al panel izquierdo)

### Paso 2
En la terminal de Replit:
```
pip install pybit requests flask
```

### Paso 3
Pega tus API keys en config.py y click en **Run**

### Mantener activo gratis con UptimeRobot
El bot de Replit usa `keep_alive.py` que levanta un servidor en el puerto 8080.
Configura UptimeRobot para pingear esa URL cada 5 minutos.

**Diferencia con Railway:**
- Replit: gratis pero se duerme, requiere UptimeRobot
- Railway: u$s5/mes pero siempre activo y mas estable

---

## 12. Configurar Telegram

### Paso 1 — Crear el bot
1. Abre Telegram → busca **@BotFather**
2. Escribe `/newbot`
3. Ponle un nombre (ej: "Mi Bot Bybit")
4. Copia el **TOKEN** que te da (formato: `123456:ABCdef...`)

### Paso 2 — Obtener tu Chat ID
1. Busca **@userinfobot** en Telegram
2. Escribe cualquier mensaje
3. Copia el numero que aparece como **Id** (ej: `987654321`)

### Paso 3 — Configurar en config.py
```python
TELEGRAM_TOKEN   = "123456:ABCdef..."
TELEGRAM_CHAT_ID = "987654321"
```

### Mensajes que recibiras
- Bot iniciado (con modo, pares y configuracion)
- Cada orden ejecutada (par, precio, cantidad, modo)
- Stop Loss activado
- Limite diario alcanzado
- Bot caido y reiniciando
- Nuevo dia (con saldo inicial)

---

## 13. Pasar a dinero real

**Solo cuando hayas practicado en testnet y estes seguro.**

### Paso 1
1. Crea cuenta en https://bybit.com (no testnet)
2. Completa la verificacion KYC
3. Deposita fondos (minimo recomendado: u$s100)

### Paso 2 — Crear API Keys reales
1. Ve a **Account & Security → API Management**
2. Crea nueva clave con permisos: Lectura + Trading Unificado
3. Guarda las claves

### Paso 3 — Actualizar config.py
```python
API_KEY    = "tu nueva key real"
API_SECRET = "tu nuevo secret real"
TESTNET    = False
```

### Paso 4 — Ajustar cantidades
Calcula la cantidad segun tu capital:
- Capital u$s100 → qty BTC = `0.0001` (aprox u$s7 por operacion)
- Capital u$s500 → qty BTC = `0.001` (aprox u$s70 por operacion)
- Capital u$s1000 → qty BTC = `0.002` (aprox u$s140 por operacion)

**IMPORTANTE:** Empieza con cantidades pequenas. Los bots pueden perder dinero.

---

## 14. Herramientas recomendadas

### Para desarrollar el bot

| Herramienta | Para que | URL |
|-------------|----------|-----|
| **Cursor** | Editor con IA para mejorar el codigo | cursor.com |
| **Claude** | Pedir mejoras, explicaciones, bugs | claude.ai |
| **ChatGPT** | Alternativa para codigo | chatgpt.com |

### Para correr el bot

| Herramienta | Para que | Costo |
|-------------|----------|-------|
| **Railway** | Deploy 24/7, mas estable | u$s5/mes |
| **Replit** | Deploy 24/7, mas simple | Gratis (con limitaciones) |
| **PC local** | Correr en tu computadora | Gratis (requiere PC encendida) |

### Para el dashboard

| Herramienta | Para que | URL |
|-------------|----------|-----|
| **Streamlit** | Dashboard en Python, facil | streamlit.io |
| **Lovable** | Generar dashboard con IA | lovable.dev |
| **Bolt** | Alternativa para UI con IA | bolt.new |

### Para monitoreo y estrategia

| Herramienta | Para que | URL |
|-------------|----------|-----|
| **UptimeRobot** | Alertas si el bot se cae | uptimerobot.com |
| **TradingView** | Backtesting visual de SuperTrend | tradingview.com |
| **Grafana** | Dashboards avanzados | grafana.com |

---

## 15. Prompts para IA

### Para Cursor (mejorar el bot)

```
Tengo un bot de trading en Python para Bybit con estos archivos en el proyecto:
- config.py → API keys y configuracion
- autobot.py → bot principal con SuperTrend
- dashboard.py → panel Streamlit con graficos Plotly

El bot calcula SuperTrend (ATR 10, multiplicador 3.0) en timeframe diario,
opera multiples pares en paralelo, tiene stop loss (2%), limite de perdida
diaria (5%), horario de trading, Telegram, logs y auto-reinicio.

Lee todos los archivos del proyecto antes de responder.

Quiero mejorar el bot. Empeza por analizar el codigo y decirme que mejorarias primero.
```

### Para Railway

```
Tengo un bot de trading Python para Bybit con Procfile y requirements.txt.
Quiero desplegarlo en Railway corriendo 24/7.
Ayudame a configurar variables de entorno, el deploy y produccion.
```

### Para Streamlit/dashboard

```
Tengo un dashboard en dashboard.py hecho con Streamlit para monitorear
un bot de trading Bybit. Muestra velas con Plotly, tabla de ordenes y log.

Quiero agregar:
- SuperTrend dibujado sobre las velas
- P&L acumulado del dia en tiempo real  
- Boton para pausar/reanudar el bot
- Historial de trades con equity curve

Lee dashboard.py antes de responder.
```

---

## 16. Problemas comunes

| Problema | Causa | Solucion |
|----------|-------|----------|
| `ModuleNotFoundError: pybit` | Dependencias no instaladas | `python instalar.py` |
| `Error de API key` | Keys incorrectas o con espacios | Verificar config.py sin espacios |
| `No hay suficientes datos` | Bybit tarda en responder | Esperar y reiniciar |
| `Error al colocar orden` | Sin saldo en Bybit | Depositar USDT en testnet |
| `Bot no arranca` | Python no en PATH | Reinstalar Python marcando "Add to PATH" |
| `UnicodeEncodeError` | Windows con emojis | Ya corregido en la version final |
| `ngrok no responde` | Solo para version TradingView | No necesario para autobot.py |
| `Telegram no envia` | Token o Chat ID incorrecto | Verificar con @userinfobot |
| `Railway no arranca` | Procfile incorrecto | Verificar que dice: `web: python autobot.py` |

---

## 17. Proximas mejoras sugeridas

**Seguridad y riesgo:**
- Trailing stop loss (sigue el precio en la direccion favorable)
- Verificar posicion abierta en Bybit antes de cada orden (evitar duplicados)
- Tamano de orden dinamico segun % del saldo

**Funcionalidad:**
- Soporte para multiples estrategias (no solo SuperTrend)
- Modo solo BUY (para spot sin shorts)
- Backtest integrado con datos historicos de Bybit

**Notificaciones:**
- Reporte diario automatico a las 23:59 con P&L, ordenes y saldo
- Alerta cuando el precio se acerca al stop loss

**Dashboard:**
- Grafico SuperTrend dibujado sobre las velas
- Equity curve (curva de capital a lo largo del tiempo)
- Boton para pausar/reanudar el bot desde el navegador
- Historial completo de todas las operaciones

---

## 18. Seguridad

### Reglas basicas
- **Nunca** compartas tus API Keys con nadie
- **Nunca** subas config.py a GitHub
- Usa claves de **testnet** mientras practicas (no tienen valor real)
- Activa solo los permisos necesarios en las API Keys (trading, no retiros)
- Empieza con cantidades muy pequenas al pasar a real

### Si crees que tus keys fueron comprometidas
1. Ve a Bybit → API Management → Eliminar la clave afectada
2. Crea una nueva clave
3. Actualiza config.py con la nueva clave

### Variables de entorno (mejor practica para la nube)
En lugar de escribir las keys directamente en config.py, usa variables de entorno:

```python
import os
API_KEY    = os.environ.get("BYBIT_API_KEY", "")
API_SECRET = os.environ.get("BYBIT_API_SECRET", "")
```

Luego configura las variables en Railway/Replit sin tocar el codigo.

---

## RESUMEN RAPIDO

```
PRIMERA VEZ:
  1. Cuenta en testnet.bybit.com → crear API keys
  2. Pegar keys en config.py
  3. python instalar.py
  4. Doble clic en INICIAR_AUTOBOT.bat

USO DIARIO:
  1. Doble clic en INICIAR_AUTOBOT.bat
  2. Abrir dashboard.html o streamlit run dashboard.py
  3. Ctrl+C para detener

PARA LA NUBE (Railway):
  1. Subir archivos a Railway
  2. Configurar variables de entorno con las API keys
  3. Deploy automatico con Procfile
  4. Configurar UptimeRobot para monitoreo

PARA DINERO REAL:
  1. Cuenta en bybit.com (no testnet)
  2. Nuevas API keys
  3. TESTNET = False en config.py
  4. Empezar con cantidades pequenas
```

---

*Manual generado el 11 de marzo de 2026*
*Bot version: SuperTrend Multi-par con Stop Loss, Telegram, Logs, Horario y Auto-reinicio*
