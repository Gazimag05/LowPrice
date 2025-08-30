from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    bot_token: Optional[str] = os.getenv("BOT_TOKEN")
    request_timeout_seconds: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "8.0"))
    user_agent: str = os.getenv(
        "HTTP_USER_AGENT",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36",
    )