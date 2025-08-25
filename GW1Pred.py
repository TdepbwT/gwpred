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
    "Tottenham Hotspur": 0.75,    # +0.10 (3-0 vs Burnley, convincing)
    "Aston Villa": 0.40,          # -0.10 (0-0 vs Newcastle, underwhelming)
    "Chelsea": 0.65,              # -0.10 (0-0 vs Palace, lackluster)
    "Newcastle United": 0.40,     # +0.05 (0-0 vs Villa away, solid defensive display)
    "Manchester United": 0.25,    # -0.10 (0-1 vs Arsenal, poor performance)
    "Brighton & Hove Albion": 0.15,  # +0.05 (1-1 vs Fulham, decent showing)
    "West Ham United": -0.45,     # -0.10 (0-3 vs Sunderland, shocking defeat)
    "Brentford": 0.00,           # -0.10 (1-3 vs Forest, disappointing)
    "Everton": -0.15,            # -0.10 (0-1 vs Leeds, poor away form)
    "Wolverhampton Wanderers": -0.15,  # -0.10 (0-4 vs City, heavy defeat)
    "Nottingham Forest": 0.15,   # +0.10 (3-1 vs Brentford, impressive win)
    "Crystal Palace": 0.05,      # +0.05 (0-0 vs Chelsea away, good point)
    "Fulham": 0.05,              # +0.05 (1-1 vs Brighton away, resilient)
    "Leeds United": -0.05,       # +0.10 (1-0 vs Everton, good home win)
    "Bournemouth": -0.30,        # -0.10 (2-4 vs Liverpool, defensive issues)
    "Burnley": -0.45,            # -0.10 (0-3 vs Spurs, struggled badly)
    "Sunderland": 0.30,          # +0.15 (3-0 vs West Ham, outstanding performance)
}

# --- Fixtures for GW2 (home vs away) ---
fixtures = [
    ("Arsenal", "Leeds United"),
    ("Bournemouth", "Wolverhampton Wanderers"),
    ("Burnley", "Sunderland"),
    ("Crystal Palace", "Nottingham Forest"),
    ("Everton", "Brighton & Hove Albion"),
    ("Fulham", "Manchester United"),
    ("Newcastle United", "Liverpool"),
    ("Manchester City", "Tottenham Hotspur"),
    ("West Ham United", "Chelsea"),
    ("Brentford", "Aston Villa"),
]

# --- Model parameters ---
# Enhanced parameters to account for Big 6 dominance in recent Premier League history
#
# HYPERPARAMETER TUNING RATIONALE:
# 1. BASE_DRAW reduced from 0.28 → 0.24: Big 6 teams historically avoid draws more
# 2. DRAW_DECAY increased from 0.75 → 0.85: Quality gaps more pronounced
# 3. SIGMOID_K increased from 1.3 → 1.5: Sharper win/loss probabilities
# 4. BASE_MU increased from 1.35 → 1.40: Higher scoring in modern Premier League
# 5. BETA increased from 0.45 → 0.60: Rating differences have bigger impact (Big 6 dominance)
# 6. Added BIG_6_BONUS: 0.15 extra rating when Big 6 faces non-Big 6
# 7. Added BIG_6_CONSISTENCY: 1.2x multiplier for more predictable Big 6 outcomes
#
HOME_ADV = 0.25  # home advantage in rating units (roughly ~0.25 goals)
BASE_DRAW = 0.24  # baseline draw rate (reduced from 0.28 - Big 6 tend to avoid draws)
DRAW_DECAY = 0.85  # fewer draws for mismatches (increased from 0.75)
SIGMOID_K = 1.5  # sharpness of win/loss split after removing draws (increased from 1.3)

# Expected goals mapping (enhanced for Big 6 dominance)
BASE_MU = 1.40   # league-average goals per team per game (increased from 1.35)
BETA = 0.60      # how much expected goals tilt with rating diff (increased from 0.45 for Big 6 dominance)

# Big 6 teams for additional adjustments
BIG_6 = {"Manchester City", "Arsenal", "Liverpool", "Chelsea", "Manchester United", "Tottenham Hotspur"}

# Additional Big 6 specific parameters
BIG_6_BONUS = 0.15  # Extra rating boost when Big 6 plays non-Big 6
BIG_6_CONSISTENCY = 1.2  # Multiplier for reducing variance in Big 6 performances

def probabilities(home, away):
    # Enhanced probability calculation accounting for Big 6 dominance
    base_diff = (ratings[home] + HOME_ADV) - ratings[away]
    
    # Apply Big 6 dominance adjustments
    diff = base_diff
    
    # Big 6 vs non-Big 6 bonus (historical dominance factor)
    if home in BIG_6 and away not in BIG_6:
        diff += BIG_6_BONUS
    elif away in BIG_6 and home not in BIG_6:
        diff -= BIG_6_BONUS
    
    # Enhanced draw probability calculation
    # Big 6 teams historically have fewer draws due to quality gap
    draw_modifier = 1.0
    if home in BIG_6 or away in BIG_6:
        draw_modifier = 0.85  # Reduce draw probability for Big 6 involvement
    
    p_draw = BASE_DRAW * draw_modifier * math.exp(-DRAW_DECAY * abs(diff))
    
    # Enhanced sigmoid for win/loss split (sharper for Big 6)
    sigmoid_k = SIGMOID_K
    if home in BIG_6 or away in BIG_6:
        sigmoid_k *= BIG_6_CONSISTENCY  # More predictable outcomes
    
    p_home_given_not_draw = 1 / (1 + math.exp(-sigmoid_k * diff))
    p_home = (1 - p_draw) * p_home_given_not_draw
    p_away = 1 - p_draw - p_home
    
    return p_home, p_draw, p_away, diff

def exp_goals(diff):
    # Enhanced expected goals calculation with Big 6 adjustments
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
    "West Ham United vs Chelsea",
    "Manchester City vs Tottenham Hotspur", 
    "Bournemouth vs Wolverhampton Wanderers",
    "Brentford vs Aston Villa",
    "Burnley vs Sunderland",
    "Arsenal vs Leeds United",
    "Crystal Palace vs Nottingham Forest",
    "Everton vs Brighton & Hove Albion",
    "Fulham vs Manchester United",
    "Newcastle United vs Liverpool",
]
df["sort"] = df["Match"].apply(lambda x: order.index(x) if x in order else 99)
df = df.sort_values("sort").drop(columns=["sort"]).reset_index(drop=True)

# print the GW2 predictions DataFrame
print("=" * 80)
print("PREMIER LEAGUE GAMEWEEK 2 PREDICTIONS (2025/26 Season)")
print("Updated after GW1 results and recent transfers")
print("=" * 80)
print(df.to_string(index=False))

# Save predictions to CSV file with enhanced hyperparameters
csv_filename = "gw2_predictions_enhanced_big6_2025-26.csv"
df.to_csv(csv_filename, index=False)
print(f"\nPredictions saved to: {csv_filename}")
print(f"File contains {len(df)} match predictions with enhanced Big 6 hyperparameters.")
print(f"Key enhancements: BETA={BETA}, BASE_DRAW={BASE_DRAW}, SIGMOID_K={SIGMOID_K}, BIG_6_BONUS={BIG_6_BONUS}")



