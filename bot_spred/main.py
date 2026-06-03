from __future__ import annotations

import asyncio
import logging

import aiohttp

from bot_spred.config import load_settings
from bot_spred.exchanges import BinancePerpClient, GatePerpClient
from bot_spred.scanner import PerpPerpScanner
from bot_spred.state import AlertRuleConfig, AlertStateMachine
from bot_spred.telegram_notifier import TelegramNotifier


async def run() -> None:
    settings = load_settings()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    async with aiohttp.ClientSession() as session:
        exchanges = []
        for exchange_name in settings.enabled_exchanges:
            if exchange_name == "binance":
                exchanges.append(BinancePerpClient(session))
            elif exchange_name == "gate":
                exchanges.append(GatePerpClient(session))

        if len(exchanges) < 2:
            raise ValueError("At least 2 exchanges must be enabled for perp/perp scanning")

        notifier = TelegramNotifier(
            session=session,
            token=settings.telegram_bot_token,
            test_chat_id=settings.test_chat_id,
            prod_chat_id=settings.prod_chat_id,
            prod_perp_threshold=settings.prod_perp_spread_threshold,
        )

        test_state_machine = AlertStateMachine(
            AlertRuleConfig(
                threshold_pct=settings.test_perp_spread_threshold,
                cooldown_after_alert=settings.cooldown_after_alert,
                realert_if_spread_increases_by=settings.realert_if_spread_increases_by,
                realert_max_interval=settings.realert_max_interval,
                hysteresis=settings.hysteresis,
            )
        )
        prod_state_machine = AlertStateMachine(
            AlertRuleConfig(
                threshold_pct=settings.prod_perp_spread_threshold,
                cooldown_after_alert=settings.cooldown_after_alert,
                realert_if_spread_increases_by=settings.realert_if_spread_increases_by,
                realert_max_interval=settings.realert_max_interval,
                hysteresis=settings.hysteresis,
            )
        )

        scanner = PerpPerpScanner(
            exchanges=exchanges,
            notifier=notifier,
            test_state_machine=test_state_machine,
            prod_state_machine=prod_state_machine,
            verify_delay_seconds=settings.verify_delay_seconds,
        )

        while True:
            try:
                await scanner.scan_and_notify_once()
            except Exception:
                logger.exception("scan_and_notify_once failed")
            await asyncio.sleep(settings.scan_interval_seconds)


if __name__ == "__main__":
    asyncio.run(run())
