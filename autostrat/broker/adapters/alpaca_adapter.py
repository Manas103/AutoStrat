import os
import alpaca_trade_api as tradeapi

class AlpacaAdapter:
    def __init__(self):
        self.api = tradeapi.REST(
            os.getenv("ALPACA_API_KEY"),
            os.getenv("ALPACA_SECRET_KEY"),
            base_url="https://paper-api.alpaca.markets"
        )

    def get_price(self, symbol):
        barset = self.api.get_bars(symbol, tradeapi.TimeFrame.Minute, limit=1)
        return float(barset[0].c) if barset else None

    def buy(self, symbol, qty):
        self.api.submit_order(
            symbol=symbol,
            qty=qty,
            side="buy",
            type="market",
            time_in_force="gtc"
        )

    def sell(self, symbol, qty):
        self.api.submit_order(
            symbol=symbol,
            qty=qty,
            side="sell",
            type="market",
            time_in_force="gtc"
        )

    def get_position(self, symbol):
        try:
            return float(self.api.get_position(symbol).qty)
        except tradeapi.rest.APIError:
            return 0
