from __future__ import annotations

from typing import Iterable

from bot_spred.models import Quote, SpreadRoute


def execution_aware_spread_pct(buy_price: float, sell_price: float) -> float:
    if buy_price <= 0:
        raise ValueError("buy_price must be > 0")
    return (sell_price - buy_price) / buy_price * 100.0


def build_perp_routes(symbol: str, quotes: Iterable[Quote]) -> list[SpreadRoute]:
    quote_list = [q for q in quotes if q.ask > 0 and q.bid > 0]
    routes: list[SpreadRoute] = []
    for long_quote in quote_list:
        for short_quote in quote_list:
            if long_quote.exchange == short_quote.exchange:
                continue
            spread_pct = execution_aware_spread_pct(long_quote.ask, short_quote.bid)
            routes.append(
                SpreadRoute(
                    symbol=symbol,
                    long_exchange=long_quote.exchange,
                    short_exchange=short_quote.exchange,
                    buy_price=long_quote.ask,
                    sell_price=short_quote.bid,
                    spread_pct=spread_pct,
                    long_funding_rate=long_quote.funding_rate,
                    short_funding_rate=short_quote.funding_rate,
                )
            )
    routes.sort(key=lambda r: r.spread_pct, reverse=True)
    return routes
