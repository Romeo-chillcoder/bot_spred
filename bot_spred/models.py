from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Quote:
    exchange: str
    symbol: str
    bid: float
    ask: float
    funding_rate: float | None
    timestamp: float
    market_type: str = "perp"


@dataclass(slots=True)
class SpreadRoute:
    symbol: str
    long_exchange: str
    short_exchange: str
    buy_price: float
    sell_price: float
    spread_pct: float
    long_funding_rate: float | None
    short_funding_rate: float | None
