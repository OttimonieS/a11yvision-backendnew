# Quick Start Guide

## Local Development (5 minutes)

### Prerequisites
- Python 3.11+
- Docker Desktop (for PostgreSQL)

### Setup

1. **Clone and Navigate**
   ```bash
   cd a11yvision-backend
   ```

2. **Create Environment File**
   ```bash
   cp .env.example .env
   ```

3. **Start Database**
   ```bash
   docker-compose up -d postgres
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

5. **Initialize Database**
   ```bash
   cd backend/app
   python init_db.py
   ```
   (Answer 'y' for test data in development)

6. **Run Application**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Test**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health

### Test Credentials
- Email: `test@example.com`
- Password: `password123`

---

## Deploy to Render.com (10 minutes)

### One-Command Deploy

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Deploy to Render"
   git push origin main
   ```

2. **Create Blueprint on Render**
   - Go to https://dashboard.render.com/
   - Click "New" → "Blueprint"
   - Connect your repository
   - Click "Apply"
   - Wait 5-10 minutes for build

3. **Initialize Database**
   - Open your web service shell on Render
   - Run: `python backend/app/init_db.py`
   - Answer 'n' for test data

4. **Test**
   ```bash
   curl https://your-app.onrender.com/health
   ```

**Done!** 🎉

---

## Docker (Alternative)

### Run Everything with Docker

```bash
docker-compose up --build
```

Access at http://localhost:8000

---

## Troubleshooting

### Database Connection Error
```bash
# Check if PostgreSQL is running
docker ps

# Restart database
docker-compose restart postgres
```

### Playwright Issues
```bash
# Reinstall browsers
playwright install --with-deps chromium
```

### Port Already in Use
```bash
# Change port in command
uvicorn main:app --reload --port 8001
```

---

## Quick Commands

```bash
# Run tests
pytest

# Format code
black backend/app
isort backend/app

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Clean restart
docker-compose down -v && docker-compose up --build
```

---

## API Quick Reference

### Create User
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass123","name":"User"}'
```

### Create Scan
```bash
curl -X POST http://localhost:8000/api/v1/scans \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"url":"https://example.com","mode":"static"}'
```

### Get Scan Result
```bash
curl http://localhost:8000/api/v1/scans/SCAN_ID/result \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

For detailed documentation, see:
- [README.md](README.md) - Full documentation
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
- API Docs: http://localhost:8000/docs (when running)
