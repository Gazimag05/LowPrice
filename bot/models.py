from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class Offer:
	provider: str
	product_id: str
	title: str
	price_minor: int  # price in minor units (e.g., kopecks)
	currency: str
	url: str

	@property
	def price(self) -> float:
		return self.price_minor / 100.0


@dataclass
class SearchResult:
	offers: List[Offer]


@dataclass
class TrackItem:
	chat_id: int
	provider: str
	product_id: str
	url: str
	title: str
	last_price_minor: int
	currency: str