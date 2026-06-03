from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass(slots=True)
class AlertRuleConfig:
    threshold_pct: float
    cooldown_after_alert: float
    realert_if_spread_increases_by: float
    realert_max_interval: float
    hysteresis: float


@dataclass(slots=True)
class AlertState:
    active: bool = False
    last_alert_ts: float = 0.0
    last_alert_spread: float = 0.0


class AlertStateMachine:
    def __init__(self, config: AlertRuleConfig) -> None:
        self.config = config
        self._states: dict[str, AlertState] = {}

    def should_alert(self, key: str, spread_pct: float, now: float | None = None) -> bool:
        ts = now if now is not None else time.time()
        state = self._states.setdefault(key, AlertState())

        threshold = self.config.threshold_pct
        if not state.active:
            if spread_pct >= threshold:
                state.active = True
                state.last_alert_ts = ts
                state.last_alert_spread = spread_pct
                return True
            return False

        if spread_pct < (threshold - self.config.hysteresis):
            state.active = False
            return False

        elapsed = ts - state.last_alert_ts
        if elapsed < self.config.cooldown_after_alert:
            return False

        if spread_pct >= state.last_alert_spread + self.config.realert_if_spread_increases_by:
            state.last_alert_ts = ts
            state.last_alert_spread = spread_pct
            return True

        if elapsed >= self.config.realert_max_interval and spread_pct >= threshold:
            state.last_alert_ts = ts
            state.last_alert_spread = spread_pct
            return True

        return False
