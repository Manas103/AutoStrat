"""
Integration test: RollingSharpeSelector should end up with a positive
portfolio value by switching between Momentum (works in an up-trend) and
VolPremium (works when IV-Rank is high then falls).

Synthetic market:
* First 60 bars: price rises (momentum wins), IV-Rank low.
* Next 60 bars: price chops sideways, IV-Rank starts high (>0.8) then
  falls to 0.4 (vol-premium earns theta / mean-reversion).
"""

import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from autostrat.strategies.momentum import MomentumStrategy
from autostrat.strategies.vol_premium import VolPremiumStrategy
from autostrat.selector.rolling_sharpe_selector import RollingSharpeSelector
from autostrat.backtest.simple_backtester import SimpleBacktester
from autostrat.risk.risk_manager import FixedStopRiskManager


class TestSelector(unittest.TestCase):
    def test_selector_switches_strategy(self):
        # build synthetic market
        prices_up = pd.Series(np.linspace(100, 150, 60))  # trending
        iv_rank_low = pd.Series(np.full(60, 0.30))

        rng = np.random.default_rng(42)
        prices_side = pd.Series(150 + rng.normal(0, 0.5, 60))  # chop
        iv_rank_high_to_low = pd.Series(np.linspace(0.80, 0.40, 60))

        prices = pd.concat([prices_up, prices_side], ignore_index=True)
        iv_rank = pd.concat([iv_rank_low, iv_rank_high_to_low], ignore_index=True)

        # set up strategies & selector
        mom = MomentumStrategy(lookback=5)
        vol = VolPremiumStrategy(iv_threshold=0.7)
        selector = RollingSharpeSelector([mom, vol], window=20)
        risk_mgr = FixedStopRiskManager(stop_loss_pct=0.05)

        cash = 1000.0
        position = 0
        equity_curve = []

        # run bar-by-bar
        for i in range(len(prices)):
            market_state = {
                "close_prices": prices.iloc[: i + 1].tolist(),
                "iv_rank": iv_rank.iloc[: i + 1].tolist(),
            }

            strat = selector.best_strategy()
            signal = strat.generate_signal(market_state)

            # naive 1-unit execution
            if signal == "BUY" and position <= 0:
                cash -= prices.iloc[i]
                position += 1
            elif signal == "SELL" and position >= 0:
                cash += prices.iloc[i]
                position -= 1

            # equity + rolling return update
            equity = cash + position * prices.iloc[i]
            if equity_curve:
                pct_ret = (equity - equity_curve[-1]) / equity_curve[-1]
                selector.update_performance(strat.name, pct_ret)

            equity_curve.append(equity)

        self.assertGreater(
            equity_curve[-1],
            1000.0,
            f"Portfolio should grow. Final equity = {equity_curve[-1]:.2f}",
        )


if __name__ == "__main__":
    unittest.main()