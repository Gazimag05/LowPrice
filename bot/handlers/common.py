from __future__ import annotations

import re
from typing import Optional

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from ..config import Config
from ..models import Offer, TrackItem
from ..services.aggregator import Aggregator
from ..services.storage import Storage

router = Router()

# Dependencies (set at startup)
_aggregator: Aggregator | None = None
_storage: Storage | None = None
_config: Config | None = None


def init_dependencies(aggregator: Aggregator, storage: Storage, config: Config) -> None:
	global _aggregator, _storage, _config
	_aggregator = aggregator
	_storage = storage
	_config = config


_LINK_RE = re.compile(r"https?://[^\s]+", re.IGNORECASE)


def _is_allowed(message: Message) -> bool:
	if _config and _config.allowed_chats:
		return message.chat.id in _config.allowed_chats
	return True


def _offer_text(o: Offer) -> str:
	return (
		f"<b>{o.title}</b>\n"
		f"{o.price_minor / 100:.2f} {o.currency}\n"
		f"{o.url}"
	)


def _track_kb(o: Offer) -> InlineKeyboardMarkup:
	cb = f"t|{o.provider}|{o.product_id}"
	return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔔 Отслеживать", callback_data=cb)]])


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
	if not _is_allowed(message):
		await message.answer("Доступ к боту ограничен.")
		return
	await message.answer(
		"Отправьте запрос (название товара) или ссылку на карточку товара.\n"
		"Поддерживается: Wildberries. Нажмите 'Отслеживать' для уведомлений о снижении цены.\n"
		"Команды: /list — список отслеживаемых, /untrack provider product_id — удалить."
	)


@router.message(Command("list"))
async def cmd_list(message: Message) -> None:
	if not _is_allowed(message):
		return
	if _storage is None:
		await message.answer("Внутренняя ошибка")
		return
	items = await _storage.list_tracks(message.chat.id)
	if not items:
		await message.answer("Список пуст.")
		return
	lines = []
	for idx, it in enumerate(items, start=1):
		lines.append(
			f"{idx}. [{it.provider}] {it.title} — {it.last_price_minor / 100:.2f} {it.currency}\n{it.url}"
		)
	await message.answer("\n\n".join(lines))


@router.message(Command("untrack"))
async def cmd_untrack(message: Message) -> None:
	if not _is_allowed(message):
		return
	if _storage is None:
		await message.answer("Внутренняя ошибка")
		return
	args = (message.text or "").split()
	if len(args) < 3:
		await message.answer("Использование: /untrack provider product_id")
		return
	provider, product_id = args[1], args[2]
	await _storage.remove_track(message.chat.id, provider, product_id)
	await message.answer("Удалено (если было в списке).")


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
			await message.answer(_offer_text(offer), reply_markup=_track_kb(offer))
			return
		# fallthrough to search
	if _aggregator:
		offers = await _aggregator.search(text, limit_per_provider=5)
		if not offers:
			await message.answer("Ничего не нашлось.")
			return
		for off in offers[:5]:
			await message.answer(_offer_text(off), reply_markup=_track_kb(off))


@router.callback_query(F.data.startswith("t|"))
async def on_track(cb: CallbackQuery) -> None:
	if cb.message is None:
		await cb.answer()
		return
	if not _is_allowed(cb.message):
		await cb.answer("Нет доступа", show_alert=True)
		return
	if _storage is None:
		await cb.answer("Внутренняя ошибка", show_alert=True)
		return
	parts = (cb.data or "").split("|")
	if len(parts) != 3:
		await cb.answer()
		return
	_, provider, product_id = parts
	# Retrieve fresh offer to store current price
	offer: Offer | None = None
	if _aggregator:
		# Try specific provider resolution when possible
		from ..providers.wb import WildberriesProvider
		if provider == WildberriesProvider.name:
			wb = next((p for p in getattr(_aggregator, "_providers", []) if isinstance(p, WildberriesProvider)), None)
			if wb:
				offer = await wb.get_by_id(product_id)
	if not offer:
		await cb.answer("Не удалось получить товар", show_alert=True)
		return
	item = TrackItem(
		chat_id=cb.message.chat.id,
		provider=offer.provider,
		product_id=offer.product_id,
		url=offer.url,
		title=offer.title,
		last_price_minor=offer.price_minor,
		currency=offer.currency,
	)
	await _storage.add_track(item)
	await cb.answer("Товар отслеживается ✅")