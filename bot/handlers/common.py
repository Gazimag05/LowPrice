from __future__ import annotations

import re
from typing import Optional, List

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from ..config import Config
from ..models import Offer
from ..services.aggregator import Aggregator

router = Router()

# Dependencies (set at startup)
_aggregator: Aggregator | None = None
_config: Config | None = None


def init_dependencies(aggregator: Aggregator, config: Config) -> None:
	global _aggregator, _config
	_aggregator = aggregator
	_config = config


_LINK_RE = re.compile(r"https?://[^\s]+", re.IGNORECASE)


def _is_allowed(message: Message) -> bool:
	if _config and _config.allowed_chats:
		return message.chat.id in _config.allowed_chats
	return True


def _offer_text(o: Offer) -> str:
	return (
		f"[{o.provider}] <b>{o.title}</b>\n"
		f"{o.price_minor / 100:.2f} {o.currency}\n"
		f"{o.url}"
	)


def _render_cheapest(offers: List[Offer], limit: int = 5) -> str:
	if not offers:
		return "Ничего не нашлось."
	sorted_offers = sorted(offers, key=lambda x: x.price_minor)
	lines = []
	for idx, o in enumerate(sorted_offers[:limit], start=1):
		lines.append(f"{idx}. {o.price_minor / 100:.2f} {o.currency} — {o.title} (#{o.provider})\n{o.url}")
	return "\n\n".join(lines)


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
	if not _is_allowed(message):
		await message.answer("Доступ к боту ограничен.")
		return
	await message.answer(
		"Отправьте запрос (название товара) или ссылку на карточку товара.\n"
		"Бот сравнивает цены на разных площадках и показывает самые дешёвые предложения."
	)


@router.message(F.text)
async def on_text(message: Message) -> None:
	if not _is_allowed(message):
		return
	text = message.text or ""
	m = _LINK_RE.search(text)
	if m and _aggregator:
		url = m.group(0)
		offer = await _aggregator.get_by_url(url)
		if offer:
			await message.answer(_offer_text(offer))
			return
		# fallthrough to search
	if _aggregator:
		offers = await _aggregator.search(text, limit_per_provider=5)
		if not offers:
			await message.answer("Ничего не нашлось.")
			return
		await message.answer(_render_cheapest(offers, limit=5))