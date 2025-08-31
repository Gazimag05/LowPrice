import asyncio
import sys
from contextlib import asynccontextmanager

import uvloop  # type: ignore
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
import httpx

from .config import load_config, Config
from .handlers.common import router as common_router, init_dependencies
from .providers.wb import WildberriesProvider
from .services.aggregator import Aggregator


@asynccontextmanager
async def lifespan(bot: Bot):
	# Placeholder if you want to manage resources tied to bot lifecycle
	yield


async def main() -> None:
	# Use uvloop when available
	try:
		uvloop.install()
	except Exception:
		pass

	config: Config = load_config()
	if not config.bot_token:
		print("BOT_TOKEN is not set in environment (.env)")
		sys.exit(1)

	# HTTP client shared across providers
	http_client = httpx.AsyncClient(timeout=httpx.Timeout(15.0, connect=10.0))

	# Providers (start with Wildberries; add more providers here)
	wb_provider = WildberriesProvider(
		http_client=http_client,
		app_type=config.wb_app_type,
		currency=config.wb_currency,
		dest=config.wb_dest,
	)
	providers = [wb_provider]

	aggregator = Aggregator(providers=providers)

	bot = Bot(token=config.bot_token, parse_mode=ParseMode.HTML)
	dp = Dispatcher()

	# Init router dependencies and include routers
	init_dependencies(aggregator=aggregator, config=config)
	dp.include_router(common_router)

	try:
		await dp.start_polling(bot)
	finally:
		await http_client.aclose()


if __name__ == "__main__":
	asyncio.run(main())