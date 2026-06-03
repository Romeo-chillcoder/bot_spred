from __future__ import annotations

import time

import aiohttp

from bot_spred.exchanges.base import ExchangeClient
from bot_spred.models import Quote


class GatePerpClient(ExchangeClient):
    name = "gate"

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session

    async def fetch_perp_quotes(self) -> dict[str, Quote]:
        async with self._session.get(
            "https://api.gateio.ws/api/v4/futures/usdt/tickers", timeout=10
        ) as response:
            response.raise_for_status()
            tickers = await response.json()

        now = time.time()
        quotes: dict[str, Quote] = {}
        for item in tickers:
            contract = item.get("contract", "")
            if not contract.endswith("_USDT"):
                continue
            bid = float(item.get("highest_bid", "0") or 0)
            ask = float(item.get("lowest_ask", "0") or 0)
            if bid <= 0 or ask <= 0:
                continue

            symbol = contract.replace("_", "")
            funding_raw = item.get("funding_rate")
            funding_rate = float(funding_raw) if funding_raw not in (None, "") else None

            quotes[symbol] = Quote(
                exchange=self.name,
                symbol=symbol,
                bid=bid,
                ask=ask,
                funding_rate=funding_rate,
                timestamp=now,
                market_type="perp",
            )
        return quotes
