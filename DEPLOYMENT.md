# Deployment Guide

This guide covers deploying the Premier League Prediction System to production environments.

## Production Deployment

The application is deployed using:
- **Frontend**: Vercel (automatic deployments from GitHub)
- **Backend**: Railway (containerized Python API)

## Backend Deployment (Railway)

### Prerequisites
- Railway account
- GitHub repository connected to Railway
- Python 3.11+ environment

### Configuration Files

**Procfile** (already configured):
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**railway.toml** (already configured):
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### Environment Variables
Set these in Railway dashboard:
```
PORT=8000
CORS_ORIGINS=https://gwpred.vercel.app,https://gwpred-2z4z.vercel.app
```

### Deployment Steps
1. Connect GitHub repository to Railway
2. Railway will auto-detect Python and install dependencies
3. Set environment variables in Railway dashboard
4. Deploy automatically on git push

## Frontend Deployment (Vercel)

### Prerequisites
- Vercel account
- GitHub repository connected to Vercel
- Node.js 18+ environment

### Configuration Files

**vercel.json** (already configured):
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite"
}
```

### Environment Variables
Set these in Vercel dashboard:
```
VITE_API_URL=https://gwpredictor.up.railway.app
```

### Deployment Steps
1. Connect GitHub repository to Vercel
2. Vercel will auto-detect Vite/React project
3. Set environment variables in Vercel dashboard
4. Deploy automatically on git push

## Local Development vs Production

### API URLs
- **Local Development**: `http://localhost:8000`
- **Production**: `https://gwpredictor.up.railway.app`

### CORS Configuration
The backend automatically configures CORS based on environment:
- **Local**: Allows `localhost:3000` and `localhost:5173`
- **Production**: Allows Vercel domains and Railway domain

## Monitoring and Health Checks

### Health Check Endpoint
- **URL**: `/health`
- **Response**: `{"status": "healthy", "timestamp": "..."}`
- **Railway**: Automatically configured for health checks

### API Documentation
- **Local**: `http://localhost:8000/docs`
- **Production**: `https://gwpredictor.up.railway.app/docs`

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Check CORS_ORIGINS environment variable
   - Ensure frontend URL is included in allowed origins

2. **Build Failures**
   - Check Python/Node.js version compatibility
   - Verify all dependencies are in requirements.txt/package.json

3. **API Connection Issues**
   - Verify VITE_API_URL is set correctly
   - Check Railway deployment logs

4. **Environment Variables**
   - Ensure all required variables are set in both platforms
   - Check variable names match exactly

### Logs and Debugging

**Railway Backend Logs**:
- Access via Railway dashboard
- Check for Python errors and API issues

**Vercel Frontend Logs**:
- Access via Vercel dashboard
- Check build logs and function logs

## Manual Deployment

If automatic deployment fails:

### Backend (Railway)
```bash
# Build and test locally
cd backend
pip install -r requirements.txt
python main.py

# Deploy via Railway CLI
railway login
railway link
railway up
```

### Frontend (Vercel)
```bash
# Build and test locally
cd frontend
npm install
npm run build
npm run preview

# Deploy via Vercel CLI
vercel login
vercel --prod
```

## Security Considerations

- Environment variables are properly secured in both platforms
- CORS is configured to only allow specific origins
- No sensitive data is exposed in client-side code
- API endpoints include proper error handling

## Performance Optimization

- Frontend uses Vite for fast builds and hot reload
- Backend uses FastAPI for high performance
- Static assets are served via CDN (Vercel)
- API responses are optimized with proper caching headers
