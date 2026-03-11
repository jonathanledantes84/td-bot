# 🤖 Bot TradingView → Bybit — Guía Completa

## Archivos incluidos

| Archivo | Para qué sirve |
|---------|---------------|
| `instalar.py` | Instala todo automáticamente |
| `config.py` | **Tu configuración** (API keys, etc.) |
| `bot.py` | El servidor principal del bot |
| `test.py` | Prueba el bot localmente |

---

## PASO 1 — Instalar Python

Descarga Python 3.10 o superior desde https://python.org  
⚠️ Durante la instalación marca **"Add Python to PATH"**

---

## PASO 2 — Instalar dependencias

Abre una terminal en la carpeta del bot y ejecuta:
```
python instalar.py
```
Esto instala Flask, pybit y requests automáticamente.

---

## PASO 3 — Crear API Keys en Bybit

1. Entra a https://testnet.bybit.com (para practicar con dinero falso)
2. Crea una cuenta → ve a **Account & Security → API Management**
3. Crea una nueva API Key con permiso: **"Contract - Orders"**
4. Guarda el **API Key** y **Secret Key**

---

## PASO 4 — Configurar el bot

Abre `config.py` y edita:
```python
API_KEY    = "pega tu API Key aquí"
API_SECRET = "pega tu Secret Key aquí"
TESTNET    = True                        # True = práctica, False = real
WEBHOOK_SECRET = "pon cualquier contraseña"
```

---

## PASO 5 — Iniciar el bot

```
python bot.py
```
Verás: `🚀 Bot iniciado — Modo: 🟡 TESTNET`

---

## PASO 6 — Instalar y correr ngrok (internet público)

1. Descarga ngrok gratis en https://ngrok.com/download
2. En una **nueva terminal**, ejecuta:
```
ngrok http 5000
```
3. Copia la URL que aparece, ejemplo:
```
https://abc123.ngrok.io
```
Tu webhook URL será: `https://abc123.ngrok.io/webhook`

---

## PASO 7 — Configurar alerta en TradingView

1. Abre TradingView → tu gráfico o estrategia
2. Crea una alerta → pestaña **"Notifications"**
3. Activa **Webhook URL** → pega: `https://abc123.ngrok.io/webhook`
4. En el campo **Message**, pega este JSON:

```json
{
  "secret":  "pon cualquier contraseña",
  "symbol":  "{{ticker}}",
  "side":    "{{strategy.order.action}}",
  "qty":     "0.001"
}
```

> `{{strategy.order.action}}` se rellena automáticamente con "buy" o "sell" desde tu Pine Script.

---

## PASO 8 — Probar todo

Con `bot.py` corriendo, en otra terminal:
```
python test.py
```
Verás si las órdenes se ejecutan correctamente.

---

## ⚠️ Advertencias importantes

- Empieza **siempre** con `TESTNET = True`
- Nunca compartas tu API Key ni Secret Key
- Nunca subas `config.py` a GitHub
- Los bots pueden perder dinero — solo arriesga lo que puedas perder

---

## Flujo completo

```
TradingView dispara alerta
        │
        ▼
Envía JSON al webhook (ngrok URL)
        │
        ▼
bot.py recibe y valida el secret
        │
        ▼
Coloca orden en Bybit (Buy o Sell)
        │
        ▼
Bybit ejecuta la orden ✅
```
