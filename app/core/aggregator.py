from __future__ import annotations

import asyncio
from typing import Iterable, List, Sequence

from app.models import Offer, SearchQuery
from app.providers.base import Provider


class Aggregator:
    def __init__(self, providers: Sequence[Provider]) -> None:
        self._providers: List[Provider] = list(providers)

    async def search_all(self, query_text: str, *, limit_per_provider: int = 5, timeout_seconds: float = 8.0) -> List[Offer]:
        query = SearchQuery(text=query_text.strip())
        if not query.text:
            return []

        async def _safe_provider_call(provider: Provider) -> List[Offer]:
            try:
                return await asyncio.wait_for(provider.search(query, limit=limit_per_provider), timeout=timeout_seconds)
            except Exception:
                return []

        results = await asyncio.gather(*[_safe_provider_call(p) for p in self._providers])
        offers = [offer for provider_offers in results for offer in provider_offers]
        offers.sort(key=lambda o: o.price_rub)
        return offers

    async def search_best(self, query_text: str, *, timeout_seconds: float = 8.0) -> Offer | None:
        offers = await self.search_all(query_text, limit_per_provider=3, timeout_seconds=timeout_seconds)
        return offers[0] if offers else None