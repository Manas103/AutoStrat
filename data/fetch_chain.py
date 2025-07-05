import yfinance as yf
import pandas as pd
from datetime import datetime

def fetch_option_chain(ticker="SPY", expiry=None):
    stock = yf.Ticker(ticker)
    
    # Use nearest expiry if none is given
    if expiry is None:
        expiry = stock.options[0]
    
    opt_chain = stock.option_chain(expiry)
    
    calls = opt_chain.calls.copy()
    puts = opt_chain.puts.copy()

    calls["type"] = "call"
    puts["type"] = "put"

    options = pd.concat([calls, puts], ignore_index=True)
    options["expiry"] = pd.to_datetime(expiry)
    options["dte"] = (options["expiry"] - datetime.now()).dt.days

    return options, stock.history(period="7d")  # returns option df and stock history
