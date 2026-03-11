# 🤖 TradingView → Bybit Webhook Bot

A beginner-friendly trading bot that executes orders on Bybit when your TradingView strategy fires an alert.

---

## 📋 How It Works

```
TradingView Alert ──► Your Server (bot.py) ──► Bybit Order
```

---

## 🚀 Step-by-Step Setup

### Step 1 — Install Python
Download Python from https://python.org (version 3.10 or higher).

### Step 2 — Install dependencies
Open a terminal in this folder and run:
```bash
pip install -r requirements.txt
```

### Step 3 — Get your Bybit API keys
1. Create a free account at https://bybit.com
2. Go to **Account & Security → API Management**
3. Create a new API key with **"Contract - Orders"** permission enabled
4. Copy your **API Key** and **Secret Key**

### Step 4 — Configure bot.py
Open `bot.py` and fill in:
```python
API_KEY        = "paste your API key here"
API_SECRET     = "paste your secret key here"
TESTNET        = True           # Keep True until you're ready for real money!
WEBHOOK_SECRET = "pick any password"  # You'll use this in TradingView too
```

### Step 5 — Run the bot
```bash
python bot.py
```
You should see: `🚀 Trading bot starting...`

### Step 6 — Expose your bot to the internet
TradingView needs a public URL to send alerts to. Use **ngrok** (free):
1. Download from https://ngrok.com
2. Run: `ngrok http 5000`
3. Copy the URL it gives you, e.g. `https://abc123.ngrok.io`

Your webhook URL will be: `https://abc123.ngrok.io/webhook`

### Step 7 — Set up TradingView Alert
1. Open your chart/strategy in TradingView
2. Create an alert → go to **"Notifications"** tab
3. Enable **Webhook URL** and paste your URL: `https://abc123.ngrok.io/webhook`
4. In the **Alert Message** box, paste this JSON (edit as needed):

```json
{
  "secret": "pick any password",
  "symbol": "BTCUSDT",
  "side": "{{strategy.order.action}}",
  "qty": "0.001"
}
```

> 💡 `{{strategy.order.action}}` auto-fills "buy" or "sell" from your Pine Script strategy.

---

## ✅ Test It First!

Keep `TESTNET = True` and use Bybit Testnet (https://testnet.bybit.com) to test with fake money before going live.

You can also test manually using curl:
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"secret":"pick any password","symbol":"BTCUSDT","side":"Buy","qty":"0.001"}'
```

---

## ⚠️ Important Warnings

- **Never share your API keys with anyone**
- **Never commit API keys to GitHub**
- **Always test on Testnet first**
- Trading bots can lose money — only risk what you can afford to lose
- This bot uses **Market orders** by default (fills instantly at current price)

---

## 📁 Files

| File | Purpose |
|------|---------|
| `bot.py` | Main bot server |
| `requirements.txt` | Python packages needed |
| `README.md` | This guide |
