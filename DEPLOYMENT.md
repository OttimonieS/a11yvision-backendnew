# Deployment Checklist for Render.com

## Pre-Deployment

- [ ] All code is committed to Git
- [ ] `.env.example` file is present (don't commit actual `.env`)
- [ ] `requirements.txt` is up to date
- [ ] `runtime.txt` specifies Python 3.11.0
- [ ] `Dockerfile` is configured correctly
- [ ] `render.yaml` is configured
- [ ] README.md has deployment instructions

## Files Required for Render

### Root Directory Files

- [x] `requirements.txt` - Python dependencies
- [x] `runtime.txt` - Python version specification
- [x] `Dockerfile` - Container configuration
- [x] `docker-compose.yml` - Local development
- [x] `render.yaml` - Render blueprint configuration
- [x] `.env.example` - Environment variables template
- [x] `.gitignore` - Git ignore rules
- [x] `README.md` - Documentation
- [x] `start.sh` - Startup script
- [x] `build.sh` - Build script

### Backend Application Files

- [x] `app/main.py` - FastAPI application
- [x] `app/api.py` - API routes
- [x] `app/worker.py` - Background worker
- [x] `app/analyzer.py` - Image analysis
- [x] `app/database.py` - Database config
- [x] `app/models.py` - SQLAlchemy models
- [x] `app/activity_logger.py` - Activity logging
- [x] `app/init_db.py` - Database initialization

## Render.com Deployment Steps

### Method 1: Blueprint (Recommended)

1. **Push to GitHub**

   ```bash
   git add .
   git commit -m "Ready for Render deployment"
   git push origin main
   ```

2. **Create Blueprint on Render**

   - Go to https://dashboard.render.com/
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Select the repository
   - Render will detect `render.yaml` automatically
   - Click "Apply"

3. **Wait for Deployment**

   - Database will be created first
   - Then the web service will build and deploy
   - Check logs for any errors

4. **Initialize Database**

   - Once deployed, go to the web service shell
   - Run: `cd app && python init_db.py`
   - Answer 'n' for test data in production

5. **Test Your API**
   - Visit: `https://your-app-name.onrender.com/health`
   - Check API docs: `https://your-app-name.onrender.com/docs`

### Method 2: Manual Setup

1. **Create PostgreSQL Database**

   - New → PostgreSQL
   - Name: `a11yvision-db`
   - Plan: Free
   - Create Database

2. **Create Web Service**

   - New → Web Service
   - Connect GitHub repo
   - **Build Command**:
     ```
     pip install --upgrade pip && pip install -r requirements.txt && playwright install --with-deps chromium
     ```
   - **Start Command**:
     ```
     bash start.sh
     ```
   - **Environment Variables**:
     - `DATABASE_URL` (from database)
     - `PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright`
     - `ENVIRONMENT=production`

3. **Deploy and Test**

## Environment Variables

Set these in Render Dashboard:

```
DATABASE_URL=postgresql://user:pass@host:port/db (auto from DB)
PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-frontend.com,*
```

## Post-Deployment

- [ ] Test health endpoint: `/health`
- [ ] Test API docs: `/docs`
- [ ] Create a test user via `/api/v1/auth/signup`
- [ ] Test creating a scan via `/api/v1/scans`
- [ ] Monitor logs for errors
- [ ] Set up monitoring/alerts (optional)

## Common Issues

### Playwright Browser Install Failed

**Solution**: Ensure build command includes:

```
playwright install --with-deps chromium
```

### Database Connection Error

**Solution**:

- Check DATABASE_URL is set correctly
- Ensure database is running
- Run init_db.py to create tables

### Out of Memory

**Solution**:

- Render free tier has 512MB RAM
- Upgrade to paid plan for production
- Only install chromium browser (not all browsers)

### Module Import Errors

**Solution**:

- Ensure all dependencies are in requirements.txt
- Check Python version in runtime.txt matches

## Monitoring

After deployment, monitor:

- Response times in Render dashboard
- Error logs
- Database connection pool
- Memory usage

## Rollback Plan

If deployment fails:

1. Check logs in Render dashboard
2. Fix issues locally
3. Test with `docker-compose up`
4. Commit and push fixes
5. Render will auto-deploy (if enabled)

## Success Criteria

Deployment is successful when:

- [x] Health endpoint returns `{"ok": true}`
- [x] API docs are accessible
- [x] Can create user account
- [x] Can create and view scans
- [x] Screenshots are captured
- [x] No errors in logs

## Next Steps After Deployment

1. Configure custom domain (optional)
2. Set up SSL (automatic with Render)
3. Connect frontend application
4. Set up monitoring
5. Configure backups
6. Add rate limiting
7. Implement caching (Redis)

---

**Last Updated**: 2025-11-22
**Status**: Ready for Deployment ✓
