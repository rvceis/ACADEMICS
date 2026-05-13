#!/bin/bash
# Start All Services Script
# Starts PostgreSQL/Redis (Docker), Backend, ML Service, and optionally Frontend

set -e

ROOT_DIR="/home/akash/Desktop/SOlar_Sharing"
BACKEND_DIR="$ROOT_DIR/backend"
ML_SERVICE_DIR="$ROOT_DIR/ml-service"
FRONTEND_DIR="$ROOT_DIR/frontend"

echo "🚀 Starting Solar Sharing Platform..."
echo "=================================="

# 1. Start Docker Compose (PostgreSQL, Redis, etc)
echo ""
echo "1️⃣  Starting Docker services (PostgreSQL, Redis)..."
cd "$BACKEND_DIR"
docker-compose up -d
sleep 3
echo "✅ Docker services started"

# 2. Verify database is ready
echo ""
echo "2️⃣  Verifying database connection..."
max_retries=30
retry_count=0
while [ $retry_count -lt $max_retries ]; do
    if docker exec solar_postgres pg_isready -U postgres > /dev/null 2>&1; then
        echo "✅ PostgreSQL is ready"
        break
    fi
    echo "⏳ Waiting for PostgreSQL... ($((retry_count+1))/$max_retries)"
    sleep 1
    ((retry_count++))
done

if [ $retry_count -eq $max_retries ]; then
    echo "❌ PostgreSQL failed to start"
    exit 1
fi

# 3. Start Backend
echo ""
echo "3️⃣  Starting Backend (port 3000)..."
cd "$BACKEND_DIR"
npm run dev > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
sleep 3

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start. See logs:"
    tail -20 /tmp/backend.log
    exit 1
fi
echo "✅ Backend started (PID: $BACKEND_PID)"

# 4. Start ML Service
echo ""
echo "4️⃣  Starting ML Service (port 8001)..."
cd "$ML_SERVICE_DIR"
source .venv/bin/activate 2>/dev/null || python3 -m venv .venv && source .venv/bin/activate
pip install -q -r requirements.txt 2>/dev/null
uvicorn src.api.main:app --host 0.0.0.0 --port 8001 > /tmp/ml_service.log 2>&1 &
ML_PID=$!
echo "ML Service PID: $ML_PID"
sleep 3

if ! kill -0 $ML_PID 2>/dev/null; then
    echo "❌ ML Service failed to start. See logs:"
    tail -20 /tmp/ml_service.log
    exit 1
fi
echo "✅ ML Service started (PID: $ML_PID)"

# 5. Health checks
echo ""
echo "5️⃣  Running health checks..."
sleep 2

# Check Backend
if curl -s http://localhost:3000/health > /dev/null; then
    echo "✅ Backend is healthy"
else
    echo "⚠️  Backend health check failed"
fi

# Check ML Service
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ ML Service is healthy"
else
    echo "⚠️  ML Service health check failed"
fi

# 6. Optional Frontend
echo ""
read -p "6️⃣  Start Frontend (npm run dev)? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd "$FRONTEND_DIR"
    npm run dev > /tmp/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "✅ Frontend started (PID: $FRONTEND_PID)"
fi

# Summary
echo ""
echo "=================================="
echo "✨ All services started!"
echo "=================================="
echo ""
echo "📊 Service Status:"
echo "  Backend:     http://localhost:3000"
echo "  ML Service:  http://localhost:8001"
if [ ! -z "$FRONTEND_PID" ]; then
    echo "  Frontend:    http://localhost:5173 (or configured port)"
fi
echo ""
echo "🗂️  Log Files:"
echo "  Backend:     /tmp/backend.log"
echo "  ML Service:  /tmp/ml_service.log"
if [ ! -z "$FRONTEND_PID" ]; then
    echo "  Frontend:    /tmp/frontend.log"
fi
echo ""
echo "To stop all services:"
echo "  docker-compose -f $BACKEND_DIR/docker-compose.yml down"
echo "  kill $BACKEND_PID $ML_PID ${FRONTEND_PID:-'<frontend_pid>'}"
echo ""
