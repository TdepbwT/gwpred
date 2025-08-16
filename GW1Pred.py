# Build GW1 predictions for Premier League 2025/26 using a simple rating+probability model
import math
import itertools
import pandas as pd
from collections import defaultdict

# --- Teams & rough pre-season power ratings (goal-difference-ish scale) ---
ratings = {
    "Manchester City": 1.20,
    "Arsenal": 1.00,
    "Liverpool": 1.25,
    "Tottenham": 0.60,
    "Aston Villa": 0.50,
    "Chelsea": 0.40,
    "Newcastle United": 0.35,
    "Manchester United": 0.30,
    "Brighton": 0.10,
    "West Ham": 0.10,
    "Brentford": 0.10,
    "Everton": -0.05,
    "Wolves": -0.10,
    "Nottingham Forest": -0.10,
    "Crystal Palace": 0.05,
    "Fulham": 0.00,
    "Leeds United": -0.15,
    "Bournemouth": -0.20,
    "Burnley": -0.35,
    "Sunderland": -0.10,
}

# --- Fixtures for GW1 (home vs away) ---
fixtures = [
    ("Liverpool", "Bournemouth"),
    ("Aston Villa", "Newcastle United"),
    ("Brighton", "Fulham"),
    ("Sunderland", "West Ham"),
    ("Tottenham", "Burnley"),
    ("Wolves", "Manchester City"),
    ("Nottingham Forest", "Brentford"),
    ("Chelsea", "Crystal Palace"),
    ("Manchester United", "Arsenal"),
    ("Leeds United", "Everton"),
]

# --- Model parameters ---
HOME_ADV = 0.25  # home advantage in rating units (roughly ~0.25 goals)
BASE_DRAW = 0.28  # baseline draw rate
DRAW_DECAY = 0.75  # fewer draws for mismatches
SIGMOID_K = 1.3  # sharpness of win/loss split after removing draws

# Expected goals mapping (for a likely-scoreline estimate)
BASE_MU = 1.35   # league-average goals per team per game
BETA = 0.45      # how much expected goals tilt with rating diff

def probabilities(home, away):
    # rating diff including home advantage
    diff = (ratings[home] + HOME_ADV) - ratings[away]
    # draw probability shrinks as mismatch growss
    p_draw = BASE_DRAW * math.exp(-DRAW_DECAY * abs(diff))
    # allocate remaining mass via a sigmoid
    p_home_given_not_draw = 1 / (1 + math.exp(-SIGMOID_K * diff))
    p_home = (1 - p_draw) * p_home_given_not_draw
    p_away = 1 - p_draw - p_home
    return p_home, p_draw, p_away, diff

def exp_goals(diff):
    mu_home = BASE_MU * math.exp(BETA * diff)
    mu_away = BASE_MU * math.exp(-BETA * diff)
    return mu_home, mu_away

# Poisson mass function (for likely scoreline mode up to 6 goals each)
def poisson_pmf(k, lam):
    return math.exp(-lam) * (lam ** k) / math.factorial(k)

def most_likely_score(mu_h, mu_a, max_goals=6):
    best = (0, 0)  # Default to 0-0 instead of None
    best_p = -1.0
    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            p = poisson_pmf(h, mu_h) * poisson_pmf(a, mu_a)
            if p > best_p:
                best_p = p
                best = (h, a)
    return best

rows = []
for home, away in fixtures:
    pH, pD, pA, diff = probabilities(home, away)
    mu_h, mu_a = exp_goals(diff)
    ml_h, ml_a = most_likely_score(mu_h, mu_a, max_goals=6)
    rows.append({
        "Match": f"{home} vs {away}",
        "Home %": round(100 * pH, 1),
        "Draw %": round(100 * pD, 1),
        "Away %": round(100 * pA, 1),
        "Fair Home Odds": round(1 / pH, 2),
        "Fair Draw Odds": round(1 / pD, 2),
        "Fair Away Odds": round(1 / pA, 2),
        "Exp Goals (Home)": round(mu_h, 2),
        "Exp Goals (Away)": round(mu_a, 2),
        "Most Likely Score": f"{ml_h}-{ml_a}",
        "Model diff (H-A)": round(diff, 2),
    })

df = pd.DataFrame(rows)

# Order matches roughly by kickoff window (Fri -> Mon) based on typical GW1 layout
order = [
    "Liverpool vs Bournemouth",
    "Aston Villa vs Newcastle United",
    "Brighton vs Fulham",
    "Sunderland vs West Ham",
    "Tottenham vs Burnley",
    "Wolves vs Manchester City",
    "Nottingham Forest vs Brentford",
    "Chelsea vs Crystal Palace",
    "Manchester United vs Arsenal",
    "Leeds United vs Everton",
]
df["sort"] = df["Match"].apply(lambda x: order.index(x) if x in order else 99)
df = df.sort_values("sort").drop(columns=["sort"]).reset_index(drop=True)

# print the DataFrame
print(df.to_string(index=False))
