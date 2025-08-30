from __future__ import annotations

import abc
from typing import List

from app.models import Offer, SearchQuery


class Provider(abc.ABC):
    name: str

    @abc.abstractmethod
    async def search(self, query: SearchQuery, *, limit: int = 5) -> List[Offer]:
        raise NotImplementedError