from abc import ABC, abstractmethod
from typing import Any, Dict, List


class Strategy(ABC):
    """Abstract base class for trading strategies."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def generate_signal(self, market_state: Dict[str, Any]) -> str:
        """Return 'BUY', 'SELL', or 'HOLD' based on market_state."""
        raise NotImplementedError

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"
