from __future__ import annotations

import asyncio
from typing import Dict

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ..models import TrackItem
from ..providers import Provider
from .storage import Storage


class Tracker:
	def __init__(self, bot: Bot, storage: Storage, providers: Dict[str, Provider], interval_seconds: int = 900) -> None:
		self._bot = bot
		self._storage = storage
		self._providers = providers
		self._interval_seconds = interval_seconds
		self._scheduler = AsyncIOScheduler()

	async def start(self) -> None:
		self._scheduler.add_job(self._tick, "interval", seconds=self._interval_seconds, id="price_tick", max_instances=1, coalesce=True)
		self._scheduler.start()

	async def stop(self) -> None:
		if self._scheduler.running:
			self._scheduler.shutdown(wait=False)

	async def _tick(self) -> None:
		tracks = await self._storage.get_all_tracks()
		for item in tracks:
			provider = self._providers.get(item.provider)
			if not provider:
				continue
			try:
				offer = await provider.get_by_id(item.product_id)
			except Exception:
				offer = None
			if not offer:
				continue
			if offer.price_minor < item.last_price_minor:
				try:
					await self._bot.send_message(
						item.chat_id,
						f"Цена снизилась: <b>{offer.title}</b>\n"
						f"Было: {item.last_price_minor / 100:.2f} {item.currency} → Стало: {offer.price_minor / 100:.2f} {offer.currency}\n"
						f"{offer.url}",
					)
				except Exception:
					pass
				await self._storage.update_last_price(item.chat_id, item.provider, item.product_id, offer.price_minor)