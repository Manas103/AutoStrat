from data.fetch_chain import fetch_option_chain
from strategy.rank_strategies import rank_calls

if __name__ == "__main__":
    options, hist = fetch_option_chain("SPY")
    current_price = hist["Close"][-1]
    
    ranked = rank_calls(options, current_price)
    print(ranked[["strike", "lastPrice", "score", "expiry"]].head(10))