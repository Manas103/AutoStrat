import pandas as pd
import numpy as np
from strategy.payoff_models import payoff_curve

def backtest_long_call(price_series, strike, premium):
    """Hold to expiry back-test."""
    final_price = price_series.iloc[-1]
    pnl = max(final_price - strike, 0) - premium
    return pnl

def run_backtest(price_series, strategy):
    final_price = price_series.iloc[-1]
    payoff = payoff_curve(strategy, np.array([final_price]))[0]
    return payoff