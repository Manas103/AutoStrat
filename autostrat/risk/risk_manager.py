"""
Risk management utilities.

RiskManager (abstract base class)
FixedStopRiskManager – exits a trade when price moves against the entry
by a fixed percentage.

Extend this file with additional risk modules (e.g. trailing‐stop,
volatility stop, max drawdown) as needed.
"""

from abc import ABC, abstractmethod


class RiskManager(ABC):
    """Interface for any risk-management rule."""

    @abstractmethod
    def should_exit(
        self,
        entry_price: float,
        current_price: float,
        position: int,  # +1 long, –1 short, 0 flat
    ) -> bool:
        """
        Return True if the open position must be closed.

        Parameters
        ----------
        entry_price : float
            Price at which the position was opened.
        current_price : float
            Latest market price (same units as entry_price).
        position : int
            +1 for long, –1 for short, 0 for flat.
        """
        ...


class FixedStopRiskManager(RiskManager):
    """
    Hard stop-loss: exit when price moves ≥ `stop_loss_pct`
    *against* the position.

    Examples
    --------
    >>> rm = FixedStopRiskManager(stop_loss_pct=0.02)  # 2 %
    >>> rm.should_exit(entry_price=100, current_price=97.5, position=+1)
    True     # price fell 2.5 %
    >>> rm.should_exit(entry_price=100, current_price=102, position=+1)
    False    # only +2 % in favour
    """

    def __init__(self, stop_loss_pct: float = 0.02):
        if stop_loss_pct <= 0:
            raise ValueError("stop_loss_pct must be positive")
        self.stop_loss_pct = float(stop_loss_pct)

    #  RiskManager API
    def should_exit(self, entry_price: float, current_price: float, position: int) -> bool:
        if position == 0:
            return False  # nothing to do

        change_pct = (current_price - entry_price) / entry_price

        if position > 0:  # long
            return change_pct <= -self.stop_loss_pct
        else:             # short
            return change_pct >= self.stop_loss_pct
