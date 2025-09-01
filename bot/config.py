import os
from dataclasses import dataclass
from typing import List, Optional

from dotenv import load_dotenv


@dataclass
class Config:
	bot_token: str
	allowed_chats: Optional[List[int]]
	track_interval_seconds: int
	wb_dest: int
	wb_currency: str
	wb_app_type: int


def load_config() -> Config:
	load_dotenv(override=False)

	bot_token = os.getenv("BOT_TOKEN", "")
	allowed_raw = os.getenv("ALLOWED_CHATS", "").strip()
	allowed_chats = None
	if allowed_raw:
		allowed_chats = []
		for item in allowed_raw.split(","):
			item = item.strip()
			if not item:
				continue
			try:
				allowed_chats.append(int(item))
			except ValueError:
				continue

	track_interval_seconds = int(os.getenv("TRACK_INTERVAL_SECONDS", "900"))
	wb_dest = int(os.getenv("WB_DEST", "-1257786"))
	wb_currency = os.getenv("WB_CURR", "rub")
	wb_app_type = int(os.getenv("WB_APP_TYPE", "1"))

	return Config(
		bot_token=bot_token,
		allowed_chats=allowed_chats,
		track_interval_seconds=track_interval_seconds,
		wb_dest=wb_dest,
		wb_currency=wb_currency,
		wb_app_type=wb_app_type,
	)