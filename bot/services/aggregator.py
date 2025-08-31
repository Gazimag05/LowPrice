from __future__ import annotations

import asyncio
from typing import List, Optional
import logging

from ..models import Offer
from ..providers import Provider


logger = logging.getLogger(__name__)


class Aggregator:
	def __init__(self, providers: List[Provider]) -> None:
		self._providers = providers

	async def search(self, query: str, limit_per_provider: int = 5) -> List[Offer]:
		async def _search_one(p: Provider) -> List[Offer]:
			try:
				offers = await p.search(query, limit=limit_per_provider)
				logger.info("Provider %s returned %d offers for query '%s'", getattr(p, 'name', p.__class__.__name__), len(offers), query)
				return offers
			except Exception as e:
				logger.exception("Provider %s failed for query '%s': %s", getattr(p, 'name', p.__class__.__name__), query, e)
				return []

		results = await asyncio.gather(*[_search_one(p) for p in self._providers])
		# Flatten and naive grouping; in real world, deduplicate by normalized title or GTIN
		offers: List[Offer] = [o for lst in results for o in lst]
		logger.info("Aggregator total offers: %d for query '%s'", len(offers), query)
		return offers

	async def get_by_url(self, url: str) -> Optional[Offer]:
		for p in self._providers:
			if p.can_handle_url(url):
				try:
					if hasattr(p, "get_by_url"):
						return await getattr(p, "get_by_url")(url)
					return None
				except Exception as e:
					logger.exception("Provider %s failed for url '%s': %s", getattr(p, 'name', p.__class__.__name__), url, e)
					return None
		return None