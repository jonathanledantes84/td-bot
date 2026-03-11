# GUIA FINAL — SuperTrend Bot para Bybit

## LO QUE NECESITAS

- Python instalado (https://python.org)
- Cuenta en Bybit Testnet (https://testnet.bybit.com)
- Los archivos del bot en una carpeta

---

## PRIMERA VEZ (solo una vez)

### 1. Crear cuenta en Bybit Testnet
1. Entra a https://testnet.bybit.com
2. Registrate gratis
3. Ve a Account → API Management → Crear nueva clave
4. Selecciona "Claves API generadas por el sistema"
5. Nombre: mi-bot | Permisos: Lectura-Editar | Trading Unificado activado
6. Guarda el API Key y Secret Key

### 2. Pegar tus claves en config.py
Abre config.py con el Bloc de notas y edita:

   API_KEY    = "tu api key aqui"
   API_SECRET = "tu secret key aqui"
   TESTNET    = True

Guarda el archivo.

### 3. Instalar dependencias
Abre una terminal en la carpeta del bot y ejecuta:

   python instalar.py

---

## USO DIARIO

### Iniciar el bot
Doble clic en:   INICIAR_AUTOBOT.bat

Veras en la terminal:
   [23:00:01] Bot SuperTrend iniciado | Modo: TESTNET | BTCUSDT
   [23:01:01] Precio: 69982.00 | Tendencia: ALCISTA (BUY)
   [23:02:01] Sin cambio de tendencia, esperando...
   [23:03:01] [SENAL] Cambio a ALCISTA -> BUY
   [23:03:01] [OK] Orden ejecutada: Buy 0.001 BTCUSDT | ID: xxxxx

### Ver el panel visual
Doble clic en:   dashboard.html
(abre en el navegador, muestra saldo, ordenes y tendencia)

### Detener el bot
Presiona Ctrl+C en la terminal

---

## COMO FUNCIONA EL BOT

1. Cada 60 segundos descarga las ultimas velas de BTCUSDT de Bybit
2. Calcula el indicador SuperTrend (ATR 10, Multiplicador 3.0)
3. Si la tendencia cambia de BAJISTA a ALCISTA → ejecuta BUY
4. Si la tendencia cambia de ALCISTA a BAJISTA → ejecuta SELL
5. Si no hay cambio → espera 60 segundos y vuelve a verificar

---

## AJUSTES EN CONFIG.PY

   DEFAULT_SYMBOL   = "BTCUSDT"   # par de trading (ej: ETHUSDT, SOLUSDT)
   DEFAULT_QTY      = "0.001"     # cantidad por orden
   DEFAULT_LEVERAGE = 1           # apalancamiento (1 = sin apalancamiento)
   TESTNET          = True        # True=practica | False=dinero real

En autobot.py tambien podes ajustar:

   ATR_PERIOD     = 10     # periodo del indicador
   ATR_MULTIPLIER = 3.0    # sensibilidad (menor = mas senales)
   TIMEFRAME      = "60"   # velas de 1 hora (usar "15" para 15min)
   CHECK_INTERVAL = 60     # segundos entre cada verificacion

---

## CUANDO ESTE LISTO PARA DINERO REAL

1. Crea una cuenta en https://bybit.com (no testnet)
2. Crea nuevas API keys ahi
3. En config.py cambia:
      API_KEY    = "nueva key real"
      API_SECRET = "nuevo secret real"
      TESTNET    = False
4. Ajusta DEFAULT_QTY segun tu capital disponible

IMPORTANTE: Empieza con cantidades pequenas. Los bots pueden perder dinero.

---

## PROBLEMAS COMUNES

Problema: "No hay suficientes datos"
Solucion: Espera un momento, Bybit puede tardar en responder

Problema: "Error al colocar orden"
Solucion: Verifica que tienes saldo en Bybit Testnet
          (Puedes obtener USDT de prueba en la seccion Activos de testnet)

Problema: El bot no arranca
Solucion: Ejecuta primero:  python instalar.py

Problema: Error de API key
Solucion: Verifica que las keys en config.py son correctas y no tienen espacios

---

## ARCHIVOS IMPORTANTES

   config.py            → tus claves y configuracion (el unico que editas)
   autobot.py           → el bot (no tocar)
   dashboard.html       → panel visual (abrir en navegador)
   INICIAR_AUTOBOT.bat  → doble clic para iniciar
   instalar.py          → instalar dependencias (solo la primera vez)

---

Recordatorio: Este bot opera en TESTNET por defecto.
Nunca arriesges dinero que no puedas perder.
