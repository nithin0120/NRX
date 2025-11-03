#!/bin/bash

echo "Starting Neural Remix Engine (Development Mode)"
echo "================================================"

if ! command -v redis-server &> /dev/null; then
    echo "Error: Redis is not installed. Install with: brew install redis"
    exit 1
fi

echo "Starting Redis..."
redis-server --daemonize yes

echo "Starting FastAPI backend..."
cd "$(dirname "$0")"
python -m backend.main &
BACKEND_PID=$!

echo "Starting Celery worker..."
celery -A backend.tasks worker --loglevel=info &
WORKER_PID=$!

echo ""
echo "Services running:"
echo "- Backend API: http://localhost:8000"
echo "- Redis: localhost:6379"
echo ""
echo "Press Ctrl+C to stop all services"

trap "kill $BACKEND_PID $WORKER_PID; redis-cli shutdown; exit" INT

wait

