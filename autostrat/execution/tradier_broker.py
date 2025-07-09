"""
TradierBroker – paper-trading REST wrapper.
Places market orders
Tracks cash / positions in memory
"""

import os
import requests
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

BASE = os.getenv("TRADIER_BASE", "https://sandbox.tradier.com/v1")
TOKEN = os.getenv("TRADIER_TOKEN")
ACCOUNT_ID = os.getenv("TRADIER_ACCOUNT_ID")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json",
}

class TradierBroker:
    def __init__(self, starting_cash: float = 10_000.0):
        self.cash = starting_cash
        self.positions: Dict[str, int] = {}

    def place_market_order(self, symbol: str, side: str, qty: int, price: float):
        if not TOKEN or not ACCOUNT_ID:
            raise RuntimeError("TRADIER_TOKEN or TRADIER_ACCOUNT_ID not set")

        payload = {
            "class": "equity",
            "symbol": symbol,
            "side": side.lower(),          # buy / sell
            "quantity": qty,
            "type": "market",
            "duration": "day",
        }
        url = f"{BASE}/accounts/{ACCOUNT_ID}/orders"
        r = requests.post(url, headers=HEADERS, data=payload, timeout=10)
        r.raise_for_status()

        # update local ledger
        if side.upper() == "BUY":
            self.cash -= qty * price
            self.positions[symbol] = self.positions.get(symbol, 0) + qty
        else:
            self.cash += qty * price
            self.positions[symbol] = self.positions.get(symbol, 0) - qty

        return r.json()["order"]["id"]

    def portfolio_value(self, last_prices: Dict[str, float]) -> float:
        value = self.cash
        for sym, pos in self.positions.items():
            value += pos * last_prices.get(sym, 0.0)
        return value
