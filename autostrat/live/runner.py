"""
LiveRunner – selector → Tradier mock broker in real time.

Currently uses the mock TradierStream and an in-memory TradierBroker.
Swap the stream & broker code for real API calls once your credentials
are ready.
"""

from typing import Dict, List

from autostrat.data.tradier_stream import TradierStream
from autostrat.execution.tradier_broker import TradierBroker
from autostrat.risk.risk_manager import FixedStopRiskManager
from autostrat.selector.rolling_sharpe_selector import RollingSharpeSelector
from autostrat.strategies.momentum import MomentumStrategy
from autostrat.strategies.vol_premium import VolPremiumStrategy


class LiveRunner:
    def __init__(self, symbols: List[str], max_ticks: int = 300):
        self.symbols = symbols
        self.max_ticks = max_ticks

        # strategy stack & selector 
        self.strategies = [
            MomentumStrategy(lookback=5),
            VolPremiumStrategy(iv_threshold=0.7),
        ]
        self.selector = RollingSharpeSelector(self.strategies, window=30)

        #  risk & broker
        self.risk_mgr = FixedStopRiskManager(stop_loss_pct=0.03)
        self.broker = TradierBroker(starting_cash=10_000.0)
        self.last_prices: Dict[str, float] = {sym: 0.0 for sym in symbols}

    def run(self) -> None:
        stream = TradierStream(self.symbols, interval_s=0.1)  # mock ticks
        equity_curve: List[float] = []

        for i, tick in enumerate(stream):
            sym = tick["symbol"]
            price = tick["price"]
            iv = tick["iv_rank"]
            self.last_prices[sym] = price

            # choose strategy 
            market_state = {
                "close_prices": [price],
                "iv_rank": [iv],
            }
            strat = self.selector.best_strategy()
            signal = strat.generate_signal(market_state)

            # place order via TradierBroker
            if signal == "BUY":
                self.broker.place_market_order(sym, "BUY", 1, price)
            elif signal == "SELL":
                self.broker.place_market_order(sym, "SELL", 1, price)

            # update rolling Sharpe
            port_val = self.broker.portfolio_value(self.last_prices)
            if equity_curve:
                pct_ret = (port_val - equity_curve[-1]) / equity_curve[-1]
                self.selector.update_performance(strat.name, pct_ret)
            equity_curve.append(port_val)

            if i + 1 >= self.max_ticks:
                break

        print(f"Finished live run. Final portfolio value: {equity_curve[-1]:.2f}")


if __name__ == "__main__":
    LiveRunner(["AAPL"], max_ticks=300).run()
