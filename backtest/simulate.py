import numpy as np
import pandas as pd
from scipy.stats import norm
from strategy.payoff_models import payoff_curve

def run_backtest_with_exit(price_series, strategy,
                           tp_pct=0.30,
                           sl_pct=-0.20):
    expiry  = pd.to_datetime(strategy.get("expiry",
                                          price_series.index[-1]))
    premium = strategy["premium"]
    r, sigma = 0.01, 0.20

    # 2) daily mark‐to‐market
    for ts in price_series.index:          # iterate over index only
        S = float(price_series.loc[ts])    # fetch the price scalar
        T = max((expiry - ts).days / 365, 1e-6)

        # 3) price each leg with Black‐Scholes
        pnl_legs = []
        for opt_type, K, qty in strategy["legs"]:
            K = float(K)
            d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
            d2 = d1 - sigma*np.sqrt(T)
            if opt_type == "call":
                price = S * norm.cdf(d1) - K * np.exp(-r*T) * norm.cdf(d2)
            else:  # put
                price = K * np.exp(-r*T) * norm.cdf(-d2) - S * norm.cdf(-d1)
            pnl_legs.append(qty * price)

        pnl = sum(pnl_legs) - premium
        ret = pnl / premium

        # 4) exit check
        if ret >= tp_pct or ret <= sl_pct:
            return pnl, ts

    # 5) if never hit TP/SL, exit at the last date
    return pnl, price_series.index[-1]
