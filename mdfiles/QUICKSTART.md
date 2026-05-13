# 🚀 Quick Start Guide - Solar Sharing Platform

## Prerequisites
- Docker & Docker Compose installed
- Node.js 18+ and npm
- Python 3.10+ with venv
- PostgreSQL client (optional, for debugging)

## Starting All Services

### Step 1: Start Database & Cache (Docker)
```bash
cd backend/
docker-compose up -d

# Verify services are running:
docker ps
```

**Expected Output:** 3 healthy containers
- ✅ solar_postgres (PostgreSQL on port 5434)
- ✅ solar_redis (Redis on port 6380)
- ✅ solar_timescaledb (TimescaleDB on port 5433)

### Step 2: Start Backend Service
```bash
cd backend/
npm install  # if needed
npm run dev
```

**Expected Output:**
```
[timestamp] INFO: Database connection successful
[timestamp] INFO: Server running on http://localhost:3000
[timestamp] INFO: ✓ IoT Manager initialized with MQTT
```

**Troubleshooting:**
- If database connection fails, ensure `docker-compose up -d` completed
- Check `.env` file has correct credentials (defaults: user/pass = postgres)
- Logs are in `backend/server.log`

### Step 3: Start ML Service
```bash
cd ml-service/
source .venv/bin/activate
pip install -r requirements.txt  # if needed
uvicorn src.api.main:app --host 0.0.0.0 --port 8001 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8001
✅ Loaded solar_xgboost from models/solar_xgboost_model.pkl
Ready for inference: 1/8 models available
```

**Troubleshooting:**
- CUDA/TensorFlow warnings are normal (CPU inference)
- If models not loading, models/ directory might not exist (auto-created on first train)

### Step 4: Start Frontend (Optional)
```bash
cd frontend/
npm install  # if needed
npm run dev
```

**Expected Output:**
```
  ➜  Local:   http://localhost:5173/
```

---

## Verification

### Health Checks
```bash
# Backend
curl http://localhost:3000/health

# ML Service
curl http://localhost:8001/health
```

Both should return JSON with status: "healthy"

### Run Integration Tests
```bash
cd /home/akash/Desktop/SOlar_Sharing
python3 run_integration_tests.py
```

**Expected:** ✅ All tests PASS

---

## Quick Commands

### Check Model Status
```bash
python3 check_model_status.py
```
Shows which ML models are loaded and can trigger training.

### View Logs
```bash
# Backend
tail -f backend/server.log

# ML Service (if using --reload)
# logs appear in terminal

# Docker
docker logs solar_postgres
docker logs solar_redis
```

### Stop Everything
```bash
# Stop services
pkill -f "npm run dev"
pkill -f "uvicorn"

# Stop Docker containers
cd backend/
docker-compose down

# Stop and remove volumes (wipe data)
docker-compose down -v
```

### Reset Everything
```bash
# Stop containers
cd backend/
docker-compose down -v

# Clear Node modules
rm -rf backend/node_modules
rm -rf frontend/node_modules

# Start fresh
docker-compose up -d
npm install
npm run dev
```

---

## Environment Variables

Located in `backend/.env`:

```
# Database (matches docker-compose.yml)
DB_HOST=localhost
DB_PORT=5434
DB_NAME=solar_platform
DB_USER=postgres
DB_PASSWORD=postgres

# Redis
REDIS_HOST=localhost
REDIS_PORT=6380

# ML Service
ML_SERVICE_URL=http://localhost:8001
ML_SERVICE_ENABLED=true

# JWT & Security
JWT_SECRET=your-secret-here
JWT_EXPIRY=24h
```

---

## Common Issues

### "Database connection failed"
- ✅ Is Docker running? `docker ps`
- ✅ Did docker-compose start? `docker ps | grep postgres`
- ✅ Is port 5434 available? `lsof -i :5434`

### "Cannot find module"
- ✅ Run `npm install` in backend/ or frontend/
- ✅ Check Node.js version: `node --version` (need 18+)

### "Port already in use"
- ✅ Kill process: `lsof -i :3000` then `kill -9 <PID>`
- ✅ Or use different port: `PORT=3001 npm run dev`

### "ML Service not responding"
- ✅ Check port 8001: `curl http://localhost:8001/health`
- ✅ Ensure Python venv: `source ml-service/.venv/bin/activate`
- ✅ Check logs for TensorFlow errors (usually non-critical)

### "Redis errors"
- ✅ Optional for development (many features work without it)
- ✅ Verify: `docker logs solar_redis`

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│           Frontend (React Native/Expo)          │
│         http://localhost:5173                   │
└─────────────────┬───────────────────────────────┘
                  │ API Calls
┌─────────────────▼───────────────────────────────┐
│         Backend (Node.js/Express)               │
│         http://localhost:3000                   │
├─────────────────┬───────────────────────────────┤
│                 │ Predictions
│      ┌──────────▼──────────┐                    │
│      │  ML Service         │                    │
│      │ (Python/FastAPI)    │                    │
│      │ port 8001           │                    │
│      └─────────────────────┘                    │
└─────────────────┬───────────────────────────────┘
                  │ Data Storage
        ┌─────────┴──────────┐
        │                    │
   ┌────▼────┐        ┌─────▼──┐
   │PostgreSQL│        │ Redis  │
   │ 5434     │        │ 6380   │
   └──────────┘        └────────┘
```

---

## Next Steps

1. **Configure Email/SMS** (optional):
   - Update Sendgrid API key in `.env`
   - Update Twilio credentials for SMS

2. **Setup Payment Gateway** (optional):
   - Add Razorpay or Stripe keys in `.env`

3. **Connect Real IoT Devices** (optional):
   - Configure MQTT broker details
   - Set `MQTT_ENABLED=true` in `.env`

4. **Train ML Models** (optional):
   - Run `python3 check_model_status.py`
   - Select "y" to train models
   - Models persist and auto-load on service restart

---

## Support

For issues or questions:
1. Check logs: `backend/server.log`
2. Run integration tests: `python3 run_integration_tests.py`
3. Check Docker status: `docker-compose ps`

