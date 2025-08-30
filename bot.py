from __future__ import annotations

import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, PhotoSize

from app.core.aggregator import Aggregator
from app.providers.wildberries import WildberriesProvider
from app.utils.config import Settings


settings = Settings()


async def create_aggregator() -> Aggregator:
    providers = [WildberriesProvider()]
    return Aggregator(providers)


def format_offer(offer) -> str:
    return f"<b>{offer.title}</b>\n{offer.provider}: <b>{offer.price_rub:.2f} ₽</b>\n<a href=\"{offer.url}\">Открыть товар</a>"


async def on_text(message: Message, aggregator: Aggregator) -> None:
    query = message.text or message.caption or ""
    if not query.strip():
        await message.answer("Пришлите название товара или фото с подписью.")
        return

    offers = await aggregator.search_all(query, limit_per_provider=5)
    if not offers:
        await message.answer("Ничего не найдено.")
        return

    best = offers[0]
    await message.answer(format_offer(best), parse_mode=ParseMode.HTML, disable_web_page_preview=True)


async def on_photo(message: Message, aggregator: Aggregator) -> None:
    # MVP: use caption text. Image recognition can be added later.
    await on_text(message, aggregator)


async def main() -> None:
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is not set in environment or .env")

    bot = Bot(token=settings.bot_token, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    aggregator = await create_aggregator()

    dp.message.register(on_text, F.text, aggregator=aggregator)
    dp.message.register(on_photo, F.photo, aggregator=aggregator)
    dp.message.register(lambda m: m.answer("Пришлите текст или фото"))
    dp.message.register(lambda m: m.answer("/start чтобы начать"), CommandStart())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())