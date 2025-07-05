from data.fetch_chain import fetch_option_chain
from strategy.rank_strategies import rank_all_strategies
from backtest.simulate import run_backtest
from strategy.payoff_models import long_call, long_put, long_straddle
import yfinance as yf


TICKER = "SPY"
hist = yf.download(TICKER, start="2023-01-01", end="2023-06-30")
close = hist["Close"]
S0 = float(close.iloc[0])

options, _ = fetch_option_chain(TICKER)
ranked = rank_all_strategies(options, S0)

top = ranked.iloc[0] # best-scoring idea
print("Top pick:\n", top)

# Build the actual strategy object
if top["type"] == "call":
    strategy = long_call(top["strike"], top["lastPrice"])
elif top["type"] == "put":
    strategy = long_put(top["strike"], top["lastPrice"])
else:
    strategy = long_straddle(top["strike"], top["lastPrice"]/2, top["lastPrice"]/2)

pnl = run_backtest(close, strategy)
print("Back-test PnL on top pick:", pnl)