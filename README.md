# A11y Vision Backend

Backend API for the A11y Vision accessibility auditing platform. This FastAPI application provides automated web accessibility scanning using Playwright and computer vision techniques.

## Features

- 🔍 Automated accessibility scanning of web pages
- 📸 Full-page screenshot capture
- 🎯 WCAG compliance checking
- 🔐 User authentication & API keys
- 📊 Scan history and results tracking
- 🗄️ PostgreSQL database integration

## Tech Stack

- **Framework**: FastAPI
- **Browser Automation**: Playwright
- **Image Processing**: OpenCV, Pillow, NumPy
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Server**: Uvicorn

## Project Structure

```
a11yvision-backend/
├── app/
│   ├── main.py              # Main FastAPI application
│   ├── api.py               # API route handlers
│   ├── worker.py            # Background scan worker
│   ├── analyzer.py          # Image analysis logic
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── activity_logger.py   # Activity logging
│   ├── init_db.py          # Database initialization
│   ├── test_db_connection.py # Database testing
│   └── data/
│       ├── screenshots/     # Screenshot storage
│       └── uploads/         # Upload storage
├── requirements.txt         # Python dependencies
├── runtime.txt             # Python version
├── Dockerfile              # Container definition
├── docker-compose.yml      # Local development setup
├── render.yaml             # Render.com deployment config
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Node.js (for frontend integration)

### Local Development

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/a11yvision-backend.git
   cd a11yvision-backend
   ```

2. **Create environment file**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your configuration.

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Start PostgreSQL** (using Docker)

   ```bash
   docker-compose up -d postgres
   ```

5. **Initialize database**

   ```bash
   cd app
   python init_db.py
   ```

6. **Run the application**

   ```bash
   cd app
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the API**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health

### Using Docker Compose

Run the entire stack (PostgreSQL + Backend):

```bash
docker-compose up --build
```

## Deployment to Render.com

### Method 1: Using render.yaml (Recommended)

1. **Push your code to GitHub**

   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Create a new Blueprint on Render**

   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`

3. **Configure environment variables** (if needed)
   The `render.yaml` file handles most configuration, but you can add additional variables in the Render dashboard.

4. **Deploy**
   - Click "Apply" to start the deployment
   - Render will create both the PostgreSQL database and the web service
   - Wait for the build and deployment to complete

### Method 2: Manual Setup

1. **Create PostgreSQL Database**

   - Go to Render Dashboard
   - Click "New" → "PostgreSQL"
   - Name: `a11yvision-db`
   - Choose your plan (Free tier available)
   - Create database

2. **Create Web Service**

   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `a11yvision-backend`
     - **Environment**: `Python 3`
     - **Region**: Choose closest to your users
     - **Branch**: `main`
     - **Build Command**:
       ```bash
       pip install -r requirements.txt && playwright install --with-deps chromium
       ```
     - **Start Command**:
       ```bash
       cd backend/app && uvicorn main:app --host 0.0.0.0 --port $PORT
       ```

3. **Add Environment Variables**

   - `DATABASE_URL`: (Auto-populated from database)
   - `PLAYWRIGHT_BROWSERS_PATH`: `/opt/render/.cache/ms-playwright`
   - `ENVIRONMENT`: `production`
   - Add any others from `.env.example`

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete

### Post-Deployment

4. **Initialize Database Tables**
   Access your Render shell and run:

   ```bash
   cd app && python init_db.py
   ```

5. **Test Your API**

   ```bash
   curl https://your-app-name.onrender.com/health
   ```

6. **View Logs**
   Monitor logs in the Render dashboard under the "Logs" tab.

## API Endpoints

### Authentication

- `POST /api/v1/auth/signup` - Create new account
- `POST /api/v1/auth/signin` - Sign in
- `POST /api/v1/auth/logout` - Sign out
- `GET /api/v1/auth/me` - Get current user

### Scans

- `GET /api/v1/scans` - List all scans
- `POST /api/v1/scans` - Create new scan
- `GET /api/v1/scans/{scan_id}` - Get scan status
- `GET /api/v1/scans/{scan_id}/result` - Get scan results
- `GET /api/v1/scans/{scan_id}/issues` - Get issues only

### Settings

- `GET /api/v1/settings` - Get user settings
- `PUT /api/v1/settings` - Update settings

### API Keys

- `GET /api/v1/api-keys` - List API keys
- `POST /api/v1/api-keys` - Create new API key
- `DELETE /api/v1/api-keys/{key_id}` - Delete API key

### Stats

- `GET /api/v1/stats` - Get dashboard statistics

### Uploads

- `POST /api/v1/uploads` - Upload screenshot

### Health

- `GET /health` - Health check

## Environment Variables

| Variable                   | Description                          | Default                                                  |
| -------------------------- | ------------------------------------ | -------------------------------------------------------- |
| `DATABASE_URL`             | PostgreSQL connection string         | `postgresql://postgres:postgres@localhost:5432/visionai` |
| `PLAYWRIGHT_BROWSERS_PATH` | Playwright browser cache path        | `/ms-playwright`                                         |
| `ENVIRONMENT`              | Environment (development/production) | `development`                                            |
| `ALLOWED_ORIGINS`          | CORS allowed origins                 | `http://localhost:5173,*`                                |
| `SECRET_KEY`               | Application secret key               | (generate securely)                                      |

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black backend/app
isort backend/app
```

### Database Migrations

```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Troubleshooting

### Playwright Issues on Render

- Ensure `playwright install --with-deps chromium` is in build command
- Set `PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright`

### Database Connection Issues

- Verify `DATABASE_URL` environment variable is set correctly
- Check database is running and accessible
- Ensure PostgreSQL version compatibility (15+)

### Memory Issues

- Render free tier has 512MB RAM limit
- Consider upgrading to a paid plan for production use
- Optimize Playwright to use `chromium` only (not full browser suite)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:

- Create an issue on GitHub
- Check the documentation at `/docs` endpoint
- Review Render.com deployment logs

## Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Playwright Documentation](https://playwright.dev/python/)
- [Render.com Documentation](https://render.com/docs)
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
