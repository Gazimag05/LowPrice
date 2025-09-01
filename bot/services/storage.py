from __future__ import annotations

import aiosqlite
from typing import List, Tuple

from ..models import TrackItem


class Storage:
	def __init__(self, db_path: str) -> None:
		self._db_path = db_path
		self._db: aiosqlite.Connection | None = None

	async def init(self) -> None:
		self._db = await aiosqlite.connect(self._db_path)
		self._db.row_factory = aiosqlite.Row
		await self._db.execute(
			"""
			CREATE TABLE IF NOT EXISTS tracks (
				chat_id INTEGER NOT NULL,
				provider TEXT NOT NULL,
				product_id TEXT NOT NULL,
				url TEXT NOT NULL,
				title TEXT NOT NULL,
				last_price_minor INTEGER NOT NULL,
				currency TEXT NOT NULL,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				PRIMARY KEY (chat_id, provider, product_id)
			);
			"""
		)
		await self._db.commit()

	async def close(self) -> None:
		if self._db is not None:
			await self._db.close()
			self._db = None

	async def add_track(self, item: TrackItem) -> None:
		assert self._db is not None
		await self._db.execute(
			"""
			INSERT OR REPLACE INTO tracks(chat_id, provider, product_id, url, title, last_price_minor, currency)
			VALUES (?, ?, ?, ?, ?, ?, ?)
			""",
			(item.chat_id, item.provider, item.product_id, item.url, item.title, item.last_price_minor, item.currency),
		)
		await self._db.commit()

	async def remove_track(self, chat_id: int, provider: str, product_id: str) -> None:
		assert self._db is not None
		await self._db.execute(
			"DELETE FROM tracks WHERE chat_id = ? AND provider = ? AND product_id = ?",
			(chat_id, provider, product_id),
		)
		await self._db.commit()

	async def list_tracks(self, chat_id: int) -> List[TrackItem]:
		assert self._db is not None
		cur = await self._db.execute(
			"SELECT chat_id, provider, product_id, url, title, last_price_minor, currency FROM tracks WHERE chat_id = ? ORDER BY created_at DESC",
			(chat_id,),
		)
		rows = await cur.fetchall()
		return [
			TrackItem(
				chat_id=row["chat_id"],
				provider=row["provider"],
				product_id=row["product_id"],
				url=row["url"],
				title=row["title"],
				last_price_minor=row["last_price_minor"],
				currency=row["currency"],
			)
			for row in rows
		]

	async def get_all_tracks(self) -> List[TrackItem]:
		assert self._db is not None
		cur = await self._db.execute(
			"SELECT chat_id, provider, product_id, url, title, last_price_minor, currency FROM tracks",
		)
		rows = await cur.fetchall()
		return [
			TrackItem(
				chat_id=row["chat_id"],
				provider=row["provider"],
				product_id=row["product_id"],
				url=row["url"],
				title=row["title"],
				last_price_minor=row["last_price_minor"],
				currency=row["currency"],
			)
			for row in rows
		]

	async def update_last_price(self, chat_id: int, provider: str, product_id: str, price_minor: int) -> None:
		assert self._db is not None
		await self._db.execute(
			"UPDATE tracks SET last_price_minor = ? WHERE chat_id = ? AND provider = ? AND product_id = ?",
			(price_minor, chat_id, provider, product_id),
		)
		await self._db.commit()