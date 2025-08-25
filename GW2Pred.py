# Build GW2 predictions for Premier League 2025/26 using a simple rating+probability model
# Updated after GW1 results and recent transfers (including Ebere Eze to Arsenal)
import math
import itertools
import pandas as pd
from collections import defaultdict

# --- Updated team ratings after GW1 results and transfers ---
# Adjustments based on GW1 performance and new signings like Eze to Arsenal
#
# GW1 Results Summary:
# Liverpool 4-2 Bournemouth (Liverpool impressive attack, Bournemouth leaky defense)
# Aston Villa 0-0 Newcastle United (Both teams underwhelming, cagey affair)
# Brighton 1-1 Fulham (Even contest, both showed decent quality)
# Sunderland 3-0 West Ham (Massive upset, Sunderland excellent, West Ham poor)
# Tottenham 3-0 Burnley (Spurs looked sharp, Burnley struggled)
# Manchester City 4-0 Wolves (City dominant as expected, Wolves outclassed)
# Nottingham Forest 3-1 Brentford (Forest impressive at home, Brentford disappointing)
# Chelsea 0-0 Crystal Palace (Both teams lacked cutting edge)
# Arsenal 1-0 Manchester United (Arsenal edged it, United looked poor)
# Leeds United 1-0 Everton (Leeds solid at home, Everton away struggles continue)
#
# Key Transfer: Ebere Eze moved from Crystal Palace to Arsenal for £68m
# This strengthens Arsenal's creative options significantly
ratings = {
    "Manchester City": 1.30,      # +0.10 (4-0 vs Wolves, dominant)
    "Arsenal": 1.25,              # +0.10 (1-0 vs Man Utd + Eze signing boost)
    "Liverpool": 1.35,            # +0.10 (4-2 vs Bournemouth, strong attack)
    "Tottenham Hotspur": 0.70,    # +0.10 (3-0 vs Burnley, convincing)
    "Aston Villa": 0.40,          # -0.10 (0-0 vs Newcastle, underwhelming)
    "Chelsea": 0.35,              # -0.10 (0-0 vs Palace, lackluster)
    "Newcastle United": 0.40,     # +0.05 (0-0 vs Villa away, solid defensive display)
    "Manchester United": 0.20,    # -0.10 (0-1 vs Arsenal, poor performance)
    "Brighton & Hove Albion": 0.15,  # +0.05 (1-1 vs Fulham, decent showing)
    "West Ham United": -0.20,     # -0.10 (0-3 vs Sunderland, shocking defeat)
    "Brentford": 0.00,           # -0.10 (1-3 vs Forest, disappointing)
    "Everton": -0.15,            # -0.10 (0-1 vs Leeds, poor away form)
    "Wolverhampton Wanderers": -0.20,  # -0.10 (0-4 vs City, heavy defeat)
    "Nottingham Forest": 0.00,   # +0.10 (3-1 vs Brentford, impressive win)
    "Crystal Palace": 0.10,      # +0.05 (0-0 vs Chelsea away, good point)
    "Fulham": 0.05,              # +0.05 (1-1 vs Brighton away, resilient)
    "Leeds United": -0.05,       # +0.10 (1-0 vs Everton, good home win)
    "Bournemouth": -0.30,        # -0.10 (2-4 vs Liverpool, defensive issues)
    "Burnley": -0.45,            # -0.10 (0-3 vs Spurs, struggled badly)
    "Sunderland": 0.25,          # +0.15 (3-0 vs West Ham, outstanding performance)
}

# --- Fixtures for GW2 (home vs away) ---
fixtures = [
    ("Arsenal", "Brighton & Hove Albion"),
    ("Bournemouth", "Newcastle United"),
    ("Burnley", "Liverpool"),
    ("Crystal Palace", "West Ham United"),
    ("Everton", "Tottenham Hotspur"),
    ("Fulham", "Leeds United"),
    ("Manchester United", "Nottingham Forest"),
    ("Sunderland", "Aston Villa"),
    ("Wolverhampton Wanderers", "Chelsea"),
    ("Brentford", "Manchester City"),
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

# Order matches roughly by kickoff window (Fri -> Mon) based on typical GW2 layout
order = [
    "Arsenal vs Brighton & Hove Albion",
    "Bournemouth vs Newcastle United", 
    "Burnley vs Liverpool",
    "Crystal Palace vs West Ham United",
    "Everton vs Tottenham Hotspur",
    "Fulham vs Leeds United",
    "Manchester United vs Nottingham Forest",
    "Sunderland vs Aston Villa",
    "Wolverhampton Wanderers vs Chelsea",
    "Brentford vs Manchester City",
]
df["sort"] = df["Match"].apply(lambda x: order.index(x) if x in order else 99)
df = df.sort_values("sort").drop(columns=["sort"]).reset_index(drop=True)

# print the GW2 predictions DataFrame
print("=" * 80)
print("PREMIER LEAGUE GAMEWEEK 2 PREDICTIONS (2025/26 Season)")
print("Updated after GW1 results and recent transfers")
print("=" * 80)
print(df.to_string(index=False))
