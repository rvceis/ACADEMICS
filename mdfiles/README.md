# Solar Sharing - Docker & Run Guide

This guide explains the container setup, why we use a Postgres container even if Postgres is installed locally, the meaning of 2>&1 & in commands, and provides copy-paste commands to run and test the backend and ML service.

## Why a Postgres Container?
- Isolation: Keeps the app’s database fully isolated from your host, avoiding conflicts with your local Postgres version, configs, or plugins.
- Reproducibility: Same Postgres image/version across machines and CI; no “works on my machine” differences.
- Declarative boot: docker-compose brings DB up with the right ports, users, and volumes. No manual host setup.
- Networking: Containers share a network; services can connect via stable hostnames (e.g., postgres) without exposing extra host ports.
- Lifecycle control: Easy reset (docker-compose down -v) and backups via volumes. Useful for dev/testing.
- Security & permissions: Avoids granting your app wide access to a host database; container users and volumes can be tightly scoped.
- Version pinning: You can run a specific Postgres version regardless of what’s installed on the host.

You can still point the app to host Postgres, but for consistent dev and deployment, the DB container is preferred.

## What does 2>&1 & mean?
- 2>&1: Redirects stderr (file descriptor 2) to stdout (file descriptor 1). This merges both streams, useful when you want unified logs or to pipe all output together.
- &: Runs the command in the background, returning control to your shell immediately (useful for long-running processes).

Combined, command 2>&1 & starts a background process and merges its stdout/stderr. You can bring it back with fg or inspect logs separately.

## Project Containers & Files
- Backend: Node.js/Express service on port 3000. See backend/docker-compose.yml.
- ML Service: FastAPI service on port 8001. See ml-service/docker-compose.yml and ml-service/Dockerfile.
- Databases:
  - Backend Postgres/TimescaleDB + Redis via backend compose.
  - ML Postgres + Redis via ML compose.
- MQTT: System Mosquitto on localhost:1883 (backend subscribe/publish).

## Quick Start (Docker)
Run each block in a terminal from the repo root.

### 1) Backend infrastructure
```bash
# Start backend infra (Postgres, Redis, TimescaleDB)
cd backend
docker-compose up -d

# Check containers
docker ps
```

### 2) ML service stack
```bash
# Start ML service (FastAPI + MLflow + ML Postgres/Redis)
cd ../ml-service
docker-compose up -d

# Check containers
docker ps
```

### 3) Start backend app
```bash
cd ../backend
npm install
# Start the Node server in foreground (recommended for dev)
npm start
# Or background (optional):
# npm start 2>&1 &
```

### 4) Health checks
```bash
# Backend health
curl -s http://localhost:3000/health | jq .

# ML service health (container port 8001)
curl -v -s http://localhost:8001/health | head -20
```

If ML health works inside the container but not from host, check port mappings in ml-service/docker-compose.yml and ensure the app binds to 0.0.0.0 (not 127.0.0.1).

## IoT/Device API (Backend)
```bash
# IoT health (mounted at /api/v1)
curl -s http://localhost:3000/api/v1/health | jq .

# Register a device
curl -s -X POST http://localhost:3000/api/v1/devices \
  -H "Content-Type: application/json" \
  -d '{"device_id":"solar_01","name":"Test Solar","capacity_kw":5.0}' | jq .

# List devices
curl -s http://localhost:3000/api/v1/devices | jq .

# Device details
curl -s http://localhost:3000/api/v1/devices/solar_01 | jq .

# Latest forecast for device (if available)
curl -s http://localhost:3000/api/v1/devices/solar_01/forecast | jq .
```

## MQTT Test (Data Ingest)
```bash
# Publish a sample sensor reading (adjust fields to your schema)
mosquitto_pub -h localhost -t "solar/solar_01/data" \
  -m '{"ghi":700,"temperature":28,"hour":14}'

# Optionally subscribe to a forecast topic (if backend publishes it)
mosquitto_sub -h localhost -t "solar/solar_01/forecast" -C 1
```

## ML Service Endpoints (Examples)
Note: Paths may be versioned depending on configuration. These examples use the commonly exposed routes.
```bash
# Health
echo "=== ML Health ==="
curl -s http://localhost:8001/health | jq .

# Solar forecast (single point)
echo "=== ML Forecast ==="
curl -s -X POST http://localhost:8001/forecast \
  -H "Content-Type: application/json" \
  -d '{"device_id":"solar_01","ghi":700,"temperature":28}' | jq .

# Anomaly detection
echo "=== ML Anomaly ==="
curl -s -X POST http://localhost:8001/api/v1/anomaly/detect \
  -H "Content-Type: application/json" \
  -d '{"power_kw": 5.2, "voltage_v": 240, "frequency_hz": 50.0}' | jq .
```

If you see Connection reset by peer from the host but not inside the container, confirm:
- ML app binds to 0.0.0.0.
- Port 8001 is published in ml-service/docker-compose.yml (e.g., 8001:8001).
- No firewall rules block localhost.

## Common Troubleshooting
- Port conflicts: Ensure host ports (e.g., 5432, 6379, 8001, 3000, 1883) aren’t already in use. Change mappings in the compose files if needed.
- Container logs:
  - Backend: docker logs <backend-app-container> or the foreground npm start output.
  - ML service: docker logs solar-ml-service (adjust name if different).
- Reset dev state: docker-compose down -v in respective folders to remove containers and volumes, then docker-compose up -d.
- MQTT: Ensure Mosquitto is running (systemctl status snap.mosquitto.mosquitto.service) and publishing/subscribing works.

## Notes on Background Processes
Only use & when you explicitly want a command to keep running without tying up your current terminal. For development, prefer foreground so you see logs. For background use, consider process managers (PM2, systemd) instead of raw &.

---
If you want, I can also verify and expand ML endpoints (demand forecasting, pricing, risk, equipment failure) and align backend ↔ ML client paths. Let me know and I’ll implement and test those next.
