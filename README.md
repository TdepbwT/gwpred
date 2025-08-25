# Premier League Prediction Model

A simple yet effective model for predicting Premier League match outcomes using team ratings and probability distributions. Now supports multiple gameweeks with dynamic rating updates.

## Overview

This project implements a rating-based prediction model for Premier League matches that:
- Uses team power ratings on a goal-difference scale (updated after each gameweek)
- Accounts for home advantage
- Calculates win/draw/loss probabilities
- Estimates expected goals and most likely scorelines
- Provides fair betting odds for each outcome
- Adapts team ratings based on results and transfer activity
- Outputs predictions in both console and CSV formats

## Features

- **Dynamic Team Ratings**: Pre-season ratings updated after each gameweek based on results
- **Transfer Impact**: Rating adjustments for significant transfers (e.g., Ebere Eze to Arsenal)
- **Home Advantage**: Built-in home field advantage adjustment (+0.25 rating units)
- **Dynamic Draw Probability**: Draw rates that decrease for mismatched teams
- **Expected Goals**: Poisson-based goal expectation modeling
- **Most Likely Scores**: Calculates the most probable scoreline for each match
- **Fair Odds**: Converts probabilities to fair betting odds
- **Multiple Output Formats**: Console display and CSV export for data analysis
- **Historical Tracking**: JSON files store fixture data and key events

## Model Parameters

- `HOME_ADV`: 0.25 - Home advantage in rating units
- `BASE_DRAW`: 0.28 - Baseline draw rate (28%)
- `DRAW_DECAY`: 0.75 - Rate at which draws decrease for mismatches
- `SIGMOID_K`: 1.3 - Sharpness of win/loss probability split
- `BASE_MU`: 1.35 - League-average goals per team per game
- `BETA`: 0.45 - How much expected goals vary with rating difference

## Team Ratings (2025/26 Season)

The model uses dynamic ratings that are updated after each gameweek. Current ratings reflect:
- Pre-season assessments
- GW1 results and performances
- Major transfer activity (e.g., Ebere Eze £68m move to Arsenal)

**Current Top Ratings (Post-GW1):**
- Liverpool: 1.35 (↑ from 1.25 - impressive 4-2 win vs Bournemouth)
- Manchester City: 1.30 (↑ from 1.20 - dominant 4-0 win vs Wolves)
- Arsenal: 1.25 (↑ from 1.00 - 1-0 win vs Man Utd + Eze signing)

**Mid-Table Adjustments:**
- Tottenham: 0.70 (↑ from 0.60 - convincing 3-0 win vs Burnley)
- Sunderland: 0.25 (↑ from -0.10 - shocking 3-0 upset win vs West Ham)
- Nottingham Forest: 0.00 (↑ from -0.10 - impressive 3-1 win vs Brentford)

**Notable Declines:**
- West Ham: -0.20 (↓ from 0.10 - poor 0-3 loss to Sunderland)
- Bournemouth: -0.30 (↓ from -0.20 - leaky 2-4 defeat vs Liverpool)
- Burnley: -0.45 (↓ from -0.35 - struggled badly in 0-3 loss to Spurs)

## Project Structure

```
gw1pred/
├── GW1Pred.py                              # Gameweek 1 predictions script
├── GW2Pred.py                              # Gameweek 2 predictions script  
├── gw1.json                                # GW1 fixture data and metadata
├── gw2.json                                # GW2 fixture data and transfer notes
├── gw2_predictions_2025-26.csv            # GW2 predictions in CSV format
├── gw2_predictions_enhanced_big6_2025-26.csv # Enhanced predictions (if applicable)
└── README.md                               # This file
```

## Requirements

