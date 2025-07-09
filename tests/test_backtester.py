"""
Unit-test: Momentum strategy should profit on a 60-day up-trend.
Path handling fixed for Windows/Mac/Linux.
"""

import unittest
from pathlib import Path

from autostrat.data.csv_provider import CSVDataProvider
from autostrat.strategies.momentum import MomentumStrategy
from autostrat.backtest.simple_backtester import SimpleBacktester


class TestBacktester(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # <repo_root>/sample_data   (works regardless of where tests run from)
        cls.sample_dir = Path(__file__).resolve().parent.parent / "sample_data"

    def setUp(self):
        provider = CSVDataProvider(self.sample_dir)
        self.prices = provider.get_history(
            "UPTREND", "2025-01-01", "2025-03-01"
        )["Close"]
        self.strategy = MomentumStrategy(lookback=5)

    def test_positive_return_on_uptrend(self):
        # Ensure data actually loaded
        self.assertGreater(len(self.prices), 0, "Price series is empty!")

        backtester = SimpleBacktester(self.strategy, initial_cash=1000)
        result = backtester.run(self.prices)

        self.assertGreater(
            result["return_pct"],
            0,
            f"Expected positive return, got {result['return_pct']:.2f} %",
        )


if __name__ == "__main__":
    unittest.main()
