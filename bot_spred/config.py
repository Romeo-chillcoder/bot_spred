from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(slots=True)
class Settings:
    telegram_bot_token: str
    test_chat_id: int
    prod_chat_id: int
    enabled_exchanges: list[str]
    scan_interval_seconds: float
    verify_delay_seconds: float
    request_timeout_seconds: float
    prod_perp_spread_threshold: float
    test_perp_spread_threshold: float
    cooldown_after_alert: float
    realert_if_spread_increases_by: float
    realert_max_interval: float
    hysteresis: float


def load_settings() -> Settings:
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    test_chat_id = os.getenv("TEST_CHAT_ID", "").strip()
    prod_chat_id = os.getenv("PROD_CHAT_ID", "").strip()

    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN is required")
    if not test_chat_id or not prod_chat_id:
        raise ValueError("TEST_CHAT_ID and PROD_CHAT_ID are required")

    enabled_exchanges = [
        item.strip().lower()
        for item in os.getenv("ENABLED_EXCHANGES", "binance,gate").split(",")
        if item.strip()
    ]

    return Settings(
        telegram_bot_token=token,
        test_chat_id=int(test_chat_id),
        prod_chat_id=int(prod_chat_id),
        enabled_exchanges=enabled_exchanges,
        scan_interval_seconds=float(os.getenv("SCAN_INTERVAL_SECONDS", "5")),
        verify_delay_seconds=float(os.getenv("VERIFY_DELAY_SECONDS", "2")),
        request_timeout_seconds=float(os.getenv("REQUEST_TIMEOUT_SECONDS", "10")),
        prod_perp_spread_threshold=float(os.getenv("PROD_PERP_SPREAD_THRESHOLD", "10.0")),
        test_perp_spread_threshold=float(os.getenv("TEST_PERP_SPREAD_THRESHOLD", "0.0")),
        cooldown_after_alert=float(os.getenv("COOLDOWN_AFTER_ALERT", "30")),
        realert_if_spread_increases_by=float(
            os.getenv("REALERT_IF_SPREAD_INCREASES_BY", "1.0")
        ),
        realert_max_interval=float(os.getenv("REALERT_MAX_INTERVAL", "120")),
        hysteresis=float(os.getenv("HYSTERESIS", "0.7")),
    )
