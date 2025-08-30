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
    "https://gwpred.vercel.app",
    "https://gwpred-2z4z.vercel.app",
    "https://gwpredictor.up.railway.app/" 
]
# Add environment variable support for production
cors_origins = os.getenv("CORS_ORIGINS", "").split(",")
if cors_origins and cors_origins[0]:
    allowed_origins.extend(cors_origins)

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
    change_from_previous: Optional[float] = None
    reason: Optional[str] = None

class TeamRatingsResponse(BaseModel):
    season: str
    gameweek: int
    ratings: List[TeamRating]
    last_updated: str

# Current team ratings (post-GW1)
CURRENT_RATINGS = {
    "Manchester City": 1.23,
    "Arsenal": 1.26,
    "Liverpool": 1.38,
    "Tottenham Hotspur": 0.83,
    "Aston Villa": 0.36,
    "Chelsea": 0.67,
    "Newcastle United": 0.38,
    "Manchester United": 0.21,
    "Brighton & Hove Albion": 0.11,
    "West Ham United": -0.46,
    "Brentford": 0.06,
    "Everton": -0.09,
    "Wolverhampton Wanderers": -0.19,
    "Nottingham Forest": 0.11,
    "Crystal Palace": 0.01,
    "Fulham": 0.06,
    "Leeds United": -0.05,
    "Bournemouth": -0.24,
    "Burnley": -0.38,
    "Sunderland": 0.24,
}

def update_ratings_after_gameweek(results: Dict[str, Dict[str, int]]):
    """
    Update team ratings based on gameweek results
    
    Args:
        results: Dictionary of match results
        Format: {
            "Arsenal vs Leeds United": {"Arsenal": 2, "Leeds United": 1},
            "Chelsea vs Manchester City": {"Chelsea": 1, "Manchester City": 3}
        }
    """
    global CURRENT_RATINGS
    
    for match, score in results.items():
        teams = list(score.keys())
        home_team, away_team = teams[0], teams[1]
        home_goals, away_goals = score[home_team], score[away_team]
        
        # Simple rating adjustment based on result vs expectation
        expected_home, expected_draw, expected_away, _ = calculate_probabilities(home_team, away_team)
        
        if home_goals > away_goals:  # Home win
            actual_result = [1, 0, 0]
        elif home_goals < away_goals:  # Away win
            actual_result = [0, 0, 1]
        else:  # Draw
            actual_result = [0, 1, 0]
        
        expected_result = [expected_home, expected_draw, expected_away]
        
        # Calculate surprise factor and adjust ratings
        surprise_factor = 0.1  # How much ratings can change per game
        home_adjustment = surprise_factor * (actual_result[0] - expected_result[0])
        away_adjustment = surprise_factor * (actual_result[2] - expected_result[2])
        
        CURRENT_RATINGS[home_team] += home_adjustment
        CURRENT_RATINGS[away_team] += away_adjustment

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
        ("Leeds United", "Newcastle"),
        ("Nottingham Forest", "West Ham United"),
        ("Wolverhampton Wanderers", "Everton"),
        ("Sunderland", "Brentford"),
    ],
    # Add future gameweeks here
}

# Current gameweek
CURRENT_GAMEWEEK = 3
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
    """Calculate win/draw/loss probabilities for a match"""
    base_diff = (CURRENT_RATINGS[home] + HOME_ADV) - CURRENT_RATINGS[away]
    
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
            "/ratings": "Get current team ratings",
            "/health": "Health check endpoint"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/ratings", response_model=TeamRatingsResponse)
async def get_team_ratings():
    """Get current team ratings"""
    ratings_list = []
    for team, rating in CURRENT_RATINGS.items():
        ratings_list.append(TeamRating(
            team=team,
            rating=rating,
            reason=f"Rating after GW1 results"
        ))
    
    # Sort by rating descending
    ratings_list.sort(key=lambda x: x.rating, reverse=True)
    
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
