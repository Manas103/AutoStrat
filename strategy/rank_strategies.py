# strategy/rank_strategies.py
import numpy as np
from scipy.stats import lognorm
from payoff_models import (long_call, long_put, long_straddle, vertical_spread, payoff_curve, strategy_metrics)

def _lognormal_pdf(S0, mu, sigma, grid):
    """Simple log-normal terminal distribution."""
    scale = S0 * np.exp(mu)
    return lognorm.pdf(grid, s=sigma, scale=scale)

def rank_all_strategies(option_df, S0, mu=0.0, sigma=0.2):
    price_grid = np.linspace(0.5*S0, 1.5*S0, 200)
    pdf = _lognormal_pdf(S0, mu, sigma, price_grid)

    ranked_rows = []
    # Individual long calls/puts
    for _, row in option_df.iterrows():
        if row["type"] == "call":
            strat = long_call(row["strike"], row["lastPrice"])
        else:
            strat = long_put(row["strike"], row["lastPrice"])
        m = strategy_metrics(strat, price_grid, pdf)
        ranked_rows.append({**m, **row[["type","strike","lastPrice"]]})

    # Straddles (same strike call+put)
    atm_strikes = option_df["strike"].unique()
    for k in atm_strikes:
        c = option_df[(option_df.type=="call") & (option_df.strike==k)].iloc[0]
        p = option_df[(option_df.type=="put")  & (option_df.strike==k)].iloc[0]
        strat = long_straddle(k, c["lastPrice"], p["lastPrice"])
        m = strategy_metrics(strat, price_grid, pdf)
        ranked_rows.append({"type":"straddle","strike":k,
                            "lastPrice":strat["premium"], **m})
    ranked = (pd.DataFrame(ranked_rows)
              .assign(score=lambda d: d["EV"] / d["max_loss"].abs())
              .sort_values("score", ascending=False))
    return ranked