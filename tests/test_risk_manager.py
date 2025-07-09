"""
Unit-test: verify that a 2 % fixed stop-loss prevents large drawdowns on
a steadily falling market.
"""

import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from autostrat.strategies.momentum import MomentumStrategy
from autostrat.backtest.simple_backtester import SimpleBacktester
from autostrat.risk.risk_manager import FixedStopRiskManager


class TestRiskManager(unittest.TestCase):
    def test_stop_loss_limits_loss(self):
        # Synthetic down-trend: price falls 1 % per bar for 20 bars
        prices = pd.Series(100 * (0.99 ** np.arange(20)))

        strategy = MomentumStrategy(lookback=1)            # flips to short quickly
        risk_mgr = FixedStopRiskManager(stop_loss_pct=0.02)  # 2 % stop
        bt = SimpleBacktester(strategy, initial_cash=1000, risk_manager=risk_mgr)
        result = bt.run(prices)

        # Final equity must be ≥ 980 (i.e. no more than 2 % portfolio loss)
        self.assertGreaterEqual(result["final_equity"], 980.0)


if __name__ == "__main__":
    unittest.main()
