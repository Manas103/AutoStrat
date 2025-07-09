"""
VolPremiumStrategy
------------------
Rule-based “volatility premium seller” (short strangle stand-in).

Signal logic (simplified for demo/back-test):
If Implied-Volatility Rank (IV-Rank) > `iv_threshold` → **SELL**
  (open short-premium position).
If a short is open **and** IV-Rank falls below `iv_threshold * 0.7`
  → **BUY** (cover / flatten).
Else **HOLD**.

The strategy tracks `self.active_short` internally to know if it has an
open position.  SELL is treated as entering short premium (–1), BUY as
closing it (+1 or flat).  You can extend this to size trades or manage
multiple legs later.
"""

from typing import Dict, Any, List

from .base import Strategy


class VolPremiumStrategy(Strategy):
    def __init__(self, iv_threshold: float = 0.7):
        super().__init__(name="VolPremium")
        self.iv_threshold = iv_threshold
        self.active_short = False

    #  Strategy API
    def generate_signal(self, market_state: Dict[str, Any]) -> str:
        iv_rank_series: List[float] = market_state["iv_rank"]
        if not iv_rank_series:
            return "HOLD"

        current_iv_rank = iv_rank_series[-1]

        if not self.active_short and current_iv_rank > self.iv_threshold:
            self.active_short = True
            return "SELL"   # open short premium
        elif self.active_short and current_iv_rank < self.iv_threshold * 0.7:
            self.active_short = False
            return "BUY"    # cover
        else:
            return "HOLD"
