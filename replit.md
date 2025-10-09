# Premier League Prediction Web App - Replit Project

## Overview
This is a full-stack Premier League match prediction web application deployed on Replit. The project features a React + TypeScript frontend with a FastAPI backend for generating match predictions based on team ratings and statistical models.

## Project Structure
- **Frontend**: React + Vite + TypeScript (in `frontend/` folder)
  - Modern UI built with shadcn/ui components and Tailwind CSS
  - Displays match predictions, team ratings, and historical data
  - Runs on port 5000 in development

- **Backend**: FastAPI Python (deployed separately on Render)
  - Provides RESTful API for predictions and team data
  - Hosted at: https://gwpred-backend.onrender.com/
  - CORS configured for production use

## Current State (as of October 9, 2025)
- ✅ Frontend configured and running on Replit
- ✅ Workflow set up to run frontend on port 5000
- ✅ Deployment configured for autoscale publishing
- ✅ Environment variables configured for backend API connection
- ⚠️ **CORS Configuration Required**: Backend needs to allow Replit domain

## Replit Configuration

### Workflow
- **Name**: Frontend
- **Command**: `cd frontend && npm run dev`
- **Port**: 5000 (webview)
- **Type**: Development server with hot reload

### Deployment Settings
- **Type**: Autoscale (for static web applications)
- **Build Command**: `npm run build` (in frontend folder)
- **Run Command**: `npx vite preview --host 0.0.0.0 --port 5000`
- **Environment Variables**: 
  - `VITE_API_URL=https://gwpred-backend.onrender.com`

### Git Branches
- **main**: Original Python prediction scripts
- **webapp**: Full-stack web application (current branch)
- **replit-agent**: Agent development branch

## Required CORS Configuration

### Backend CORS Setup
The backend at https://gwpred-backend.onrender.com/ needs to allow requests from:
- **Replit Development Domain**: `b681cf65-1b53-413d-b493-f8c69bbb40f4-00-118ov6il7cfti.picard.replit.dev`
- **Deployed Replit Domain**: (will be assigned when published)

To fix CORS issues, update the backend's CORS configuration to include these domains in the allowed origins list.

## Technology Stack
- **Frontend Framework**: React 18 with TypeScript
- **Build Tool**: Vite 4.5
- **UI Components**: shadcn/ui (Radix UI primitives)
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Charts**: Recharts (for data visualization)

## Development
- **Local Development**: Frontend runs on port 5000 with hot reload
- **Backend API**: https://gwpred-backend.onrender.com/
- **API Documentation**: Available at backend URL + `/docs`

## Deployment
To publish this app to the internet:
1. Click the **Publish** button in Replit
2. Choose Autoscale deployment (already configured)
3. Replit will build and deploy the frontend
4. Update backend CORS to include the new deployment URL
5. Access your app via the assigned Replit URL

## Important Notes
- Frontend must run on port 5000 (only exposed port in Replit)
- Vite config set to allow all hosts (required for Replit iframe proxy)
- Environment variables stored in `frontend/.env` for development
- Production environment variables managed via Replit Secrets

## API Endpoints
Base URL: https://gwpred-backend.onrender.com

- `GET /` - API information
- `GET /health` - Health check
- `GET /predictions/{gameweek}` - Get predictions for specific gameweek
- `GET /predictions` - List available gameweeks
- `GET /ratings` - Get current team ratings
- `GET /team/{team_name}` - Get team details and history

## Recent Changes
- 2025-10-09: Initial Replit setup completed
  - Installed Node.js 20
  - Configured Vite for Replit environment (port 5000, allow all hosts)
  - Set up frontend workflow
  - Configured autoscale deployment
  - Created environment configuration for backend API

## Next Steps
1. **Fix CORS**: Update backend to allow Replit domains
2. **Test Deployment**: Publish frontend and verify it works
3. **Custom Domain**: (Optional) Add custom domain to deployment
4. **Enhanced Features**: Add more interactive features and visualizations
