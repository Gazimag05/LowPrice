# Marketplace Price Aggregator Bot (MVP)

Minimum viable product for a Telegram bot that finds the lowest price across marketplaces.

Currently implemented provider(s):
- Wildberries (public search API)

Planned providers: Ozon, Yandex Market, Sber/Megamarket, Lamoda, Magnit.

## Requirements
- Python 3.10+

## Setup
1. Create virtualenv (optional) and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create `.env` and set your Telegram token:
```bash
cp .env.example .env
# then edit .env and set BOT_TOKEN=...
```

3. Test search via CLI:
```bash
python cli.py "iphone 14"
```

4. Run Telegram bot:
```bash
python bot.py
```

## Environment
- BOT_TOKEN: Telegram bot token
- REQUEST_TIMEOUT_SECONDS: per-request timeout (default 8.0)
- HTTP_USER_AGENT: custom User-Agent string

## Notes
- Image queries are stubbed in MVP: photo caption is used as the query. Real visual search can be added with OCR/CLIP later.
- For production, add more providers, caching, rate limiting, and monitoring.