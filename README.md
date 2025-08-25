# Premier League Prediction Model

A simple yet effective model for predicting Premier League match outcomes using team ratings and probability distributions. Now available as both a command-line tool and a modern web application.

## 🚀 Quick Start Options

### Option 1: Web Application (Recommended)
Experience the predictions through a modern React web interface:

```bash
# Setup (one-time)
.\setup.ps1

# Start both backend and frontend servers
.\start.ps1
```

Then open http://localhost:3000 in your browser.

### Option 2: Command Line
Run predictions directly in the terminal:

```bash
python GW1Pred.py  # For Gameweek 1
python GW2Pred.py  # For Gameweek 2
```

## Overview

This project implements a rating-based prediction model for Premier League matches that:
- Uses pre-season team power ratings on a goal-difference scale
- Accounts for home advantage
- Calculates win/draw/loss probabilities
- Estimates expected goals and most likely scorelines
- Provides fair betting odds for each outcome

## Features

- **Team Ratings**: Pre-season power ratings for all 20 Premier League teams
- **Home Advantage**: Built-in home field advantage adjustment (+0.25 rating units)
- **Dynamic Draw Probability**: Draw rates that decrease for mismatched teams
- **Expected Goals**: Poisson-based goal expectation modeling
- **Most Likely Scores**: Calculates the most probable scoreline for each match
- **Fair Odds**: Converts probabilities to fair betting odds

## Model Parameters

- `HOME_ADV`: 0.25 - Home advantage in rating units
- `BASE_DRAW`: 0.28 - Baseline draw rate (28%)
- `DRAW_DECAY`: 0.75 - Rate at which draws decrease for mismatches
- `SIGMOID_K`: 1.3 - Sharpness of win/loss probability split
- `BASE_MU`: 1.35 - League-average goals per team per game
- `BETA`: 0.45 - How much expected goals vary with rating difference

## Team Ratings (2025/26 Season)

The model uses the following pre-season ratings:

**Top Tier:**
- Liverpool: 1.25
- Manchester City: 1.20
- Arsenal: 1.00

**Upper Mid-Table:**
- Tottenham: 0.60
- Aston Villa: 0.50
- Chelsea: 0.40
- Newcastle United: 0.35
- Manchester United: 0.30

**Mid-Table:**
- Brighton: 0.10
- West Ham: 0.10
- Brentford: 0.10
- Crystal Palace: 0.05
- Fulham: 0.00

**Lower Table:**
- Everton: -0.05
- Sunderland: -0.10
- Wolves: -0.10
- Nottingham Forest: -0.10
- Leeds United: -0.15
- Bournemouth: -0.20
- Burnley: -0.35

## Project Structure

```
gw1pred/
├── backend/                    # FastAPI web application
│   ├── main.py                # REST API server
│   └── requirements.txt       # Python dependencies
├── frontend/                   # React web interface  
│   ├── src/                   # React components and pages
│   ├── package.json           # Node.js dependencies
│   └── tailwind.config.js     # Styling configuration
├── GW1Pred.py                 # Command-line GW1 predictions
├── GW2Pred.py                 # Command-line GW2 predictions
├── gw1.json                   # GW1 fixture data
├── gw2.json                   # GW2 fixture data with transfers
├── setup.ps1                  # Web app setup script
├── start.ps1                  # Development server launcher
├── WEB_APP_README.md          # Detailed web app documentation
└── README.md                  # This file
```

## Web Application Features

### Frontend (React + shadcn/ui)
- **Modern Interface**: Clean, responsive design with Tailwind CSS
- **Real-time Data**: Live updates from the prediction API
- **Interactive Tabs**: Switch between match predictions and team ratings
- **Mobile Friendly**: Optimized for all screen sizes
- **Accessible**: Built with accessibility best practices

### Backend (FastAPI)
- **REST API**: Clean endpoints for predictions and ratings
- **Type Safety**: Full Pydantic validation and documentation
- **CORS Enabled**: Ready for frontend integration
- **Auto Documentation**: Interactive API docs at `/docs`
- **Fast Performance**: Async Python with optimized calculations

## Requirements

### For Web Application:
```
Python 3.8+ (backend)
Node.js 18+ (frontend)
npm or yarn (package manager)
```

### For Command Line Only:
```
pandas
math (built-in)
itertools (built-in)
```

## Installation & Usage

### Web Application Setup

1. **Quick Setup (Windows):**
   ```bash
   # Clone and navigate to the project
   cd gw1pred
   
   # Run the automated setup
   .\setup.ps1
   
   # Start the development servers
   .\start.ps1
   ```

   The web app will be available at:
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs

2. **Manual Setup:**
   
   **Backend:**
   ```bash
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python main.py
   ```
   
   **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Command Line Usage

For standalone prediction scripts:

```bash
# Install Python dependencies
pip install pandas

# Run predictions
python GW1Pred.py  # Gameweek 1 predictions
python GW2Pred.py  # Gameweek 2 predictions
```

Both options provide:
- Win/Draw/Loss probabilities (%)
- Fair betting odds
- Expected goals for each team
- Most likely scoreline
- Model rating differences
- Model rating difference

## Sample Output

```
                        Match  Home %  Draw %  Away %  Fair Home Odds  Fair Draw Odds  Fair Away Odds  Exp Goals (Home)  Exp Goals (Away) Most Likely Score  Model diff (H-A)
           Liverpool vs Bournemouth    71.2    17.8    11.0            1.40            5.62           9.09               1.89              0.96              2-1              1.70
    Aston Villa vs Newcastle United    56.9    24.7    18.4            1.76            4.05           5.43               1.55              1.17              1-1              0.40
                Brighton vs Fulham    53.2    26.1    20.7            1.88            3.83           4.83               1.49              1.21              1-1              0.25
```

## Model Methodology

1. **Rating Difference**: Calculate the effective rating difference including home advantage
2. **Draw Probability**: Apply exponential decay to reduce draws for mismatched teams
3. **Win Probabilities**: Use sigmoid function to split remaining probability mass
4. **Expected Goals**: Apply exponential scaling based on rating difference
5. **Scoreline Prediction**: Use Poisson distributions to find most likely score

## Limitations

- Ratings are subjective pre-season estimates
- Model doesn't account for injuries, transfers, or form
- Historical data not incorporated beyond rating assignments
- Fixed parameters may not reflect current season dynamics

## Future Improvements

- Incorporate transfer market activity
- Add injury/suspension tracking
- Include historical head-to-head records
- Dynamic rating updates based on results
- Weather and referee impact factors

## Contributing

Feel free to fork this repository and submit pull requests for improvements. Some areas for contribution:
- More sophisticated rating systems
- Additional statistical features
- Model validation against historical data
- Alternative probability distributions

## License

This project is open source and available under the [MIT License](LICENSE).

## Disclaimer

This model is for educational and entertainment purposes only. Please gamble responsibly and within your means if using for betting purposes.
