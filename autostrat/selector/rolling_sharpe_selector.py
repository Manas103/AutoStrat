"""
RollingSharpeSelector
---------------------
Given multiple Strategy objects, tracks each one’s rolling percentage
returns and selects the strategy with the highest Sharpe ratio over a
sliding window.

* Call `update_performance(name, pct_return)` once per bar **after**
  you compute that bar’s portfolio % return when the strategy was
  active.
* Call `best_strategy()` to retrieve the Strategy instance that
  currently has the highest Sharpe ratio (mean / std) over the window.

Note: requires at least 2 returns before Sharpe is defined; until then
the selector simply returns the first strategy in the list.
"""

from collections import deque
from typing import Dict, List

import numpy as np

from autostrat.strategies.base import Strategy


class RollingSharpeSelector:
    def __init__(self, strategies: List[Strategy], window: int = 20):
        self.strategies = strategies
        self.window = window
        self.ret_history: Dict[str, deque] = {
            strat.name: deque(maxlen=window) for strat in strategies
        }

    #  Public API
    def update_performance(self, strategy_name: str, pct_return: float) -> None:
        """Append the last bar’s % return for the given strategy."""
        self.ret_history[strategy_name].append(pct_return)

    def best_strategy(self) -> Strategy:
        """Return the Strategy object with the highest rolling Sharpe."""
        best = self.strategies[0]
        best_score = -np.inf

        for strat in self.strategies:
            rets = self.ret_history[strat.name]
            if len(rets) < 2:
                score = -np.inf
            else:
                arr = np.array(rets, dtype=float)
                mean, std = arr.mean(), arr.std(ddof=1)
                score = mean / std if std > 0 else -np.inf

            if score > best_score:
                best_score = score
                best = strat

        return best
