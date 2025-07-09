"""
Unit-test: ensure LiveRunner executes 50 ticks without crashing.

We monkey-patch TradierStream to emit deterministic ticks so the test
remains offline and reproducible.
"""

import unittest

from autostrat.live.runner import LiveRunner
from autostrat.data.tradier_stream import TradierStream


class TestLiveRunner(unittest.TestCase):
    def test_live_runner_executes(self):
        runner = LiveRunner(symbols=["TEST"], max_ticks=50)

        # monkey-patch the stream with deterministic data 
        def mock_stream(self):
            for i in range(50):
                yield {
                    "timestamp": "",
                    "symbol": "TEST",
                    "price": 100.0 + 0.1 * i,
                    "iv_rank": 0.5,
                }

        TradierStream._yield_mock_ticks = mock_stream

        # Should complete without exceptions
        runner.run()


if __name__ == "__main__":
    unittest.main()
