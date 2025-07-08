import unittest
from autostrat.strategies.momentum import MomentumStrategy


class TestMomentumStrategy(unittest.TestCase):
    def test_buy_signal(self):
        prices = list(range(1, 30))  # strictly increasing
        strat = MomentumStrategy(lookback=5)
        signal = strat.generate_signal({"close_prices": prices})
        self.assertEqual(signal, "BUY")

    def test_sell_signal(self):
        prices = list(range(30, 1, -1))  # strictly decreasing
        strat = MomentumStrategy(lookback=5)
        signal = strat.generate_signal({"close_prices": prices})
        self.assertEqual(signal, "SELL")

    def test_hold_signal_insufficient_data(self):
        prices = [1, 2, 3]  # not enough data
        strat = MomentumStrategy(lookback=5)
        signal = strat.generate_signal({"close_prices": prices})
        self.assertEqual(signal, "HOLD")


if __name__ == "__main__":
    unittest.main()
