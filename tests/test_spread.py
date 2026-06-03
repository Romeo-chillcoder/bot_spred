import pytest

from bot_spred.models import Quote
from bot_spred.spread import build_perp_routes, execution_aware_spread_pct


def test_execution_aware_spread_pct():
    result = execution_aware_spread_pct(100.0, 110.0)
    assert result == pytest.approx(10.0)


def test_execution_aware_spread_pct_requires_positive_buy_price():
    with pytest.raises(ValueError):
        execution_aware_spread_pct(0.0, 110.0)


def test_build_perp_routes_uses_ask_for_long_and_bid_for_short():
    quotes = [
        Quote(
            exchange="binance",
            symbol="BTCUSDT",
            bid=100.0,
            ask=101.0,
            funding_rate=0.001,
            timestamp=1.0,
        ),
        Quote(
            exchange="gate",
            symbol="BTCUSDT",
            bid=112.0,
            ask=113.0,
            funding_rate=0.002,
            timestamp=1.0,
        ),
    ]

    routes = build_perp_routes("BTCUSDT", quotes)

    assert routes[0].long_exchange == "binance"
    assert routes[0].short_exchange == "gate"
    assert routes[0].buy_price == pytest.approx(101.0)
    assert routes[0].sell_price == pytest.approx(112.0)
    assert routes[0].spread_pct == pytest.approx((112.0 - 101.0) / 101.0 * 100)
