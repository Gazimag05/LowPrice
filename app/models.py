from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Offer:
    provider: str
    title: str
    price_rub: float
    url: str
    image_url: Optional[str] = None


@dataclass
class SearchQuery:
    text: str