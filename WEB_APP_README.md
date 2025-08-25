# Premier League Prediction Web App

This is a full-stack web application for Premier League match predictions, featuring a FastAPI backend and React frontend with shadcn/ui components.

## Project Structure

```
gw1pred/
├── backend/
│   ├── main.py                 # FastAPI application
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/ui/      # shadcn/ui components
│   │   ├── lib/               # Utility functions
│   │   ├── App.tsx            # Main React component
│   │   ├── main.tsx           # React entry point
│   │   └── index.css          # Global styles
│   ├── package.json           # Node.js dependencies
│   ├── vite.config.ts         # Vite configuration
│   ├── tailwind.config.js     # Tailwind CSS configuration
│   └── tsconfig.json          # TypeScript configuration
├── setup.ps1                  # Windows setup script
└── start.ps1                  # Development server script
```

## Features

### Backend (FastAPI)
- **RESTful API** for match predictions and team ratings
- **CORS enabled** for frontend integration
- **Pydantic models** for data validation
- **Dynamic team ratings** updated after each gameweek
- **Big 6 enhancement parameters** for more accurate predictions
- **JSON fixture data** with transfer tracking

### Frontend (React + shadcn/ui)
- **Modern React** with TypeScript and Vite
- **shadcn/ui components** for consistent, accessible UI
- **Tailwind CSS** for responsive styling
- **Real-time data fetching** from the backend API
- **Interactive tabs** for predictions and team ratings
- **Responsive design** for mobile and desktop

### Prediction Engine
- **Rating-based model** with home advantage
- **Poisson distribution** for expected goals
- **Dynamic draw probability** based on team strength difference
- **Transfer impact modeling** (e.g., Ebere Eze to Arsenal)
- **Big 6 dominance factors** for enhanced accuracy

## Quick Start

### Prerequisites
- **Python 3.8+** with pip
- **Node.js 18+** with npm
- **PowerShell** (Windows) or bash (Unix)

### Windows Setup (PowerShell)

1. **Clone and navigate to the project:**
   ```powershell
   cd "c:\Users\David Adeoyo\Documents\Computer Science Projects\footballprediction\predictor-simple\gw1pred"
   ```

2. **Run the setup script:**
   ```powershell
   .\setup.ps1
   ```

3. **Start both servers:**
   ```powershell
   .\start.ps1
   ```

### Manual Setup

#### Backend Setup
1. **Create and activate Python virtual environment:**
   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. **Install Python dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Start the FastAPI server:**
   ```powershell
   python main.py
   # or: uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup
1. **Install Node.js dependencies:**
   ```powershell
   cd frontend
   npm install
   ```

2. **Start the React development server:**
   ```powershell
   npm run dev
   ```

## API Endpoints

### Base URL: `http://localhost:8000`

- **GET /** - API information and available endpoints
- **GET /health** - Health check endpoint
- **GET /predictions/{gameweek}** - Get predictions for specific gameweek
- **GET /predictions** - List available gameweeks
- **GET /ratings** - Get current team ratings

### Example API Response

```json
{
  "gameweek": 2,
  "season": "2025-26",
  "predictions": [
    {
      "match": "Arsenal vs Leeds United",
      "home_team": "Arsenal",
      "away_team": "Leeds United",
      "home_percentage": 79.4,
      "draw_percentage": 11.4,
      "away_percentage": 9.2,
      "fair_home_odds": 1.26,
      "fair_draw_odds": 8.77,
      "fair_away_odds": 10.87,
      "exp_goals_home": 2.42,
      "exp_goals_away": 0.91,
      "most_likely_score": "2-1",
      "model_diff": 1.35
    }
  ],
  "last_updated": "2025-08-25T10:30:00",
  "total_matches": 10
}
```

## Development

### Frontend Development
- **Hot reload**: Changes automatically reload in the browser
- **TypeScript**: Full type safety and IntelliSense
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: High-quality, accessible components

### Backend Development
- **FastAPI**: Automatic API documentation at `http://localhost:8000/docs`
- **Pydantic**: Request/response validation
- **CORS**: Configured for frontend integration
- **Type hints**: Full Python type annotations

### Adding New Features

#### New API Endpoint
1. Add endpoint function to `backend/main.py`
2. Define Pydantic models for request/response
3. Update frontend API calls in `App.tsx`

#### New UI Component
1. Create component in `frontend/src/components/`
2. Use shadcn/ui base components
3. Style with Tailwind CSS classes

## Model Parameters

The prediction model uses these enhanced parameters:

- **HOME_ADV**: 0.25 - Home advantage boost
- **BASE_DRAW**: 0.24 - Baseline draw probability
- **DRAW_DECAY**: 0.85 - Draw reduction for mismatches
- **SIGMOID_K**: 1.5 - Win/loss probability sharpness
- **BASE_MU**: 1.40 - Average goals per team
- **BETA**: 0.60 - Rating impact on expected goals
- **BIG_6_BONUS**: 0.15 - Big 6 vs non-Big 6 advantage
- **BIG_6_CONSISTENCY**: 1.2 - More predictable Big 6 outcomes

## Troubleshooting

### Common Issues

1. **CORS errors**: Ensure backend is running on port 8000
2. **Module not found**: Run `pip install -r requirements.txt` in backend
3. **npm install fails**: Try `npm install --legacy-peer-deps`
4. **Port already in use**: Change ports in config files
5. **API connection fails**: Check backend server is running

### Port Configuration
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000

### Logs
- **Backend logs**: Console output from FastAPI server
- **Frontend logs**: Browser developer console
- **Network requests**: Browser Network tab

## Future Enhancements

- **Real-time updates**: WebSocket integration for live scores
- **Historical data**: Past gameweek predictions and accuracy
- **User accounts**: Personalized predictions and tracking
- **Mobile app**: React Native or PWA version
- **Advanced analytics**: Player-level statistics integration
- **Betting integration**: Live odds comparison
- **Social features**: Prediction sharing and leagues

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with proper type annotations
4. Test both frontend and backend
5. Submit a pull request

## License

This project is open source and available under the MIT License.
