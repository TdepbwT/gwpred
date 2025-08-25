# Football Prediction App - Deployment Guide

## Vercel + Railway Deployment

### Prerequisites
- GitHub account
- Vercel account (free)
- Railway account (free tier available)

### Step 1: Prepare Repository
Your code is now ready for deployment with the necessary configuration files.

### Step 2: Deploy Backend on Railway

1. **Sign up for Railway**: Go to [railway.app](https://railway.app) and sign up with GitHub
2. **Create new project**: Click "New Project" → "Deploy from GitHub repo"
3. **Select repository**: Choose your `gwpred` repository
4. **Configure backend**:
   - Railway will detect multiple services, select the `backend` folder
   - Or create a new service and connect your repo
5. **Set environment variables**:
   - Go to your service → Variables tab
   - Add: `PORT` = `8000`
   - Add: `CORS_ORIGINS` = `https://your-app-name.vercel.app` (you'll get this from Vercel)
6. **Deploy**: Railway will automatically build and deploy your FastAPI app
7. **Get your backend URL**: Copy the generated Railway URL (e.g., `https://your-app-name.railway.app`)

### Step 3: Deploy Frontend on Vercel

1. **Sign up for Vercel**: Go to [vercel.com](https://vercel.com) and sign up with GitHub
2. **Import project**: Click "Add New..." → "Project"
3. **Select repository**: Choose your `gwpred` repository
4. **Configure build settings**:
   - Framework Preset: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
5. **Set environment variables**:
   - Add: `VITE_API_URL` = `https://your-railway-backend-url.railway.app`
6. **Deploy**: Vercel will build and deploy your React app
7. **Get your frontend URL**: Copy the generated Vercel URL

### Step 4: Update CORS Settings

1. Go back to Railway
2. Update the `CORS_ORIGINS` environment variable with your actual Vercel URL
3. Redeploy the backend service

### Your app is now live! 🎉

## Environment Variables Reference

### Backend (.env)
```
PORT=8000
CORS_ORIGINS=https://your-frontend-domain.vercel.app
```

### Frontend (.env)
```
VITE_API_URL=https://your-backend-domain.railway.app
```

## Estimated Costs
- **Vercel**: Free tier (generous limits)
- **Railway**: $5/month after free tier
- **Total**: ~$5/month

## Monitoring
- **Vercel**: Automatic deployments on git push
- **Railway**: Automatic deployments on git push
- Both platforms provide logs and monitoring dashboards
