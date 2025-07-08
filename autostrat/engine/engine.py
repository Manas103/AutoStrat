from typing import Dict, Any
from autostrat.strategies.base import Strategy


class Engine:
    """Core engine to evaluate strategies and output actions."""

    def __init__(self, strategy: Strategy):
        self.strategy = strategy

    def step(self, market_state: Dict[str, Any]) -> str:
        """Evaluate one step and return suggested action."""
        return self.strategy.generate_signal(market_state)
