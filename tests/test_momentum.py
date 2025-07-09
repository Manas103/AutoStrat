import unittest
from autostrat.strategies.momentum import MomentumStrategy


class TestMomentumStrategy(unittest.TestCase):
    def test_buy_signal(self):
        prices = list(range(1, 30))  # rising prices
        strat = MomentumStrategy(lookback=5)
        self.assertEqual(
            strat.generate_signal({"close_prices": prices}),
            "BUY",
        )

    def test_sell_signal(self):
        prices = list(range(30, 1, -1))  # falling prices
        strat = MomentumStrategy(lookback=5)
        self.assertEqual(
            strat.generate_signal({"close_prices": prices}),
            "SELL",
        )

    def test_hold_signal_insufficient_data(self):
        prices = [1, 2, 3]
        strat = MomentumStrategy(lookback=5)
        self.assertEqual(
            strat.generate_signal({"close_prices": prices}),
            "HOLD",
        )


if __name__ == "__main__":
    unittest.main()
