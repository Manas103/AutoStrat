"""
SimpleBacktester – now with optional risk management.

* Executes 1-unit trades based on a Strategy’s BUY / SELL signals.
* If a RiskManager is supplied, the back-tester checks it each bar and
  exits the open position when `should_exit(...)` returns True.
"""

from typing import Dict, List, Optional

import pandas as pd

from autostrat.strategies.base import Strategy
from autostrat.risk.risk_manager import RiskManager


class SimpleBacktester:
    """
    Parameters
    strategy : Strategy
    Trading logic that produces BUY / SELL / HOLD.
    initial_cash : float, default 1000
    risk_manager : RiskManager | None
    If provided, positions will be closed when the rule triggers.
    """

    def __init__(
        self,
        strategy: Strategy,
        initial_cash: float = 1000.0,
        risk_manager: Optional[RiskManager] = None,
    ):
        self.strategy = strategy
        self.initial_cash = float(initial_cash)
        self.risk_manager = risk_manager

    #  Public API
    def run(self, prices: pd.Series) -> Dict[str, float | List[float]]:
        cash = self.initial_cash
        position = 0                     # +1 long, –1 short, 0 flat
        entry_price: float | None = None
        equity_curve: List[float] = [cash]

        for i, current_price in enumerate(prices):
            #  Risk manager first: decide to flatten early
            if (
                position != 0
                and self.risk_manager is not None
                and self.risk_manager.should_exit(entry_price, current_price, position)
            ):
                cash += position * current_price
                position = 0
                entry_price = None

            #  Strategy signal
            slice_until_now = prices.iloc[: i + 1]
            signal = self.strategy.generate_signal({"close_prices": slice_until_now.tolist()})

            if signal == "BUY" and position <= 0:
                if position < 0:                      # close short
                    cash += abs(position) * current_price
                cash -= current_price                 # open long
                position = 1
                entry_price = current_price

            elif signal == "SELL" and position >= 0:
                if position > 0:                      # close long
                    cash += position * current_price
                cash += current_price                 # open short
                position = -1
                entry_price = current_price

            equity_curve.append(cash + position * current_price)

        #  Liquidate any open position at the final price
        if position != 0:
            cash += position * prices.iloc[-1]
            position = 0

        final_equity = cash
        return {
            "final_equity": final_equity,
            "equity_curve": equity_curve,
            "return_pct": (final_equity - self.initial_cash) / self.initial_cash * 100,
        }
