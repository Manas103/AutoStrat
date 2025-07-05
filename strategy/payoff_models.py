import numpy as np
import pandas as pd

# Leg Helpers
def leg_payoff(option_type, strike, qty, price_grid):
    """Return payoff of a single option leg at expiry."""
    if option_type == "call":
        return qty * np.maximum(price_grid - strike, 0)
    elif option_type == "put":
        return qty * np.maximum(strike - price_grid, 0)
    else:
        raise ValueError("option_type must be 'call' or 'put'")

# Strategies
def long_call(strike, premium):
    return {"legs": [("call", strike, +1)], "premium": premium}

def long_put(strike, premium):
    return {"legs": [("put", strike, +1)], "premium": premium}

def long_straddle(strike, prem_call, prem_put):
    return {
        "legs": [("call", strike, +1), ("put", strike, +1)],
        "premium": prem_call + prem_put,
    }

def vertical_spread(strike_long, prem_long, strike_short, prem_short,
                    direction="bull"):
    if direction == "bull":   # debit call spread
        legs = [("call", strike_long, +1), ("call", strike_short, -1)]
        net_premium = prem_long - prem_short
    else:                     # bear put spread
        legs = [("put", strike_long, +1), ("put", strike_short, -1)]
        net_premium = prem_long - prem_short
    return {"legs": legs, "premium": net_premium}

# Payoff curve and metrics
def payoff_curve(strategy, price_grid):
    payoff = -strategy["premium"] * np.ones_like(price_grid)
    for opt_type, strike, qty in strategy["legs"]:
        payoff += leg_payoff(opt_type, strike, qty, price_grid)
    return payoff

def strategy_metrics(strategy, price_grid, prob_density):
    """EV, breakevens, max risk, max reward."""
    payoff = payoff_curve(strategy, price_grid)
    ev = np.trapz(payoff * prob_density, price_grid)          # expected value
    max_gain = payoff.max()
    max_loss = payoff.min()
    breakevens = price_grid[np.isclose(payoff, 0, atol=1e-2)]
    return {"EV": ev, "max_gain": max_gain,
            "max_loss": max_loss, "breakevens": breakevens}
