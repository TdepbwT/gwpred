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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
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
    "Manchester City": 1.30,
    "Arsenal": 1.25,
    "Liverpool": 1.35,
    "Tottenham Hotspur": 0.75,
    "Aston Villa": 0.40,
    "Chelsea": 0.65,
    "Newcastle United": 0.40,
    "Manchester United": 0.25,
    "Brighton & Hove Albion": 0.15,
    "West Ham United": -0.45,
    "Brentford": 0.00,
    "Everton": -0.15,
    "Wolverhampton Wanderers": -0.15,
    "Nottingham Forest": 0.15,
    "Crystal Palace": 0.05,
    "Fulham": 0.05,
    "Leeds United": -0.05,
    "Bournemouth": -0.30,
    "Burnley": -0.45,
    "Sunderland": 0.30,
}

# Gameweek fixtures
GW2_FIXTURES = [
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
        season="2025-26",
        gameweek=2,
        ratings=ratings_list,
        last_updated=datetime.now().isoformat()
    )

@app.get("/predictions/{gameweek}", response_model=GameweekPredictions)
async def get_predictions(gameweek: int):
    """Get predictions for a specific gameweek"""
    if gameweek != 2:
        raise HTTPException(status_code=404, detail=f"Predictions for GW{gameweek} not available. Only GW2 is currently supported.")
    
    predictions = []
    
    for home, away in GW2_FIXTURES:
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
        season="2025-26",
        predictions=predictions,
        last_updated=datetime.now().isoformat(),
        total_matches=len(predictions)
    )

@app.get("/predictions")
async def get_available_gameweeks():
    """Get list of available gameweeks for predictions"""
    return {
        "available_gameweeks": [2],
        "current_gameweek": 2,
        "season": "2025-26",
        "total_teams": len(CURRENT_RATINGS)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
