# Deploy en Streamlit Cloud (GRATIS)

## Paso 1 — Subir archivos al repo GitHub

Subí estos archivos a tu repo `td-bot`:
- `dashboard.py`
- `requirements.txt`
- `.streamlit/config.toml` (carpeta nueva)

## Paso 2 — Crear cuenta en Streamlit Cloud

1. Andá a **share.streamlit.io**
2. Iniciá sesión con tu cuenta de GitHub
3. Hacé clic en **"New app"**
4. Elegí tu repo: `jonathanledantes84/td-bot`
5. Branch: `main`
6. Main file: `dashboard.py`
7. Hacé clic en **"Deploy"**

## Paso 3 — Agregar API Keys como Secrets

⚠️ No pongas las keys en config.py cuando uses Streamlit Cloud

1. En tu app desplegada → **Settings** (⚙️) → **Secrets**
2. Pegá esto y completá con tus keys:

```toml
API_KEY = "tu_api_key_de_bybit"
API_SECRET = "tu_api_secret_de_bybit"
TESTNET = "true"
TELEGRAM_TOKEN = ""
TELEGRAM_CHAT_ID = ""
```

## Paso 4 — Listo

Tu dashboard va a estar disponible en:
`https://tu-usuario-td-bot-dashboard-XXXXX.streamlit.app`

Lo podés abrir desde el celular también 📱

## Nota sobre el bot automático

El dashboard y el bot automático (GitHub Actions) son independientes:
- **Dashboard** = ver + operar manualmente (Streamlit Cloud)
- **Bot automático** = opera solo cada hora (GitHub Actions)

Los dos usan las mismas API keys de Bybit y funcionan al mismo tiempo.
