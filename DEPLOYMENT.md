# Deployment Guide

## Production Deployment

### Frontend (Vercel)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Migrate to Next.js + FastAPI"
   git push origin main
   ```

2. **Deploy to Vercel**:
   - Visit [vercel.com](https://vercel.com)
   - Import GitHub repository
   - Set Root Directory: `frontend`
   - Framework Preset: Next.js
   - Add environment variable:
     - `NEXT_PUBLIC_API_URL`: Your backend URL

3. **Configure for iframe embedding**:
   - Add CSP headers in `next.config.js`:
   ```javascript
   async headers() {
     return [{
       source: '/:path*',
       headers: [
         { key: 'X-Frame-Options', value: 'ALLOW-FROM https://policyengine.org' },
       ],
     }];
   }
   ```

### Backend (Google Cloud Run)

1. **Build Docker image**:
   ```bash
   cd backend
   docker build -t marginal-child-backend .
   ```

2. **Push to Google Container Registry**:
   ```bash
   docker tag marginal-child-backend gcr.io/PROJECT_ID/marginal-child-backend
   docker push gcr.io/PROJECT_ID/marginal-child-backend
   ```

3. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy marginal-child-backend \
     --image gcr.io/PROJECT_ID/marginal-child-backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars CORS_ORIGINS=https://your-vercel-app.vercel.app
   ```

### Alternative: Railway

**Backend:**
1. Connect GitHub repo to Railway
2. Set Root Directory: `backend`
3. Add environment variables
4. Railway will auto-detect FastAPI and deploy

**Frontend:**
- Use Vercel (easier for Next.js)

## Environment Variables

### Production Backend

```env
CORS_ORIGINS=https://marginal-child.vercel.app,https://policyengine.org
PORT=8000
```

### Production Frontend

```env
NEXT_PUBLIC_API_URL=https://marginal-child-backend.run.app
```

## Iframe Integration

To embed in policyengine.org (app-v2):

```tsx
<iframe
  src="https://marginal-child.vercel.app"
  width="100%"
  height="800px"
  frameBorder="0"
  title="The Marginal Child Calculator"
/>
```

**URL parameters** (for deep linking):
```
https://marginal-child.vercel.app?country=UK&metric=mtr&view=absolute&maxChildren=3
```

## Performance Optimization

### Backend Caching

Add Redis for caching calculation results:

```python
# In backend/app/main.py
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="marginal-child")
```

### Frontend Optimization

- Enable SWR/TanStack Query for client-side caching
- Add loading skeletons
- Debounce calculation triggers
- Preload common scenarios

## Monitoring

- **Backend**: Add Sentry for error tracking
- **Frontend**: Add Vercel Analytics
- **API**: Log calculation requests for usage analytics

## Cost Estimates

**Vercel** (Frontend):
- Free tier: ~100GB bandwidth/month
- Pro: $20/month for production apps

**Google Cloud Run** (Backend):
- ~$0.10 per 100k requests
- Estimate: $5-20/month depending on usage

**Total**: ~$25-40/month for production deployment
