from __future__ import annotations

import time

import aiohttp

from bot_spred.exchanges.base import ExchangeClient
from bot_spred.models import Quote


class BinancePerpClient(ExchangeClient):
    name = "binance"

    def __init__(self, session: aiohttp.ClientSession, request_timeout_seconds: float) -> None:
        self._session = session
        self._request_timeout = aiohttp.ClientTimeout(total=request_timeout_seconds)

    async def fetch_perp_quotes(self) -> dict[str, Quote]:
        async with self._session.get(
            "https://fapi.binance.com/fapi/v1/ticker/bookTicker",
            timeout=self._request_timeout,
        ) as response:
            response.raise_for_status()
            tickers = await response.json()

        async with self._session.get(
            "https://fapi.binance.com/fapi/v1/premiumIndex",
            timeout=self._request_timeout,
        ) as response:
            response.raise_for_status()
            funding_items = await response.json()

        funding_by_symbol = {}
        for item in funding_items:
            if not isinstance(item, dict) or not item.get("symbol"):
                continue
            funding_raw = item.get("lastFundingRate")
            funding_by_symbol[item["symbol"]] = (
                float(funding_raw) if funding_raw not in (None, "") else None
            )

        now = time.time()
        quotes: dict[str, Quote] = {}
        for item in tickers:
            symbol = item.get("symbol", "")
            if not symbol.endswith("USDT") or "_" in symbol:
                continue
            bid = float(item.get("bidPrice", "0") or 0)
            ask = float(item.get("askPrice", "0") or 0)
            if bid <= 0 or ask <= 0:
                continue
            quotes[symbol] = Quote(
                exchange=self.name,
                symbol=symbol,
                bid=bid,
                ask=ask,
                funding_rate=funding_by_symbol.get(symbol),
                timestamp=now,
                market_type="perp",
            )
        return quotes
