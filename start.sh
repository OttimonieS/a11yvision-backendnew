#!/bin/bash

# Render startup script for A11y Vision Backend

echo "Starting A11y Vision Backend..."

# Navigate to app directory
cd backend/app

# Initialize database if needed
echo "Initializing database..."
python init_db.py || echo "Database initialization skipped or failed"

# Start the application
echo "Starting uvicorn server..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
