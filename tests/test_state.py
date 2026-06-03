from bot_spred.state import AlertRuleConfig, AlertStateMachine


def _build_state_machine(threshold: float = 10.0) -> AlertStateMachine:
    return AlertStateMachine(
        AlertRuleConfig(
            threshold_pct=threshold,
            cooldown_after_alert=30,
            realert_if_spread_increases_by=1.0,
            realert_max_interval=120,
            hysteresis=0.7,
        )
    )


def test_initial_alert_and_cooldown_behavior():
    sm = _build_state_machine()

    assert sm.should_alert("perp:BTCUSDT", 10.1, now=100.0)
    assert not sm.should_alert("perp:BTCUSDT", 11.5, now=120.0)
    assert sm.should_alert("perp:BTCUSDT", 11.5, now=131.0)


def test_realert_after_max_interval_when_still_above_threshold():
    sm = _build_state_machine()

    assert sm.should_alert("perp:BTCUSDT", 10.1, now=100.0)
    assert sm.should_alert("perp:BTCUSDT", 10.2, now=221.0)


def test_hysteresis_resets_state_below_threshold_minus_hysteresis():
    sm = _build_state_machine()

    assert sm.should_alert("perp:BTCUSDT", 10.2, now=100.0)
    assert not sm.should_alert("perp:BTCUSDT", 9.2, now=150.0)
    assert sm.should_alert("perp:BTCUSDT", 10.3, now=151.0)
