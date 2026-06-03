from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import aiohttp

from bot_spred.models import SpreadRoute

KYIV_TZ = ZoneInfo("Europe/Kyiv")


class TelegramNotifier:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        token: str,
        test_chat_id: int,
        prod_chat_id: int,
        prod_perp_threshold: float,
    ) -> None:
        self._session = session
        self._token = token
        self._test_chat_id = test_chat_id
        self._prod_chat_id = prod_chat_id
        self._prod_perp_threshold = prod_perp_threshold

    async def notify_perp(
        self,
        best_route: SpreadRoute,
        all_routes: list[SpreadRoute],
        verified_delay_seconds: float,
    ) -> None:
        text = self._format_perp_message(best_route, all_routes, verified_delay_seconds)
        await self._send_message(self._test_chat_id, text)
        if best_route.spread_pct >= self._prod_perp_threshold:
            await self._send_message(self._prod_chat_id, text)

    async def _send_message(self, chat_id: int, text: str) -> None:
        endpoint = f"https://api.telegram.org/bot{self._token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        async with self._session.post(endpoint, json=payload, timeout=10) as response:
            response.raise_for_status()

    def _format_perp_message(
        self,
        best_route: SpreadRoute,
        all_routes: list[SpreadRoute],
        verified_delay_seconds: float,
    ) -> str:
        ts_kyiv = datetime.now(tz=KYIV_TZ).strftime("%Y-%m-%d %H:%M:%S %Z")

        all_route_lines = [
            f"- {route.long_exchange} -> {route.short_exchange}: {route.spread_pct:.2f}%"
            for route in all_routes
        ]
        all_routes_text = "\n".join(all_route_lines) if all_route_lines else "- no routes"

        long_funding = self._format_funding(best_route.long_funding_rate)
        short_funding = self._format_funding(best_route.short_funding_rate)

        return (
            f"{best_route.symbol} | {best_route.spread_pct:.2f}%\n"
            f"Long:\n"
            f"- Exchange: {best_route.long_exchange}\n"
            f"- Ask: {best_route.buy_price:.8f}\n"
            f"- Funding: {long_funding}\n"
            f"Short:\n"
            f"- Exchange: {best_route.short_exchange}\n"
            f"- Bid: {best_route.sell_price:.8f}\n"
            f"- Funding: {short_funding}\n"
            f"Best route: {best_route.long_exchange} -> {best_route.short_exchange}\n"
            f"All routes:\n"
            f"{all_routes_text}\n"
            f"Timestamp: {ts_kyiv}\n"
            f"Verified after {verified_delay_seconds:g}s delay"
        )

    @staticmethod
    def _format_funding(value: float | None) -> str:
        return "n/a" if value is None else f"{value:.6f}"
