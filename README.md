# bot_spred

MVP Telegram-бот сканування спредів (alert-only) для CEX Perp/Perp.

## Що реалізовано

- Async Python scanner (`asyncio`) для USDT-margined perpetual ринків.
- Біржі MVP: **Binance** + **Gate**.
- Execution-aware spread:
  - `buy_price = ask` на LONG біржі
  - `sell_price = bid` на SHORT біржі
  - `spread% = (sell - buy) / buy * 100`
- Telegram routing:
  - `TEST_CHAT_ID`: отримує всі perp/perp алерти, які проходять anti-spam.
  - `PROD_CHAT_ID`: лише perp/perp алерти зі spread `>= 10%`.
- Anti-spam state machine:
  - `cooldown_after_alert = 30s`
  - `realert_if_spread_increases_by = 1.0%`
  - `realert_max_interval = 120s`
  - `hysteresis = 0.7%`
- Повідомлення у timezone `Europe/Kyiv` + `Verified after Xs delay`.
- Каркас для розширення:
  - exchange interface для додавання нових CEX
  - `SpotSpotScanner` placeholder для spot/spot.

## Налаштування

1. Скопіюйте `.env.example` у `.env` і заповніть значення.
2. Встановіть залежності:

```bash
pip install -r requirements.txt
```

## Запуск

```bash
python -m bot_spred.main
```

## Тести

```bash
python -m pytest -q
```

## Змінні оточення

- `TELEGRAM_BOT_TOKEN`
- `TEST_CHAT_ID`
- `PROD_CHAT_ID`
- `ENABLED_EXCHANGES` (наприклад: `binance,gate`)
- `SCAN_INTERVAL_SECONDS`
- `VERIFY_DELAY_SECONDS`
- `PROD_PERP_SPREAD_THRESHOLD` (за замовчуванням `10.0`)
- `TEST_PERP_SPREAD_THRESHOLD` (за замовчуванням `0.0`)
- `COOLDOWN_AFTER_ALERT`
- `REALERT_IF_SPREAD_INCREASES_BY`
- `REALERT_MAX_INTERVAL`
- `HYSTERESIS`
