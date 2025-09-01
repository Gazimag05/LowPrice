## Telegram Price Compare Bot (Yolo-like)

Features:
- Compare prices for a product across providers (starting with Wildberries)
- Send a product link or text query; bot shows the cheapest offers

### Setup

1) Create and fill `.env` from `.env.example` (set `BOT_TOKEN`).
2) Install deps:
```bash
pip3 install -r requirements.txt
```
3) Run bot:
```bash
python3 -m bot
```

### Commands
- /start — help and usage
- Send text query or a marketplace link; bot replies with cheapest options

### Providers
- Wildberries: uses public endpoints for search and product details
- Architecture allows adding Ozon, Yandex.Market, etc.

### Docker
```bash
docker build -t pricebot .
docker run --env-file .env pricebot
```