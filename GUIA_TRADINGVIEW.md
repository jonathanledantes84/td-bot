# GUIA: Configurar TradingView con el Bot

## Lo que necesitas tener antes de empezar
- El bot corriendo (`python lanzar.py`)
- Tu URL del webhook (ej: `https://pulplike-casimira-subarboreal.ngrok-free.dev/webhook`)

---

## OPCION A — Alerta manual (cualquier grafico)

Usa esto si queres disparar ordenes a mano o con condiciones simples.

### Pasos:

1. Abre TradingView → elige cualquier grafico (ej: BTCUSDT)

2. Haz clic en el icono de **reloj con signo +** (barra superior derecha)
   → O click derecho en el grafico → "Agregar alerta"

3. En la pestana **"Configuracion"**:
   - Condicion: lo que quieras (ej: precio cruza hacia arriba X valor)

4. Ve a la pestana **"Notificaciones"**:
   - Activa la casilla **"Webhook URL"**
   - Pega tu URL:
     ```
     https://pulplike-casimira-subarboreal.ngrok-free.dev/webhook
     ```

5. En el campo **"Mensaje"** pega exactamente esto:
   ```json
   {
     "secret": "Julit@2018!@@@",
     "symbol": "BTCUSDT",
     "side":   "buy",
     "qty":    "0.001"
   }
   ```
   > Cambia "buy" por "sell" segun lo que necesites.

6. Haz clic en **"Crear"**

---

## OPCION B — Estrategia Pine Script (automatico)

Usa esto si tenes o usas una estrategia en Pine Script que genera senales de compra/venta automaticamente.

### Pasos:

1. Abre TradingView → agrega una estrategia al grafico
   - En "Indicadores" busca cualquier estrategia (ej: "SuperTrend Strategy")
   - O pega tu propio Pine Script en el Editor de Pine

2. Con la estrategia cargada, haz clic en el **icono de reloj +** para crear alerta

3. En **"Configuracion"**:
   - Condicion: selecciona el nombre de tu estrategia
   - Orden: "Order fills only" (solo cuando se ejecuta una orden)

4. En **"Notificaciones"**:
   - Activa **"Webhook URL"** y pega tu URL

5. En **"Mensaje"** pega esto:
   ```json
   {
     "secret": "Julit@2018!@@@",
     "symbol": "{{ticker}}",
     "side":   "{{strategy.order.action}}",
     "qty":    "0.001"
   }
   ```
   > `{{ticker}}` y `{{strategy.order.action}}` se rellenan automaticamente.
   > "buy" o "sell" lo decide la estrategia sola.

6. Haz clic en **"Crear"**

---

## Verificar que funciona

Cuando TradingView dispare la alerta:

1. En la terminal donde corre el bot veras:
   ```
   Alerta recibida: {'secret': '...', 'symbol': 'BTCUSDT', 'side': 'buy', ...}
   [OK] Orden ejecutada: Buy 0.001 BTCUSDT | ID: xxxxxxxx
   ```

2. En el monitor ngrok (`http://localhost:4040`) veras la peticion POST en verde.

3. En Bybit Testnet → **Ordenes** podras ver la orden ejecutada.

---

## Problemas comunes

| Problema | Solucion |
|----------|----------|
| No llega la alerta | Verifica que el bot esta corriendo y ngrok esta activo |
| Error 403 | La clave "secret" en TradingView no coincide con config.py |
| Error de orden | Verifica que tienes saldo en Bybit Testnet |
| URL no funciona | Cada vez que reinicias ngrok cambia la URL — actualizala en TradingView |

---

## Recuerda

- Cada vez que reinicias el bot, la URL de ngrok **cambia**.
  Tendras que actualizar la alerta en TradingView con la nueva URL.
- Para evitar esto, podes comprar un dominio estatico en ngrok (plan pago).
- Cuando estes listo para dinero real: cambia `TESTNET = False` en `config.py`
  y usa las API keys de bybit.com (no testnet).
