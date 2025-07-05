import numpy as np
from scipy.stats import lognorm
import pandas as pd
from .payoff_models import long_call, long_put, long_straddle, vertical_spread, payoff_curve, strategy_metrics

def _lognormal_pdf(S0, mu, sigma, grid):
    # Simple log-normal terminal distribution.
    scale = S0 * np.exp(mu)
    return lognorm.pdf(grid, s=sigma, scale=scale)

def rank_all_strategies(option_df, s0):
    ranked = []

    call_candidates = option_df[(option_df["type"] == "call") & (option_df["strike"] > s0)]
    if not call_candidates.empty:
        c = call_candidates.iloc[0]
        call_score = payoff_curve(long_call(c["strike"], c["lastPrice"]), np.array([s0 + 10]))[0]
        ranked.append({"type": "call", "score": call_score, **c})

    put_candidates = option_df[(option_df["type"] == "put") & (option_df["strike"] > s0)]
    if not put_candidates.empty:
        p = put_candidates.iloc[0]
        put_score = payoff_curve(long_put(p["strike"], p["lastPrice"]), np.array([s0 - 10]))[0]
        ranked.append({"type": "put", "score": put_score, **p})

    near_atm = option_df[np.abs(option_df["strike"] - s0) < 5]
    if not near_atm.empty:
        s = near_atm.iloc[0]
        straddle_score = payoff_curve(
            long_straddle(s["strike"], s["lastPrice"] / 2, s["lastPrice"] / 2), 
            np.array([s0 + 10])
        )[0]
        ranked.append({"type": "straddle", "score": straddle_score, **s})

    return pd.DataFrame(ranked).sort_values(by="score", ascending=False)
