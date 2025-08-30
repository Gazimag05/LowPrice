from __future__ import annotations

import aiohttp
from typing import Any, Dict, Optional

from app.utils.config import Settings


async def get_json(url: str, *, params: Optional[Dict[str, Any]] = None, timeout_seconds: float | None = None) -> Any:
    settings = Settings()
    timeout = aiohttp.ClientTimeout(total=timeout_seconds or settings.request_timeout_seconds)
    headers = {"User-Agent": settings.user_agent, "Accept": "application/json"}

    async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
        async with session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json(content_type=None)