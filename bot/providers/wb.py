from __future__ import annotations

import re
from typing import List, Optional

import httpx

from ..models import Offer
from . import Provider


_WB_LINK_ID_RE = re.compile(r"/catalog/(\d+)/detail\\.aspx", re.IGNORECASE)
_WB_NM_PARAM_RE = re.compile(r"[?&]nm=(\d+)")


class WildberriesProvider(Provider):
	name = "wildberries"

	def __init__(self, http_client: httpx.AsyncClient, app_type: int = 1, currency: str = "rub", dest: int = -1257786) -> None:
		self._http = http_client
		self._app_type = app_type
		self._currency = currency
		self._dest = dest

	def can_handle_url(self, url: str) -> bool:
		return "wildberries" in url or "wb.ru" in url

	def build_url(self, product_id: str) -> str:
		return f"https://www.wildberries.ru/catalog/{product_id}/detail.aspx"

	def _extract_id_from_url(self, url: str) -> Optional[str]:
		m = _WB_LINK_ID_RE.search(url)
		if m:
			return m.group(1)
		m = _WB_NM_PARAM_RE.search(url)
		if m:
			return m.group(1)
		return None

	async def search(self, query: str, limit: int = 10) -> List[Offer]:
		# Public search API; may change over time, kept simple here
		params = {
			"appType": str(self._app_type),
			"curr": self._currency,
			"dest": str(self._dest),
			"query": query,
			"resultset": "catalog",
			"spp": "30",
			"searchPrecise": "1",
		}
		url = "https://search.wb.ru/exactmatch/ru/common/v4/search"
		resp = await self._http.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
		resp.raise_for_status()
		data = resp.json()
		products = (data.get("data") or {}).get("products") or []
		offers: List[Offer] = []
		for p in products[:limit]:
			nm_id = str(p.get("id") or p.get("nmId") or "")
			if not nm_id:
				continue
			title = p.get("name") or p.get("brand") or "WB Item"
			price_minor = int(p.get("salePriceU") or p.get("priceU") or 0)
			offers.append(
				Offer(
					provider=self.name,
					product_id=nm_id,
					title=title,
					price_minor=price_minor,
					currency=self._currency,
					url=self.build_url(nm_id),
				)
			)
		return offers

	async def get_by_id(self, product_id: str) -> Optional[Offer]:
		params = {
			"appType": str(self._app_type),
			"curr": self._currency,
			"dest": str(self._dest),
			"nm": product_id,
		}
		url = "https://card.wb.ru/cards/detail"
		resp = await self._http.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
		resp.raise_for_status()
		data = resp.json()
		products = (data.get("data") or {}).get("products") or []
		if not products:
			return None
		p = products[0]
		title = p.get("name") or p.get("brand") or "WB Item"
		price_minor = int(p.get("salePriceU") or p.get("priceU") or 0)
		return Offer(
			provider=self.name,
			product_id=str(product_id),
			title=title,
			price_minor=price_minor,
			currency=self._currency,
			url=self.build_url(str(product_id)),
		)

	async def get_by_url(self, url: str) -> Optional[Offer]:
		product_id = self._extract_id_from_url(url)
		if not product_id:
			return None
		return await self.get_by_id(product_id)