"""
TradierStream – REST polling for paper trading.

Uses TRADIER_TOKEN to pull delayed quotes from the sandbox endpoint.
Falls back to a mock random-walk generator if the token is missing.
"""

import os
import time
from typing import Dict, Iterator, List

import requests
from dotenv import load_dotenv

load_dotenv()

BASE = os.getenv("TRADIER_BASE", "https://sandbox.tradier.com/v1")
TOKEN = os.getenv("TRADIER_TOKEN")
HDRS = {
    "Authorization": f"Bearer {TOKEN}" if TOKEN else "",
    "Accept": "application/json",
}


class TradierStream:
    def __init__(self, symbols: List[str], interval_s: float = 1.0):
        self.symbols = symbols
        self.interval_s = interval_s
        self.enabled = bool(TOKEN)

    def __iter__(self) -> Iterator[Dict]:
        if self.enabled:
            yield from self._poll_quotes()
        else:
            yield from self._yield_mock_ticks()

    #  REST-polling loop (paper accounts have 15-min delayed data)
    def _poll_quotes(self) -> Iterator[Dict]:
        symbols_csv = ",".join(self.symbols)
        url = f"{BASE}/markets/quotes"

        while True:

            print("DEBUG token length", len(TOKEN) if TOKEN else 0)
            
            resp = requests.get(
                url,
                headers=HDRS,
                params={"symbols": symbols_csv},
                timeout=10,
            )
            print("DEBUG status", resp.status_code)
            print("DEBUG headers", resp.headers.get("Content-Type"))
            print("DEBUG body", resp.text[:150])
            #  skip if body empty or HTML 
            if not resp.text:
                time.sleep(self.interval_s)
                continue
            if resp.headers.get("Content-Type", "").startswith("text/html"):
                print("Received HTML (likely token/endpoint issue); retrying in 5 s")
                time.sleep(5)
                continue

            try:
                data = resp.json()["quotes"]["quote"]
            except ValueError:
                # JSON decode failed → retry
                time.sleep(self.interval_s)
                continue

            if not data:                      # empty quote -> retry
                time.sleep(self.interval_s)
                continue

            quotes = data if isinstance(data, list) else [data]
            for q in quotes:
                yield {
                    "timestamp": q["trade_date"] + " " + q["trade_time"][:8],
                    "symbol": q["symbol"],
                    "price": q["last"],
                    "iv_rank": 0.5,           # TODO: real IV-Rank
                }

            time.sleep(self.interval_s)

    #  Mock fallback (unchanged)
    def _yield_mock_ticks(self) -> Iterator[Dict]:
        import random

        price = {s: 100 + random.random() * 2 for s in self.symbols}
        iv = {s: 0.50 for s in self.symbols}

        while True:
            for s in self.symbols:
                price[s] *= 1 + random.uniform(-0.001, 0.001)
                iv[s] += random.uniform(-0.02, 0.02)
                iv[s] = max(0.0, min(1.0, iv[s]))
                yield {
                    "timestamp": time.time(),
                    "symbol": s,
                    "price": price[s],
                    "iv_rank": iv[s],
                }
            time.sleep(self.interval_s)
