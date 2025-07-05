import numpy as np

def score_long_call(row, current_price, iv_rank=0.5):
    strike = row['strike']
    premium = row['lastPrice']
    dte = row['dte']
    
    # Breakeven = strike + premium
    breakeven = strike + premium
    upside = max(current_price * 1.1 - strike, 0) - premium  # Assume 10% rally
    ev = upside - premium
    
    score = ev / premium if premium > 0 else 0
    score *= (1 + iv_rank)  # favor low IV
    return score

def rank_calls(option_df, current_price):
    calls = option_df[(option_df['type'] == 'call') & (option_df['inTheMoney'] == False)]
    ranked = calls.copy()
    ranked['score'] = ranked.apply(lambda row: score_long_call(row, current_price), axis=1)
    return ranked.sort_values(by="score", ascending=False)
