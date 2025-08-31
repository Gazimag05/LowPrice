## Telegram Price Compare Bot (Yolo-like)

Features:
- Search products and compare prices across providers (starting with Wildberries)
- Send a product link to get current price and title
- Track items and receive price drop alerts

### Setup

1) Create and fill `.env` from `.env.example` (set `BOT_TOKEN`).
2) Install deps:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
3) Run bot:
```bash
python -m bot
```

### Commands
- /start — help and usage
- Send text query or a marketplace link
- "Track" button to track an item, /list to list, /untrack to stop

### Providers
- Wildberries: uses public endpoints for search and product details
- Architecture allows adding Ozon, Yandex.Market, etc.

### Docker
```bash
docker build -t pricebot .
docker run --env-file .env pricebot
```