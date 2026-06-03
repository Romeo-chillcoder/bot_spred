from __future__ import annotations

from abc import ABC, abstractmethod

from bot_spred.models import Quote


class ExchangeClient(ABC):
    name: str

    @abstractmethod
    async def fetch_perp_quotes(self) -> dict[str, Quote]:
        raise NotImplementedError

    async def fetch_spot_quotes(self) -> dict[str, Quote]:
        return {}
