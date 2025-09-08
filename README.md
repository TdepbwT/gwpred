# Premier League Prediction System

A comprehensive football prediction system featuring dynamic team ratings, multiple gameweek support, and a modern web interface. Built with FastAPI (backend) and React (frontend), deployed on Railway and Vercel.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-000000?style=for-the-badge&logo=vercel)](https://gwpred.vercel.app)
[![API](https://img.shields.io/badge/API-Railway-0B0D0E?style=for-the-badge&logo=railway)](https://gwpredictor.up.railway.app)

## Quick Start

### Web Application (Live)
The application is deployed and ready to use:
- **Frontend**: [https://gwpred.vercel.app](https://gwpred.vercel.app)
- **API**: [https://gwpredictor.up.railway.app](https://gwpredictor.up.railway.app)
- **API Documentation**: [https://gwpredictor.up.railway.app/docs](https://gwpredictor.up.railway.app/docs)

### Local Development
```bash
# Clone the repository
git clone https://github.com/TdepbwT/gwpred.git
cd gwpred

# Quick setup (Windows)
.\setup.ps1

# Start development servers
.\start.ps1
```

## Features

### Prediction Engine
- **Dynamic Team Ratings**: Automatically updated based on match results and transfer activity
- **Form-Based Rating System**: Recent performance tracking with opposition strength weighting
- **Transfer Window Integration**: Updated ratings reflecting summer 2025 signings
- **Multiple Gameweeks**: Support for entire season with easy gameweek management
- **Advanced Modeling**: Home advantage, Big 6 bonuses, dynamic draw probabilities
- **Expected Goals**: Poisson-based goal expectation with most likely scorelines
- **Fair Odds**: Probability-based betting odds calculation

### Modern Web Interface
- **Responsive Design**: Beautiful UI built with React and Tailwind CSS
- **Real-time Data**: Live predictions from FastAPI backend
- **Interactive Tabs**: Switch between predictions, team ratings, and team details
- **Team Analysis**: Detailed team pages with match history and rating progression
- **Form Tracking**: Visual representation of team form over last 5 games
- **Rating History**: Track rating changes and improvements over time
- **Mobile Optimized**: Works perfectly on all devices
- **Accessible**: WCAG compliant with keyboard navigation

### Developer Experience
- **Type Safety**: Full TypeScript frontend, Pydantic backend validation
- **Auto Documentation**: Interactive API docs with OpenAPI/Swagger
- **Hot Reload**: Development servers with instant updates
- **Easy Deployment**: Ready for Vercel (frontend) and Railway (backend)

##  Architecture

```
gw1pred/
├──   backend/                 # FastAPI REST API
│   ├── main.py                # Core prediction engine & API endpoints
│   ├── requirements.txt       # Python dependencies
│   ├── Procfile              # Railway deployment config
│   └── railway.toml          # Railway build settings
├──   frontend/               # React web application
│   ├── src/
│   │   ├── App.tsx           # Main application component
│   │   └── components/       # Reusable UI components
│   ├── package.json          # Node.js dependencies
│   ├── tailwind.config.js    # Styling configuration
│   └── vercel.json           # Vercel deployment config
├──   Scripts & Tools
│   ├── add_gameweek.py       # Helper script for adding new gameweeks
│   ├── update_ratings.py     # Helper script for updating team ratings
│   ├── example_fixtures.txt  # Sample fixture format
│   └── example_results.json  # Sample results format
├──   Data Files
│   ├── gw1.json              # Historical gameweek data
│   ├── gw2.json              # Historical gameweek data
│   └── *.csv                 # Prediction outputs
└──   Documentation
    ├── README.md             # This file
    ├── DEPLOYMENT.md         # Deployment guide
    └── WEB_APP_README.md     # Detailed web app docs
```

##  Prediction Model

### Core Algorithm
The system uses an advanced rating-based model that considers:

- **Team Strength Ratings**: Dynamic values updated after each gameweek
- **Home Advantage**: +0.25 rating boost for home teams
- **Big 6 Dominance**: Enhanced performance against smaller teams
- **Draw Probability Decay**: Fewer draws in mismatched fixtures
- **Expected Goals**: Poisson distribution modeling

### Current Team Ratings (Post-GW3 + Transfer Updates)
```python
"Liverpool": 1.45        # Top rated team (+ Isak, Wirtz signings)
"Arsenal": 1.35          # Strong title contenders (+ Eze, Gyökeres, Zubimendi)
"Manchester City": 1.20  # Defending champions (+ Reijnders)
"Tottenham Hotspur": 0.70
"Chelsea": 0.75          # Improved (+ Joao Pedro)
"Manchester United": 0.30 # Enhanced (+ Sesko, Mbeumo, Cunha)
# ... (see main.py for complete ratings with form boosts)
```

### Model Parameters
```python
HOME_ADV = 0.25              # Home advantage
BASE_DRAW = 0.24             # Base draw probability
BIG_6_BONUS = 0.15           # Big 6 dominance factor
SIGMOID_K = 1.5              # Win probability sharpness
BASE_MU = 1.40               # Expected goals base
BETA = 0.60                  # Goals variance factor
```

## Adding New Gameweeks

### Method 1: Helper Script (Recommended)
```bash
# Create fixtures file
echo "Liverpool vs Arsenal
Chelsea vs Manchester City
Tottenham vs Newcastle" > gw4_fixtures.txt

# Add new gameweek
python add_gameweek.py 4 gw4_fixtures.txt
```

### Method 2: Manual Update
Edit `backend/main.py`:
```python
GAMEWEEK_FIXTURES = {
    2: [("Arsenal", "Leeds United"), ...],
    3: [("Liverpool", "Arsenal"), ...],
    4: [("Chelsea", "Manchester City"), ...],  # Add new gameweek
}
CURRENT_GAMEWEEK = 4  # Update current gameweek
```

### Updating Ratings After Results
```bash
# Create results file
echo '{
  "Liverpool vs Arsenal": {"Liverpool": 2, "Arsenal": 1},
  "Chelsea vs Manchester City": {"Chelsea": 0, "Manchester City": 3}
}' > gw3_results.json

# Update ratings
python update_ratings.py gw3_results.json
```

## Deployment

### Production Deployment
The application is deployed using:
- **Frontend**: Vercel (automatic deployments from GitHub)
- **Backend**: Railway (containerized Python API)

### Environment Variables
**Backend (Railway)**:
```bash
PORT=8000
CORS_ORIGINS=https://gwpred.vercel.app
```

**Frontend (Vercel)**:
```bash
VITE_API_URL=https://gwpredictor.up.railway.app
```

### Manual Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## Development

### Prerequisites
- **Python 3.11+** (backend)
- **Node.js 18+** (frontend)
- **Git** (version control)

### Local Setup
```bash
# Backend setup
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
python main.py

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

### API Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `GET /predictions` - Available gameweeks
- `GET /predictions/{gameweek}` - Specific gameweek predictions
- `GET /ratings` - Current team ratings with form information
- `GET /form` - Team form data for last 5 games
- `GET /team/{team_name}` - Detailed team information including match history and rating changes
- `GET /match-history` - Complete match history for all gameweeks
- `GET /rating-history` - Complete rating history for all teams

## Sample Output

### Match Predictions
```
Arsenal vs Leeds United
├── Home Win: 90.9% (Odds: 1.10)
├── Draw: 4.8% (Odds: 20.83)
├── Away Win: 4.3% (Odds: 23.26)
├── Expected Goals: 2.34 - 0.73
└── Most Likely Score: 2-0
```

### Team Analysis Features
The application now includes comprehensive team analysis capabilities:

**Team Details Page:**
- Current effective rating (base + form boost)
- Match history with results and venues
- Rating progression over gameweeks
- Form tracking with visual indicators
- Recent rating changes and improvements

**Form System:**
- Tracks last 5 games for each team
- Visual form indicators (Win/Draw/Loss)
- Opposition strength weighting
- Form-based rating adjustments (up to ±0.2)

**Match History:**
- Complete results for all gameweeks
- Home/Away venue indicators
- Score displays and result tracking
- Chronological match progression

### Team Ratings Table
```
Rank | Team              | Base Rating | Form Boost | Effective Rating
-----|-------------------|-------------|------------|-----------------
1    | Liverpool         | +1.45       | +0.12      | +1.57
2    | Arsenal           | +1.35       | +0.12      | +1.47
3    | Manchester City   | +1.20       | +0.12      | +1.32
4    | Chelsea           | +0.75       | +0.12      | +0.87
5    | Tottenham         | +0.70       | +0.04      | +0.74
```

## Testing

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests  
cd frontend
npm test

# API testing
curl https://gwpredictor.up.railway.app/health
```



### Areas for Future Improvement
- Enhanced prediction algorithms
- Additional statistical features
- UI/UX improvements
- Test coverage expansion


## Roadmap

- [x] **Form-based rating system** - Implemented with opposition strength weighting
- [x] **Transfer window integration** - Updated ratings reflecting summer 2025 signings
- [x] **Team analysis pages** - Detailed match history and rating progression
- [x] **Enhanced API endpoints** - Team details, match history, and rating history
- [ ] **Player-level data integration**
- [ ] **Injury/suspension tracking**
- [ ] **Weather impact modeling**
- [ ] **Live score integration**
- [ ] **Mobile app (React Native)**
- [ ] **Fantasy football integration**
- [ ] **Multi-league support**

## License

This project is open source and available under the [MIT License](LICENSE).

## Disclaimer

This application is for educational and entertainment purposes only. The predictions are based on statistical models and should not be considered as professional betting advice. Please gamble responsibly.

## Acknowledgments

- **FastAPI** - Modern Python web framework
- **React** - Frontend library
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Beautiful UI components
- **Vercel** - Frontend hosting platform
- **Railway** - Backend hosting platform

---

<div align="center">

**[Live Demo](https://gwpred.vercel.app) | [API Docs](https://gwpredictor.up.railway.app/docs) | [Report Bug](https://github.com/TdepbwT/gwpred/issues) | [Request Feature](https://github.com/TdepbwT/gwpred/issues)**

Made by [David Adeoyo](https://github.com/TdepbwT)

</div>
