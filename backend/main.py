"""
FastAPI backend for Premier League Prediction System
Serves predictions for multiple gameweeks with dynamic rating updates
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import math
import json
from datetime import datetime
from pathlib import Path

app = FastAPI(
    title="Premier League Prediction API",
    description="API for predicting Premier League match outcomes using team ratings",
    version="1.0.0"
)

# Enable CORS for React frontend
import os
allowed_origins = [
    "http://localhost:3000", 
    "http://localhost:5173",
]
# Add environment variable support for production
cors_origins = os.getenv("CORS_ORIGINS", "")
if cors_origins:
    for origin in cors_origins.split(","):
        origin = origin.strip()
        if origin:
            allowed_origins.append(origin)
            
else:
    allowed_origins.extend(["https://gwpred.vercel.app",
                            "https://gwpred-2z4z.vercel.app",
                            "https://gwpredictor.up.railway.app"])

print(f"Allowed CORS origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API responses
class MatchPrediction(BaseModel):
    match: str
    home_team: str
    away_team: str
    home_percentage: float
    draw_percentage: float
    away_percentage: float
    fair_home_odds: float
    fair_draw_odds: float
    fair_away_odds: float
    exp_goals_home: float
    exp_goals_away: float
    most_likely_score: str
    rating_diff: float  # Changed from model_diff to avoid Pydantic warning
    
    model_config = {"protected_namespaces": ()}

class GameweekPredictions(BaseModel):
    gameweek: int
    season: str
    predictions: List[MatchPrediction]
    last_updated: str
    total_matches: int

class TeamRating(BaseModel):
    team: str
    rating: float
    effective_rating: float  # Rating including form boost
    form_boost: float        # Form boost applied
    change_from_previous: Optional[float] = None
    reason: Optional[str] = None

class TeamRatingsResponse(BaseModel):
    season: str
    gameweek: int
    ratings: List[TeamRating]
    last_updated: str

# Current team ratings (post-GW4 results)
# Updated based on GW2 & GW3 results and major summer 2025 transfers
CURRENT_RATINGS = {
    "Manchester City": 1.26,      # +0.05 (3-0 win vs Man Utd, strong performance)
    "Arsenal": 1.40,              # +0.05 (3-0 win vs Nottingham Forest, good form continues)
    "Liverpool": 1.43,            # +0.03 (1-0 win vs Burnley, maintaining form)
    "Tottenham Hotspur": 0.77,    # +0.05 (3-0 win vs West Ham, good performance)
    "Aston Villa": 0.25,          # -0.02 (0-0 draw vs Everton, still struggling)
    "Chelsea": 0.79,              # -0.02 (2-2 draw vs Brentford, dropped points)
    "Newcastle United": 0.41,     # +0.03 (1-0 win vs Wolves, solid result)
    "Manchester United": 0.26,    # -0.08 (0-3 loss vs Man City, poor performance)
    "Brighton & Hove Albion": 0.16, # -0.05 (1-2 loss vs Bournemouth, disappointing)
    "West Ham United": -0.37,     # -0.10 (0-3 loss vs Spurs, heavy defeat)
    "Brentford": -0.04,           # +0.02 (2-2 draw vs Chelsea, good point)
    "Everton": 0.12,              # +0.02 (0-0 draw vs Villa, decent point)
    "Wolverhampton Wanderers": -0.31, # -0.05 (0-1 loss vs Newcastle, another loss)
    "Nottingham Forest": -0.08,   # -0.05 (0-3 loss vs Arsenal, heavy defeat)
    "Crystal Palace": 0.15,       # +0.03 (0-0 draw vs Sunderland, solid point)
    "Fulham": 0.12,               # +0.03 (1-0 win vs Leeds, good result)
    "Leeds United": -0.11,        # -0.05 (0-1 loss vs Fulham, another loss)
    "Bournemouth": -0.08,         # +0.05 (2-1 win vs Brighton, excellent result)
    "Burnley": -0.45,             # -0.05 (0-1 loss vs Liverpool, another loss)
    "Sunderland": 0.30,           # -0.02 (0-0 draw vs Palace, missed opportunity)
}

# Team form tracking for last 5 games (updated with GW7 results)
TEAM_FORM = {
    "Manchester City": [0, 1, 0.5, 1, 1],    # L-W-D-W-W (last 5 games)
    "Arsenal": [0, 1, 0.5, 1, 1],            # L-W-D-W-W
    "Liverpool": [1, 1, 1, 0, 0],          # W-W-W-L-L
    "Tottenham Hotspur": [0, 1, 0.5, 0.5, 1],  # L-W-D-D-W
    "Aston Villa": [0, 0.5, 0.5, 1, 1],      # L-D-D-W-W
    "Chelsea": [1, 0.5, 0, 0, 1],          # W-D-L-L-W
    "Newcastle United": [0.5, 1, 0.5, 0, 1],   # D-W-D-L-W
    "Manchester United": [1, 0, 1, 0, 1],  # W-D-W-L-W
    "Brighton & Hove Albion": [1, 0, 0.5, 1, 0.5], # W-L-D-W-D
    "West Ham United": [1, 0, 0, 0.5, 0],    # W-L-L-D-L
    "Brentford": [0, 0.5, 0, 1, 0],        # L-D-L-W-L
    "Everton": [1, 0.5, 0, 0.5, 1],          # W-D-L-D-W
    "Wolverhampton Wanderers": [0, 0, 0, 0.5, 0.5], # L-L-L-D-D
    "Nottingham Forest": [0, 0, 0.5, 0, 0],  # L-L-D-L-L
    "Crystal Palace": [1, 0.5, 1, 1, 0],   # W-D-W-W-L
    "Fulham": [0, 1, 1, 0, 0],             # D-W-W-L-L
    "Leeds United": [0.5, 0, 1, 0.5, 0],     # D-L-W-D-L
    "Bournemouth": [1, 1, 0.5, 0.5, 1],        # W-W-D-D-W
    "Burnley": [0, 0, 0.5, 0, 0],            # L-L-D-L-L
    "Sunderland": [1, 0.5, 0.5, 1, 0],       # W-D-D-W-L
}

# Match history - add GW4 results
MATCH_HISTORY = {
    # GW1 Results
    1: {
        "Liverpool vs Bournemouth": {"Liverpool": 4, "Bournemouth": 2},
        "Aston Villa vs Newcastle United": {"Aston Villa": 0, "Newcastle United": 0},
        "Brighton & Hove Albion vs Fulham": {"Brighton & Hove Albion": 1, "Fulham": 1},
        "Sunderland vs West Ham United": {"Sunderland": 3, "West Ham United": 0},
        "Tottenham Hotspur vs Burnley": {"Tottenham Hotspur": 3, "Burnley": 0},
        "Manchester City vs Wolverhampton Wanderers": {"Manchester City": 4, "Wolverhampton Wanderers": 0},
        "Nottingham Forest vs Brentford": {"Nottingham Forest": 3, "Brentford": 1},
        "Chelsea vs Crystal Palace": {"Chelsea": 0, "Crystal Palace": 0},
        "Arsenal vs Manchester United": {"Arsenal": 1, "Manchester United": 0},
        "Leeds United vs Everton": {"Leeds United": 1, "Everton": 0},
    },
    # GW2 Results
    2: {
        "Arsenal vs Leeds United": {"Arsenal": 5, "Leeds United": 0},
        "Bournemouth vs Wolverhampton Wanderers": {"Bournemouth": 1, "Wolverhampton Wanderers": 0},
        "Burnley vs Sunderland": {"Burnley": 2, "Sunderland": 0},
        "Crystal Palace vs Nottingham Forest": {"Crystal Palace": 1, "Nottingham Forest": 1},
        "Everton vs Brighton & Hove Albion": {"Everton": 2, "Brighton & Hove Albion": 0},
        "Fulham vs Manchester United": {"Fulham": 2, "Manchester United": 2},
        "Newcastle United vs Liverpool": {"Newcastle United": 2, "Liverpool": 3},
        "Manchester City vs Tottenham Hotspur": {"Manchester City": 0, "Tottenham Hotspur": 2},
        "West Ham United vs Chelsea": {"West Ham United": 1, "Chelsea": 5},
        "Brentford vs Aston Villa": {"Brentford": 1, "Aston Villa": 0},
    },
    # GW3 Results
    3: {
        "Chelsea vs Fulham": {"Chelsea": 2, "Fulham": 0},
        "Manchester United vs Burnley": {"Manchester United": 3, "Burnley": 2},
        "Tottenham Hotspur vs Bournemouth": {"Tottenham Hotspur": 0, "Bournemouth": 1},
        "Sunderland vs Brentford": {"Sunderland": 2, "Brentford": 1},
        "Wolverhampton Wanderers vs Everton": {"Wolverhampton Wanderers": 2, "Everton": 3},
        "Leeds United vs Newcastle United": {"Leeds United": 0, "Newcastle United": 0},
        "Brighton & Hove Albion vs Manchester City": {"Brighton & Hove Albion": 2, "Manchester City": 1},
        "Nottingham Forest vs West Ham United": {"Nottingham Forest": 0, "West Ham United": 3},
        "Liverpool vs Arsenal": {"Liverpool": 1, "Arsenal": 0},
        "Aston Villa vs Crystal Palace": {"Aston Villa": 0, "Crystal Palace": 3},
    },
    # GW4 Results
    4: {
        "Manchester City vs Manchester United": {"Manchester City": 3, "Manchester United": 0},
        "Burnley vs Liverpool": {"Burnley": 0, "Liverpool": 1},
        "Brentford vs Chelsea": {"Brentford": 2, "Chelsea": 2},
        "West Ham United vs Tottenham Hotspur": {"West Ham United": 0, "Tottenham Hotspur": 3},
        "Bournemouth vs Brighton & Hove Albion": {"Bournemouth": 2, "Brighton & Hove Albion": 1},
        "Crystal Palace vs Sunderland": {"Crystal Palace": 0, "Sunderland": 0},
        "Everton vs Aston Villa": {"Everton": 0, "Aston Villa": 0},
        "Fulham vs Leeds United": {"Fulham": 1, "Leeds United": 0},
        "Newcastle United vs Wolverhampton Wanderers": {"Newcastle United": 1, "Wolverhampton Wanderers": 0},
        "Arsenal vs Nottingham Forest": {"Arsenal": 3, "Nottingham Forest": 0},
    }
}

# Rating history tracking (add GW4 data)
RATING_HISTORY = {
    "Manchester City": [1.15, 1.20, 1.20, 1.21, 1.26],
    "Arsenal": [1.23, 1.35, 1.35, 1.35, 1.40],
    "Liverpool": [1.42, 1.45, 1.45, 1.40, 1.43],
    "Tottenham Hotspur": [0.74, 0.70, 0.70, 0.72, 0.77],
    "Aston Villa": [0.30, 0.25, 0.25, 0.27, 0.25],
    "Chelsea": [0.69, 0.75, 0.75, 0.81, 0.79],
    "Newcastle United": [0.33, 0.35, 0.35, 0.38, 0.41],
    "Manchester United": [0.23, 0.30, 0.30, 0.34, 0.26],
    "Brighton & Hove Albion": [0.20, 0.25, 0.25, 0.21, 0.16],
    "West Ham United": [-0.38, -0.25, -0.25, -0.27, -0.37],
    "Brentford": [0.03, -0.05, -0.05, -0.06, -0.04],
    "Everton": [-0.03, 0.05, 0.05, 0.10, 0.12],
    "Wolverhampton Wanderers": [-0.23, -0.20, -0.20, -0.26, -0.31],
    "Nottingham Forest": [0.04, 0.00, 0.00, -0.03, -0.08],
    "Crystal Palace": [0.09, 0.15, 0.15, 0.12, 0.15],
    "Fulham": [0.05, 0.10, 0.10, 0.09, 0.12],
    "Leeds United": [-0.08, -0.05, -0.05, -0.06, -0.11],
    "Bournemouth": [-0.15, -0.10, -0.10, -0.13, -0.08],
    "Burnley": [-0.39, -0.35, -0.35, -0.40, -0.45],
    "Sunderland": [0.29, 0.35, 0.35, 0.32, 0.30],
}

def calculate_form_boost(team: str) -> float:
    """
    Calculate form boost based on recent results and opposition strength
    
    Args:
        team: Team name
        
    Returns:
        Form boost to apply to base rating
    """
    if team not in TEAM_FORM:
        return 0.0
    
    form_results = TEAM_FORM[team]
    
    # Calculate points from last 5 games (3 for win, 1 for draw, 0 for loss)
    total_points = sum([3 if r == 1 else 1 if r == 0.5 else 0 for r in form_results])
    
    # Base form rating (0-15 points possible)
    form_rating = total_points / 15.0  # Normalize to 0-1
    
    
    # Calculate form boost (max 0.2 boost for perfect form)
    form_boost = (form_rating - 0.5) * 0.4 
    
    return round(form_boost, 3)

def get_effective_rating(team: str) -> float:
    """
    Get team rating with form boost applied
    
    Args:
        team: Team name
        
    Returns:
        Effective rating including form boost
    """
    base_rating = CURRENT_RATINGS.get(team, 0.0)
    form_boost = calculate_form_boost(team)
    return base_rating + form_boost

def update_ratings_after_gameweek(results: Dict[str, Dict[str, int]]):
    """
    Update team ratings based on gameweek results with form consideration
    
    Args:
        results: Dictionary of match results
        Format: {
            "Arsenal vs Leeds United": {"Arsenal": 2, "Leeds United": 1},
            "Chelsea vs Manchester City": {"Chelsea": 1, "Manchester City": 3}
        }
    """
    global CURRENT_RATINGS, TEAM_FORM
    
    for match, score in results.items():
        teams = list(score.keys())
        home_team, away_team = teams[0], teams[1]
        home_goals, away_goals = score[home_team], score[away_team]
        
        # Use effective ratings (with form) for probability calculation
        home_effective = get_effective_rating(home_team)
        away_effective = get_effective_rating(away_team)
        
        # Calculate expected probabilities using effective ratings
        base_diff = (home_effective + HOME_ADV) - away_effective
        
        # Apply Big 6 dominance adjustments
        diff = base_diff
        if home_team in BIG_6 and away_team not in BIG_6:
            diff += BIG_6_BONUS
        elif away_team in BIG_6 and home_team not in BIG_6:
            diff -= BIG_6_BONUS
        
        # Enhanced draw probability calculation
        draw_modifier = 1.0
        if home_team in BIG_6 or away_team in BIG_6:
            draw_modifier = 0.85
        
        p_draw = BASE_DRAW * draw_modifier * math.exp(-DRAW_DECAY * abs(diff))
        
        # Enhanced sigmoid for win/loss split
        sigmoid_k = SIGMOID_K
        if home_team in BIG_6 or away_team in BIG_6:
            sigmoid_k *= BIG_6_CONSISTENCY
        
        p_home_given_not_draw = 1 / (1 + math.exp(-sigmoid_k * diff))
        expected_home = (1 - p_draw) * p_home_given_not_draw
        expected_away = 1 - p_draw - expected_home
        
        # Determine actual result
        if home_goals > away_goals:  # Home win
            actual_result = [1, 0, 0]
        elif home_goals < away_goals:  # Away win
            actual_result = [0, 0, 1]
        else:  # Draw
            actual_result = [0, 1, 0]
        
        expected_result = [expected_home, p_draw, expected_away]
        
        # Calculate surprise factor and adjust ratings
        surprise_factor = 0.08  # Reduced from 0.1 to account for form system
        home_adjustment = surprise_factor * (actual_result[0] - expected_result[0])
        away_adjustment = surprise_factor * (actual_result[2] - expected_result[2])
        
        CURRENT_RATINGS[home_team] += home_adjustment
        CURRENT_RATINGS[away_team] += away_adjustment
        
        # Update form tracking (1 for win, 0.5 for draw, 0 for loss)
        if home_goals > away_goals:
            TEAM_FORM[home_team].append(1)
            TEAM_FORM[away_team].append(0)
        elif home_goals < away_goals:
            TEAM_FORM[home_team].append(0)
            TEAM_FORM[away_team].append(1)
        else:
            TEAM_FORM[home_team].append(0.5)
            TEAM_FORM[away_team].append(0.5)
        
        # Keep only last 5 games
        TEAM_FORM[home_team] = TEAM_FORM[home_team][-5:]
        TEAM_FORM[away_team] = TEAM_FORM[away_team][-5:]

# Gameweek fixtures - Add new gameweeks here
GAMEWEEK_FIXTURES = {
    2: [
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
    ],
    3: [
        ("Liverpool", "Arsenal"),
        ("Chelsea", "Fulham"),
        ("Tottenham Hotspur", "Bournemouth"),
        ("Manchester United", "Burnley"),
        ("Aston Villa", "Crystal Palace"),
        ("Brighton & Hove Albion", "Manchester City"),
        ("Leeds United", "Newcastle United"),
        ("Nottingham Forest", "West Ham United"),
        ("Wolverhampton Wanderers", "Everton"),
        ("Sunderland", "Brentford"),
    ],
    4: [
        ("Arsenal", "Nottingham Forest"),
        ("Bournemouth", "Brighton & Hove Albion"),
        ("Crystal Palace", "Sunderland"),
        ("Everton", "Aston Villa"),
        ("Fulham", "Leeds United"),
        ("Newcastle United", "Wolverhampton Wanderers"),
        ("West Ham United", "Tottenham Hotspur"),
        ("Brentford", "Chelsea"),
        ("Burnley", "Liverpool"),
        ("Manchester City", "Manchester United"),
    ],
    5: [
        ("Liverpool", "Everton"),
        ("Brighton & Hove Albion", "Tottenham Hotspur"),
        ("Burnley", "Nottingham Forest"),
        ("West Ham United", "Crystal Palace"),
        ("Wolverhampton Wanderers", "Leeds United"),
        ("Manchester United", "Chelsea"),
        ("Fulham", "Brentford"),
        ("Bournemouth", "Newcastle United"),
        ("Sunderland", "Aston Villa"),
        ("Arsenal", "Manchester City"),
    ],
    6: [
        ("Brentford", "Manchester United"),
        ("Chelsea", "Brighton & Hove Albion"),
        ("Crystal Palace", "Liverpool"),
        ("Leeds United", "Bournemouth"),
        ("Manchester City", "Burnley"),
        ("Nottingham Forest", "Sunderland"),
        ("Tottenham Hotspur", "Wolverhampton Wanderers"),
        ("Aston Villa", "Fulham"),
        ("Newcastle United", "Arsenal"),
        ("Everton", "West Ham United"),
    ],
    7: [
        ("Bournemouth", "Fulham"),
        ("Leeds United", "Tottenham Hotspur"),
        ("Arsenal", "West Ham United"),
        ("Manchester United", "Sunderland"),
        ("Chelsea", "Liverpool"),
        ("Aston Villa", "Burnley"),
        ("Everton", "Crystal Palace"),
        ("Newcastle United", "Nottingham Forest"),
        ("Wolverhampton Wanderers", "Brighton & Hove Albion"),
        ("Brentford", "Manchester City"),
    ],
    # Add future gameweeks here
}

# Current gameweek (update to 5 for next predictions)
CURRENT_GAMEWEEK = 5
SEASON = "2025-26"

# Model parameters
HOME_ADV = 0.25
BASE_DRAW = 0.24
DRAW_DECAY = 0.85
SIGMOID_K = 1.5
BASE_MU = 1.40
BETA = 0.60
BIG_6 = {"Manchester City", "Arsenal", "Liverpool", "Chelsea", "Manchester United", "Tottenham Hotspur"}
BIG_6_BONUS = 0.15
BIG_6_CONSISTENCY = 1.2

def calculate_probabilities(home: str, away: str) -> tuple:
    """Calculate win/draw/loss probabilities for a match using effective ratings (base + form)"""
    # Use effective ratings that include form boost
    home_effective = get_effective_rating(home)
    away_effective = get_effective_rating(away)
    
    base_diff = (home_effective + HOME_ADV) - away_effective
    
    # Apply Big 6 dominance adjustments
    diff = base_diff
    if home in BIG_6 and away not in BIG_6:
        diff += BIG_6_BONUS
    elif away in BIG_6 and home not in BIG_6:
        diff -= BIG_6_BONUS
    
    # Enhanced draw probability calculation
    draw_modifier = 1.0
    if home in BIG_6 or away in BIG_6:
        draw_modifier = 0.85
    
    p_draw = BASE_DRAW * draw_modifier * math.exp(-DRAW_DECAY * abs(diff))
    
    # Enhanced sigmoid for win/loss split
    sigmoid_k = SIGMOID_K
    if home in BIG_6 or away in BIG_6:
        sigmoid_k *= BIG_6_CONSISTENCY
    
    p_home_given_not_draw = 1 / (1 + math.exp(-sigmoid_k * diff))
    p_home = (1 - p_draw) * p_home_given_not_draw
    p_away = 1 - p_draw - p_home
    
    return p_home, p_draw, p_away, diff

def calculate_expected_goals(diff: float) -> tuple:
    """Calculate expected goals for both teams"""
    mu_home = BASE_MU * math.exp(BETA * diff)
    mu_away = BASE_MU * math.exp(-BETA * diff)
    return mu_home, mu_away

def poisson_pmf(k: int, lam: float) -> float:
    """Poisson probability mass function"""
    return math.exp(-lam) * (lam ** k) / math.factorial(k)

def most_likely_score(mu_h: float, mu_a: float, max_goals: int = 6) -> tuple:
    """Calculate most likely scoreline"""
    best = (0, 0)
    best_p = -1.0
    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            p = poisson_pmf(h, mu_h) * poisson_pmf(a, mu_a)
            if p > best_p:
                best_p = p
                best = (h, a)
    return best

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Premier League Prediction API",
        "version": "1.0.0",
        "endpoints": {
            "/predictions/{gameweek}": "Get predictions for a specific gameweek",
            "/ratings": "Get current team ratings with form information",
            "/form": "Get team form data for last 5 games",
            "/team/{team_name}": "Get detailed team information including match history and rating changes",
            "/match-history": "Get complete match history for all gameweeks",
            "/rating-history": "Get complete rating history for all teams",
            "/health": "Health check endpoint"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/ratings", response_model=TeamRatingsResponse)
async def get_team_ratings():
    """Get current team ratings with form information"""
    ratings_list = []
    for team, rating in CURRENT_RATINGS.items():
        form_boost = calculate_form_boost(team)
        effective_rating = get_effective_rating(team)
        
        ratings_list.append(TeamRating(
            team=team,
            rating=rating,
            effective_rating=effective_rating,
            form_boost=form_boost,
            reason=f"Rating after GW {CURRENT_GAMEWEEK - 1} results + form boost"
        ))
    
    # Sort by effective rating descending
    ratings_list.sort(key=lambda x: x.effective_rating, reverse=True)
    
    return TeamRatingsResponse(
        season=SEASON,
        gameweek=CURRENT_GAMEWEEK - 1,  # Ratings are from previous gameweek
        ratings=ratings_list,
        last_updated=datetime.now().isoformat()
    )

@app.get("/predictions/{gameweek}", response_model=GameweekPredictions)
async def get_predictions(gameweek: int):
    """Get predictions for a specific gameweek"""
    if gameweek not in GAMEWEEK_FIXTURES:
        available_gws = list(GAMEWEEK_FIXTURES.keys())
        raise HTTPException(
            status_code=404, 
            detail=f"Predictions for GW{gameweek} not available. Available gameweeks: {available_gws}"
        )
    
    predictions = []
    fixtures = GAMEWEEK_FIXTURES[gameweek]
    
    for home, away in fixtures:
        # Calculate probabilities and expected goals
        p_home, p_draw, p_away, diff = calculate_probabilities(home, away)
        mu_h, mu_a = calculate_expected_goals(diff)
        ml_h, ml_a = most_likely_score(mu_h, mu_a)
        
        prediction = MatchPrediction(
            match=f"{home} vs {away}",
            home_team=home,
            away_team=away,
            home_percentage=round(100 * p_home, 1),
            draw_percentage=round(100 * p_draw, 1),
            away_percentage=round(100 * p_away, 1),
            fair_home_odds=round(1 / p_home, 2),
            fair_draw_odds=round(1 / p_draw, 2),
            fair_away_odds=round(1 / p_away, 2),
            exp_goals_home=round(mu_h, 2),
            exp_goals_away=round(mu_a, 2),
            most_likely_score=f"{ml_h}-{ml_a}",
            rating_diff=round(diff, 2)
        )
        predictions.append(prediction)
    
    return GameweekPredictions(
        gameweek=gameweek,
        season=SEASON,
        predictions=predictions,
        last_updated=datetime.now().isoformat(),
        total_matches=len(predictions)
    )

@app.get("/form")
async def get_team_form():
    """Get team form data for last 5 games"""
    form_data = {}
    for team, form_results in TEAM_FORM.items():
        # Calculate form points (3 for win, 1 for draw, 0 for loss)
        points = sum([3 if result == 1 else (1 if result == 0.5 else 0) for result in form_results])
        form_boost = calculate_form_boost(team)
        
        form_data[team] = {
            "last_5_results": form_results,
            "points": points,
            "max_possible": 15,
            "form_boost": form_boost,
            "form_description": get_form_description(form_results)
        }
    
    return {
        "season": SEASON,
        "gameweek": CURRENT_GAMEWEEK,
        "form_data": form_data,
        "last_updated": datetime.now().isoformat()
    }

def get_form_description(form_results: List[float]) -> str:
    """Get a human-readable description of team form"""
    if not form_results:
        return "No recent form data"
    
    wins = sum([1 for result in form_results if result == 1])
    draws = sum([1 for result in form_results if result == 0.5])
    losses = sum([1 for result in form_results if result == 0])
    
    if wins >= 4:
        return "Excellent form"
    elif wins >= 3:
        return "Good form"
    elif wins >= 2:
        return "Decent form"
    elif wins >= 1:
        return "Mixed form"
    elif draws >= 2:
        return "Struggling for wins"
    else:
        return "Poor form"

@app.get("/team/{team_name}")
async def get_team_details(team_name: str):
    """Get detailed information about a specific team including match history and rating changes"""
    if team_name not in CURRENT_RATINGS:
        raise HTTPException(status_code=404, detail=f"Team '{team_name}' not found")
    
    # Get team's match history
    team_matches = []
    for gameweek, matches in MATCH_HISTORY.items():
        for match, score in matches.items():
            if team_name in score:
                # Determine if team was home or away
                teams = list(score.keys())
                home_team, away_team = teams[0], teams[1]
                is_home = team_name == home_team
                opponent = away_team if is_home else home_team
                
                team_goals = score[team_name]
                opponent_goals = score[opponent]
                
                # Determine result
                if team_goals > opponent_goals:
                    result = "W"
                elif team_goals < opponent_goals:
                    result = "L"
                else:
                    result = "D"
                
                team_matches.append({
                    "gameweek": gameweek,
                    "opponent": opponent,
                    "is_home": is_home,
                    "team_goals": team_goals,
                    "opponent_goals": opponent_goals,
                    "result": result,
                    "score": f"{team_goals}-{opponent_goals}" if is_home else f"{opponent_goals}-{team_goals}"
                })
    
    # Sort matches by gameweek (most recent first)
    team_matches.sort(key=lambda x: x["gameweek"], reverse=True)
    
    # Get rating history
    rating_history = RATING_HISTORY.get(team_name, [])
    rating_changes = []
    for i in range(1, len(rating_history)):
        change = rating_history[i] - rating_history[i-1]
        rating_changes.append({
            "gameweek": i + 1,
            "previous_rating": rating_history[i-1],
            "new_rating": rating_history[i],
            "change": change
        })
    
    # Get current form and rating info
    current_rating = CURRENT_RATINGS[team_name]
    form_boost = calculate_form_boost(team_name)
    effective_rating = get_effective_rating(team_name)
    form_results = TEAM_FORM.get(team_name, [])
    
    return {
        "team": team_name,
        "current_rating": current_rating,
        "effective_rating": effective_rating,
        "form_boost": form_boost,
        "form_results": form_results,
        "form_description": get_form_description(form_results),
        "match_history": team_matches,
        "rating_history": rating_history,
        "rating_changes": rating_changes,
        "season": SEASON,
        "current_gameweek": CURRENT_GAMEWEEK
    }

@app.get("/match-history")
async def get_all_match_history():
    """Get complete match history for all gameweeks"""
    return {
        "match_history": MATCH_HISTORY,
        "season": SEASON,
        "current_gameweek": CURRENT_GAMEWEEK,
        "last_updated": datetime.now().isoformat()
    }

@app.get("/rating-history")
async def get_all_rating_history():
    """Get complete rating history for all teams"""
    return {
        "rating_history": RATING_HISTORY,
        "current_ratings": CURRENT_RATINGS,
        "season": SEASON,
        "current_gameweek": CURRENT_GAMEWEEK,
        "last_updated": datetime.now().isoformat()
    }

@app.get("/predictions")
async def get_available_gameweeks():
    """Get list of available gameweeks for predictions"""
    available_gws = sorted(GAMEWEEK_FIXTURES.keys())
    return {
        "available_gameweeks": available_gws,
        "current_gameweek": CURRENT_GAMEWEEK,
        "season": SEASON,
        "total_teams": len(CURRENT_RATINGS)
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"Starting server on {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=False)
