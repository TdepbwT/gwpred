# Football Prediction App - Deployment Guide

## Live Application
- **Frontend**: https://gwpred.vercel.app
- **Backend API**: https://gwpredictor.up.railway.app
- **API Documentation**: https://gwpredictor.up.railway.app/docs

## 🏗️ Vercel + Railway Deployment

### Prerequisites
- GitHub account with your forked repository
- Vercel account (free tier available)
- Railway account (free tier available)

### Step 1: Prepare Repository
Your code is now ready for deployment with the necessary configuration files:
- `frontend/vercel.json` - Vercel deployment configuration
- `backend/Procfile` - Railway startup commands
- `backend/railway.toml` - Railway build configuration

### Step 2: Deploy Backend on Railway

1. **Sign up for Railway**: Go to [railway.app](https://railway.app) and sign up with GitHub
2. **Create new project**: Click "New Project" → "Deploy from GitHub repo"
3. **Select repository**: Choose your `gwpred` repository
4. **Configure backend service**:
   - Railway may detect multiple services, ensure you select/configure the backend
   - Root directory should be set to `backend/`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Set environment variables**:
   - Go to your service → Variables tab
   - Add: `PORT` = `8000`
   - Add: `CORS_ORIGINS` = `https://your-app-name.vercel.app` (you'll get this from Vercel)
6. **Deploy**: Railway will automatically build and deploy your FastAPI app
7. **Get your backend URL**: Copy the generated Railway URL (e.g., `https://gwpredictor.up.railway.app`)

### Step 3: Deploy Frontend on Vercel

1. **Sign up for Vercel**: Go to [vercel.com](https://vercel.com) and sign up with GitHub
2. **Import project**: Click "Add New..." → "Project"
3. **Select repository**: Choose your `gwpred` repository
4. **Configure build settings**:
   - Framework Preset: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`
5. **Set environment variables**:
   - Add: `VITE_API_URL` = `https://your-railway-backend-url.railway.app`
   - Example: `VITE_API_URL` = `https://gwpredictor.up.railway.app`
6. **Deploy**: Vercel will build and deploy your React app
7. **Get your frontend URL**: Copy the generated Vercel URL (e.g., `https://gwpred.vercel.app`)

### Step 4: Update CORS Settings

1. Go back to Railway dashboard
2. Navigate to your backend service → Variables
3. Update the `CORS_ORIGINS` environment variable with your actual Vercel URL
4. Example: `CORS_ORIGINS` = `https://gwpred.vercel.app`
5. Railway will automatically redeploy with the new settings

### Your app is now live!

Access your application at the Vercel URL and verify it can fetch data from the Railway backend.

## Environment Variables Reference

### Backend Railway Environment
```bash
PORT=8000
CORS_ORIGINS=https://gwpred.vercel.app
```

### Frontend Vercel Environment
```bash
VITE_API_URL=https://gwpredictor.up.railway.app
```

## Testing Deployment

### Backend API Testing
```bash
# Health check
curl https://gwpredictor.up.railway.app/health

# Get available predictions
curl https://gwpredictor.up.railway.app/predictions

# Get specific gameweek
curl https://gwpredictor.up.railway.app/predictions/2

# Get team ratings
curl https://gwpredictor.up.railway.app/ratings
```

### Frontend Testing
1. Visit your Vercel URL
2. Check that predictions load correctly
3. Verify team ratings are displayed
4. Test tab switching functionality
5. Check browser console for any errors

## Troubleshooting

### Common Issues

#### CORS Errors
- **Problem**: Frontend can't access backend API
- **Solution**: Ensure `CORS_ORIGINS` in Railway includes exact Vercel URL
- **Check**: No trailing slashes, use `https://`, not `http://`

#### Build Failures on Vercel
- **Problem**: Frontend build fails
- **Solution**: Ensure Node.js 18+ is used, check build logs
- **Fix**: Verify all dependencies in `package.json`

#### API Returns HTML Instead of JSON
- **Problem**: Backend not properly deployed
- **Solution**: Check Railway logs, verify Python dependencies
- **Fix**: Ensure `requirements.txt` is complete and `main.py` is in root

#### 404 Errors on Frontend Routes
- **Problem**: React Router not configured for production
- **Solution**: `vercel.json` should handle SPA routing (already included)

### Debug Steps
1. **Check Railway logs**: Go to Railway dashboard → your service → Logs
2. **Check Vercel logs**: Go to Vercel dashboard → your project → Functions tab
3. **Test API directly**: Use curl or browser to test API endpoints
4. **Check browser console**: Look for JavaScript errors or network failures

## Estimated Costs

### Free Tier Limits
- **Vercel**: 
  - 6,000 serverless function invocations/month
  - 1,000 build minutes/month
  - 100 GB bandwidth/month
- **Railway**: 
  - 500 execution hours/month
  - Shared CPU/memory
  - Custom domain not included

### Paid Tier Costs
- **Vercel Pro**: $20/month per member
- **Railway Pro**: $5/month + usage-based pricing
- **Total**: ~$5-25/month depending on usage

### Recommendations
- **Development**: Use free tiers
- **Production**: Consider Railway Pro for better performance
- **High Traffic**: Monitor usage and upgrade as needed

## Automatic Deployments

Both platforms support automatic deployments:

### Vercel
- Deploys on every push to main branch
- Creates preview deployments for pull requests
- Build logs available in dashboard

### Railway
- Deploys on every push to main branch
- Zero-downtime deployments
- Runtime logs and metrics available

### GitHub Integration
- Connect repository to both platforms
- Push code changes to trigger automatic deployments
- Monitor deployment status in platform dashboards

## Security Best Practices

1. **Environment Variables**: Never commit secrets to git
2. **CORS Configuration**: Only allow necessary origins
3. **HTTPS**: Both platforms enforce HTTPS by default
4. **Dependencies**: Keep packages updated for security patches
5. **API Rate Limiting**: Consider implementing rate limiting for production

## Alternative Deployment Options

### Backend Alternatives
- **Heroku**: Easy deployment with git push
- **Render**: Free tier with automatic SSL
- **DigitalOcean App Platform**: Competitive pricing
- **AWS/GCP/Azure**: Enterprise-grade infrastructure

### Frontend Alternatives
- **Netlify**: Similar to Vercel with generous free tier
- **GitHub Pages**: Free for public repositories
- **Firebase Hosting**: Google's hosting solution
- **Cloudflare Pages**: Fast global CDN

## Monitoring and Maintenance

### Health Monitoring
- Set up uptime monitoring (UptimeRobot, Pingdom)
- Monitor API response times
- Check error rates in platform dashboards

### Maintenance Tasks
- Regular dependency updates
- Monitor platform usage and costs
- Backup important data/configurations
- Review and rotate secrets periodically

---

For technical details about the application architecture, see the [main README](README.md).
For local development setup, see the [project documentation](README.md#development).
