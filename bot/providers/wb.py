from __future__ import annotations

import re
from typing import List, Optional

import httpx
import logging

from ..models import Offer
from . import Provider


logger = logging.getLogger(__name__)

_WB_LINK_ID_RE = re.compile(r"/catalog/(\d+)/detail\\.aspx", re.IGNORECASE)
_WB_NM_PARAM_RE = re.compile(r"[?&]nm=(\d+)")

_DEFAULT_HEADERS = {
	"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36",
	"Accept": "application/json, text/plain, */*",
	"Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
	"Origin": "https://www.wildberries.ru",
	"Referer": "https://www.wildberries.ru/",
}

# Broad regions/stores list improves WB API responses from various IPs
_REGIONS = "80,64,38,4,33,70,82,86,75,30,31,22,66,68,69,48,1,105,114"
_STORES = "117501,117986,173086,120602,4013,686,132043,507,3158,6158"


class WildberriesProvider(Provider):
	name = "wildberries"

	def __init__(self, http_client: httpx.AsyncClient, app_type: int = 1, currency: str = "rub", dest: int = -1257786) -> None:
		self._http = http_client
		self._app_type = app_type
		self._currency = currency
		self._dest = dest

	def can_handle_url(self, url: str) -> bool:
		return "wildberries.ru" in url or "wildberries" in url or "wb.ru" in url

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

	async def _fetch_search(self, base_url: str, params: dict) -> List[Offer]:
		resp = await self._http.get(base_url, params=params, headers=_DEFAULT_HEADERS)
		ct = resp.headers.get("content-type", "")
		logger.info("WB search GET %s -> %s (%s)", resp.url, resp.status_code, ct)
		resp.raise_for_status()
		data = resp.json()
		products = (data.get("data") or {}).get("products") or []
		offers: List[Offer] = []
		for p in products:
			nm_id = str(p.get("id") or p.get("nmId") or "")
			if not nm_id:
				continue
			title = (p.get("name") or p.get("brand") or "WB Item").strip()
			price_minor = int(p.get("salePriceU") or p.get("priceU") or 0)
			if price_minor <= 0:
				continue
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

	async def search(self, query: str, limit: int = 10) -> List[Offer]:
		q = (query or "").strip()
		if len(q) < 2:
			return []
		params = {
			"appType": str(self._app_type),
			"curr": self._currency,
			"dest": str(self._dest),
			"regions": _REGIONS,
			"stores": _STORES,
			"query": q,
			"resultset": "catalog",
			"spp": "30",
			"searchPrecise": "1",
			"page": "1",
			"limit": str(max(10, limit * 10)),
			"sort": "priceup",
		}
		urls = [
			"https://search.wb.ru/exactmatch/ru/common/v6/search",
			"https://search.wb.ru/exactmatch/ru/common/v5/search",
			"https://search.wb.ru/exactmatch/ru/common/v4/search",
		]
		all_offers: List[Offer] = []
		for u in urls:
			try:
				offs = await self._fetch_search(u, params)
				logger.info("WB search at %s returned %d items for query '%s'", u, len(offs), q)
				all_offers.extend(offs)
			except Exception as e:
				logger.warning("WB search failed at %s: %s", u, e)
		if not all_offers:
			return []
		uniq: dict[str, Offer] = {}
		for o in all_offers:
			prev = uniq.get(o.product_id)
			if prev is None or o.price_minor < prev.price_minor:
				uniq[o.product_id] = o
		result = sorted(uniq.values(), key=lambda x: x.price_minor)[:limit]
		return result

	async def get_by_id(self, product_id: str) -> Optional[Offer]:
		params = {
			"appType": str(self._app_type),
			"curr": self._currency,
			"dest": str(self._dest),
			"regions": _REGIONS,
			"stores": _STORES,
			"spp": "30",
			"nm": product_id,
		}
		url = "https://card.wb.ru/cards/v2/detail"
		resp = await self._http.get(url, params=params, headers=_DEFAULT_HEADERS)
		ct = resp.headers.get("content-type", "")
		logger.info("WB detail GET %s -> %s (%s)", resp.url, resp.status_code, ct)
		if resp.status_code != 200:
			return None
		try:
			data = resp.json()
		except Exception:
			return None
		products = (data.get("data") or {}).get("products") or []
		if not products:
			return None
		p = products[0]
		title = (p.get("name") or p.get("brand") or "WB Item").strip()
		price_minor = int(p.get("salePriceU") or p.get("priceU") or 0)
		if price_minor <= 0:
			return None
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