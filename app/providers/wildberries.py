from __future__ import annotations

import asyncio
from typing import List, Optional
from urllib.parse import urlencode

from app.models import Offer, SearchQuery
from app.utils.http import get_json


_WB_SEARCH_URL_V5 = "https://search.wb.ru/exactmatch/ru/common/v5/search"


class WildberriesProvider:
    name = "Wildberries"

    async def search(self, query: SearchQuery, *, limit: int = 5) -> List[Offer]:
        params = {
            "appType": 1,
            "curr": "rub",
            "dest": -1257786,
            "page": 1,
            "query": query.text,
            "limit": max(1, min(limit, 50)),
            "resultset": "catalog",
        }

        try:
            data = await get_json(_WB_SEARCH_URL_V5, params=params, timeout_seconds=6.0)
        except Exception:
            return []

        products = (data or {}).get("data", {}).get("products", [])
        offers: List[Offer] = []
        for product in products:
            try:
                product_id = product.get("id")
                title = product.get("name") or ""
                sale_price_kopecks: Optional[int] = product.get("salePriceU")
                if sale_price_kopecks is None:
                    sale_price_kopecks = product.get("priceU")
                if sale_price_kopecks is None:
                    continue
                price_rub = float(sale_price_kopecks) / 100.0
                url = f"https://www.wildberries.ru/catalog/{product_id}/detail.aspx"

                offers.append(
                    Offer(
                        provider=self.name,
                        title=title,
                        price_rub=price_rub,
                        url=url,
                        image_url=None,
                    )
                )
            except Exception:
                continue

        return offers