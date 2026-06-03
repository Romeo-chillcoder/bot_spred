from __future__ import annotations

import asyncio
import logging
import time
from collections import defaultdict

from bot_spred.exchanges.base import ExchangeClient
from bot_spred.models import Quote
from bot_spred.spread import build_perp_routes
from bot_spred.state import AlertStateMachine
from bot_spred.telegram_notifier import TelegramNotifier

logger = logging.getLogger(__name__)


class PerpPerpScanner:
    def __init__(
        self,
        exchanges: list[ExchangeClient],
        notifier: TelegramNotifier,
        test_state_machine: AlertStateMachine,
        prod_state_machine: AlertStateMachine,
        verify_delay_seconds: float,
    ) -> None:
        self._exchanges = exchanges
        self._notifier = notifier
        self._test_state_machine = test_state_machine
        self._prod_state_machine = prod_state_machine
        self._verify_delay_seconds = verify_delay_seconds

    async def scan_and_notify_once(self) -> None:
        if self._verify_delay_seconds > 0:
            await self._fetch_symbol_quotes()
            await asyncio.sleep(self._verify_delay_seconds)

        verified_quotes = await self._fetch_symbol_quotes()
        now = time.time()
        for symbol, quotes in verified_quotes.items():
            routes = build_perp_routes(symbol, quotes)
            if not routes:
                continue
            best_route = routes[0]
            key = f"perp:{symbol}"

            test_alert = self._test_state_machine.should_alert(key, best_route.spread_pct, now)
            prod_alert = self._prod_state_machine.should_alert(key, best_route.spread_pct, now)

            if test_alert or prod_alert:
                await self._notifier.notify_perp(
                    best_route=best_route,
                    all_routes=routes,
                    verified_delay_seconds=self._verify_delay_seconds,
                )

    async def _fetch_symbol_quotes(self) -> dict[str, list[Quote]]:
        tasks = [exchange.fetch_perp_quotes() for exchange in self._exchanges]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        by_symbol: dict[str, list[Quote]] = defaultdict(list)
        for exchange, result in zip(self._exchanges, results):
            if isinstance(result, Exception):
                logger.warning("Failed to fetch quotes from %s: %s", exchange.name, result)
                continue
            for symbol, quote in result.items():
                by_symbol[symbol].append(quote)
        return by_symbol


class SpotSpotScanner:
    async def scan_and_notify_once(self) -> None:
        return
