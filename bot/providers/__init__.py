from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Optional, List

from ..models import Offer


class Provider(ABC):
	name: str

	@abstractmethod
	def can_handle_url(self, url: str) -> bool:  # pragma: no cover
		...

	@abstractmethod
	async def search(self, query: str, limit: int = 10) -> List[Offer]:  # pragma: no cover
		...

	@abstractmethod
	async def get_by_id(self, product_id: str) -> Optional[Offer]:  # pragma: no cover
		...

	@abstractmethod
	def build_url(self, product_id: str) -> str:  # pragma: no cover
		...