```
pandas
math (built-in)
itertools (built-in)
```

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd gw1pred
```

2. Install required dependencies:
```bash
pip install pandas
```

## Usage

### For Gameweek 1 Predictions:
```bash
python GW1Pred.py
```

### For Gameweek 2 Predictions:
```bash
python GW2Pred.py
```

Each script will:
1. Output formatted predictions to the console
2. Generate corresponding CSV files for data analysis
3. Show updated team ratings based on latest results and transfers

The scripts automatically handle:
- Rating adjustments after each gameweek
- Home advantage calculations
- Expected goals modeling
- Most likely scoreline predictions

## Sample Output

### Console Output (GW2 Example):
```
================================================================================
PREMIER LEAGUE GAMEWEEK 2 PREDICTIONS (2025/26 Season)
Updated after GW1 results and recent transfers
================================================================================
                        Match  Home %  Draw %  Away %  Fair Home Odds  Fair Draw Odds  Fair Away Odds  Exp Goals (Home)  Exp Goals (Away) Most Likely Score  Model diff (H-A)
           Arsenal vs Brighton     79.4    11.4     9.2            1.26            8.77          10.87               2.42              0.91              2-1              1.35
    Bournemouth vs Newcastle Utd    45.6    23.1    31.3            2.19            4.33           3.19               1.57              1.24              1-1              0.25
```

### CSV Output:
All predictions are also saved to CSV files (e.g., `gw2_predictions_2025-26.csv`) containing:
- Match details
- Probability percentages for each outcome
- Fair odds calculations
- Expected goals for both teams
- Most likely scoreline
- Model rating difference

## Model Methodology

1. **Initial Ratings**: Assign pre-season power ratings to all teams based on expected performance
2. **Dynamic Updates**: Adjust ratings after each gameweek based on:
   - Match results and performance levels
   - Goal difference and expected goal metrics
   - Significant transfer activity
3. **Rating Difference**: Calculate effective rating difference including home advantage (+0.25)
4. **Draw Probability**: Apply exponential decay to reduce draws for mismatched teams
5. **Win Probabilities**: Use sigmoid function to split remaining probability mass
6. **Expected Goals**: Apply exponential scaling based on rating difference
7. **Scoreline Prediction**: Use Poisson distributions to find most likely score
8. **Output Generation**: Create both console display and CSV files for analysis

## Key Updates (2025/26 Season)

### GW1 Results Impact:
- **Liverpool** upgraded after impressive 4-2 win vs Bournemouth
- **Sunderland** dramatically improved following shock 3-0 upset vs West Ham
- **West Ham** downgraded significantly after poor defensive display
- **Arsenal** boosted by both match performance and Eze signing

### Transfer Activity:
- **Ebere Eze** (Crystal Palace → Arsenal, £68m): Major creative addition
- Rating adjustments reflect both transfer impact and early season form

### Technical Improvements:
- Enhanced CSV output format for better data analysis
- JSON metadata files for fixture tracking and transfer notes
- Improved console formatting with seasonal context

## Limitations

- Ratings adjustments are subjective and based on limited data samples
- Model doesn't account for injuries, suspensions, or squad rotation
- Transfer impact estimations may be speculative
- Weather, referee, and psychological factors not considered
- Small sample sizes early in season may lead to overreactions
- Historical head-to-head records not incorporated

## Future Improvements

- **Advanced Analytics**: Incorporate xG, xA, and defensive metrics
- **Injury/Suspension Tracking**: Real-time squad availability monitoring
- **Historical Integration**: Head-to-head records and venue-specific performance
- **Machine Learning**: Automated rating adjustments using statistical models
- **Live Updates**: API integration for real-time transfer and team news
- **Extended Coverage**: Additional leagues and competitions
- **Performance Validation**: Backtesting against historical seasons
- **Enhanced Visualization**: Interactive charts and prediction confidence intervals

## Contributing

Feel free to fork this repository and submit pull requests for improvements. Some areas for contribution:
- **Enhanced Rating Systems**: More sophisticated team strength calculations
- **Data Integration**: APIs for live transfer and injury data
- **Statistical Validation**: Backtesting frameworks and accuracy metrics
- **Alternative Models**: Elo ratings, machine learning approaches
- **Visualization Tools**: Interactive dashboards and prediction tracking
- **Extended Features**: Player-level analysis, formation impact

## Data Sources

- Team ratings: Subjective assessments based on squad quality and market activity
- Transfer data: Public transfer announcements and reported fees
- Fixture data: Official Premier League fixture lists
- Results: Match outcomes and basic statistics

## License

This project is open source and available under the [MIT License](LICENSE).

## Disclaimer

This model is for educational and entertainment purposes only. 
