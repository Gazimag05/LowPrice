from __future__ import annotations

import asyncio
import sys

from app.core.aggregator import Aggregator
from app.providers.wildberries import WildberriesProvider


async def _run(query: str) -> int:
    aggregator = Aggregator([WildberriesProvider()])
    offers = await aggregator.search_all(query, limit_per_provider=5)
    if not offers:
        print("No offers found.")
        return 1

    for offer in offers[:10]:
        print(f"{offer.provider}\t{offer.price_rub:.2f} ₽\t{offer.title}\t{offer.url}")
    return 0


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python cli.py <query>")
        sys.exit(2)
    query = " ".join(sys.argv[1:])
    rc = asyncio.run(_run(query))
    sys.exit(rc)


if __name__ == "__main__":
    main()