from typing import Dict, Any, List
from .base import Strategy
import numpy as np


class MomentumStrategy(Strategy):
    """Simple momentum strategy comparing price to moving average."""

    def __init__(self, lookback: int = 20):
        super().__init__(name="Momentum")
        self.lookback = lookback

    def generate_signal(self, market_state: Dict[str, Any]) -> str:
        prices: List[float] = market_state["close_prices"]
        if len(prices) < self.lookback + 1:
            return "HOLD"

        sma = np.mean(prices[-self.lookback - 1:-1])
        current_price = prices[-1]

        if current_price > sma:
            return "BUY"
        elif current_price < sma:
            return "SELL"
        else:
            return "HOLD"
