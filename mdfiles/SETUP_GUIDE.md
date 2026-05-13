# Solar Energy Sharing Platform - Setup & Running Guide

## 📋 Prerequisites

### System Requirements
- **Node.js**: v18+ (LTS recommended)
- **npm**: v9+ or **yarn** v3+
- **PostgreSQL**: v14+ (for database)
- **Redis**: v7+ (for caching)
- **Git**: For version control

### Accounts & Services
- **MQTT Server**: Optional (for real-time device data)
- **Email Service**: For sending verification emails (configure in `.env`)

---

## 🚀 Quick Start (5 minutes)

### 1. Clone & Setup
```bash
cd /home/akash/Desktop/SOlar_Sharing

# Install backend dependencies
cd backend
npm install

# Install frontend dependencies
cd ../frontend
npm install
```

### 2. Create Environment Files

#### Backend `.env` file
```bash
cd backend
cat > .env << 'EOF'
# Server
PORT=3000
NODE_ENV=development

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=solar_sharing
DB_USER=postgres
DB_PASSWORD=your_postgres_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# JWT
JWT_ACCESS_SECRET=your_secret_key_min_32_chars_long!
JWT_REFRESH_SECRET=your_refresh_secret_key_min_32_chars_long!
JWT_ACCESS_EXPIRES=24h
JWT_REFRESH_EXPIRES=30d

# CORS
CORS_ORIGIN=http://localhost:3001,http://localhost:19006,http://10.167.159.193:19006

# API
API_BASE_URL=http://10.167.159.193:3000

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password

# MQTT (Optional)
MQTT_BROKER=mqtt://localhost:1883
MQTT_USERNAME=mqtt_user
MQTT_PASSWORD=mqtt_password
EOF
```

#### Frontend `.env` file
```bash
cd frontend
cat > .env.local << 'EOF'
# API Configuration
REACT_APP_API_BASE_URL=http://10.167.159.193:3000
REACT_APP_API_TIMEOUT=30000
EOF
```

### 3. Setup Database

#### Option A: Using Docker (Easiest)
```bash
cd /home/akash/Desktop/SOlar_Sharing
docker-compose up -d postgres redis
```

#### Option B: Manual Installation

**PostgreSQL:**
```bash
# macOS
brew install postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Start service
sudo service postgresql start

# Create database and user
sudo -u postgres psql
```

```sql
CREATE DATABASE solar_sharing;
CREATE USER solar_user WITH PASSWORD 'solar_password';
ALTER ROLE solar_user SET client_encoding TO 'utf8';
ALTER ROLE solar_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE solar_user SET default_transaction_deferrable TO on;
ALTER ROLE solar_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE solar_sharing TO solar_user;
\q
```

**Redis:**
```bash
# macOS
brew install redis

# Ubuntu/Debian
sudo apt-get install redis-server

# Start service
sudo service redis-server start
```

### 4. Run the Application

#### Terminal 1: Backend Server
```bash
cd /home/akash/Desktop/SOlar_Sharing/backend
npm run dev
# Output: Server running on http://localhost:3000
```

#### Terminal 2: Frontend Web (Expo)
```bash
cd /home/akash/Desktop/SOlar_Sharing/frontend
npm start
# Press 'w' for web - opens http://localhost:19006
```

#### Terminal 3 (Optional): Frontend Mobile (Expo Go)
```bash
# Same terminal as web, just use different key
# Press 'i' for iOS or 'a' for Android
```

---

## 🧪 Test the App

### Login Credentials
```
Email: test@example.com
Password: Test123!@#
Role: host (can manage devices)
```

### Test Features
1. **Home Screen** - View dashboard
2. **Devices Tab** (hosts only) - Manage IoT devices
   - Add new device
   - View device list
   - Edit device details
   - Delete devices
3. **Energy Screen** - View energy data
4. **Wallet Screen** - View balance and transactions
5. **Profile Screen** - View/edit profile

---

## 📦 Project Structure

```
SOlar_Sharing/
├── backend/
│   ├── src/
│   │   ├── controllers/      # Route handlers
│   │   ├── routes/           # API routes
│   │   ├── services/         # Business logic
│   │   ├── database/         # DB setup & schema
│   │   ├── middleware/       # Auth, error handling
│   │   ├── utils/            # Helpers
│   │   └── server.js         # Entry point
│   ├── .env                  # Environment variables
│   └── package.json
│
└── frontend/
    ├── src/
    │   ├── screens/          # UI screens
    │   │   ├── main/         # HomeScreen, EnergyScreen, etc.
    │   │   ├── auth/         # LoginScreen, RegisterScreen, etc.
    │   │   └── host/         # AddDeviceScreen, DeviceDetailScreen
    │   ├── store/            # Zustand state management
    │   ├── navigation/       # React Navigation setup
    │   ├── api/              # Axios configuration
    │   ├── components/       # Reusable components
    │   ├── theme/            # Colors, typography, spacing
    │   └── App.tsx           # Entry point
    ├── .env.local            # Environment variables
    └── package.json
```

---

## 🔧 Available Commands

### Backend
```bash
cd backend

# Development (with hot reload)
npm run dev

# Production build
npm run build

# Start production
npm run start

# Run tests
npm test

# Lint code
npm run lint
```

### Frontend
```bash
cd frontend

# Start development server
npm start

# Build for web
npm run build

# Eject (not recommended)
npm run eject

# Run tests
npm test

# Lint code
npm run lint
```

---

## 📱 Device Management Features Implemented

### ✅ Completed
- **Backend APIs** (5 endpoints)
  - Register device
  - Get all devices
  - Get single device
  - Update device
  - Delete device

- **Frontend Screens** (3 screens)
  - DeviceManagementScreen (list view)
  - AddDeviceScreen (registration form)
  - DeviceDetailScreen (view/edit/delete)

- **State Management**
  - Zustand store with CRUD operations
  - Error handling
  - Loading states

- **Navigation**
  - Device stack navigator
  - Devices tab (hosts only)
  - Proper screen flow

### 🔄 Device Types Supported
1. **Solar Meter** - Solar panel output
2. **Consumption Meter** - Energy consumption
3. **Battery BMS** - Battery management system
4. **Weather Station** - Weather monitoring

---

## 🚨 Common Issues & Fixes

### Backend Won't Start
```bash
# Check if port 3000 is in use
lsof -i :3000
# Kill the process if needed
kill -9 <PID>

# Check database connection
psql -U postgres -d solar_sharing -c "SELECT 1"
```

### Frontend Shows "API Error"
```bash
# Verify backend is running
curl http://localhost:3000/api/v1/auth/health

# Check IP address in config.ts matches your machine
# Edit: frontend/src/api/config.ts
```

### Redis Connection Error
```bash
# Check if Redis is running
redis-cli ping
# Output should be: PONG

# If not running
redis-server
```

### Mobile App Can't Connect
```
Make sure you're using the correct IP:
- Current IP: 10.167.159.193
- Update in: frontend/src/api/config.ts
- Restart app after change
```

---

## 🔑 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Create account
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/logout` - Logout

### Device Management (NEW ✨)
- `POST /api/v1/iot/devices` - Register device
- `GET /api/v1/iot/devices` - Get user devices
- `GET /api/v1/iot/devices/:deviceId` - Get device details
- `PUT /api/v1/iot/devices/:deviceId` - Update device
- `DELETE /api/v1/iot/devices/:deviceId` - Delete device

### Energy Data
- `GET /api/v1/energy/readings` - Get energy readings
- `GET /api/v1/energy/summary` - Get energy summary

### Wallet
- `GET /api/v1/wallet/balance` - Get wallet balance
- `GET /api/v1/wallet/transactions` - Get transactions
- `POST /api/v1/wallet/topup` - Add funds

### User
- `GET /api/v1/user/profile` - Get user profile
- `PUT /api/v1/user/profile` - Update profile

---

## 📊 Database Schema

### Key Tables
- **users** - User accounts
- **devices** - IoT devices (NEW ✨)
- **energy_readings** - Energy data (TimescaleDB hypertable)
- **wallets** - User wallets
- **transactions** - Financial transactions
- **hosts** - Host profiles
- **buyers** - Buyer profiles
- **investors** - Investor profiles

---

## 🧪 Testing Device Management

### Curl Commands
```bash
# Register Device
curl -X POST http://localhost:3000/api/v1/iot/devices \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "deviceType": "solar_meter",
    "deviceModel": "SMA SunnyBoy",
    "firmwareVersion": "v2.1.0"
  }'

# Get All Devices
curl http://localhost:3000/api/v1/iot/devices \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get Device Details
curl http://localhost:3000/api/v1/iot/devices/{deviceId} \
  -H "Authorization: Bearer YOUR_TOKEN"

# Update Device
curl -X PUT http://localhost:3000/api/v1/iot/devices/{deviceId} \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "deviceModel": "SMA SunnyBoy Pro",
    "firmwareVersion": "v2.2.0"
  }'

# Delete Device
curl -X DELETE http://localhost:3000/api/v1/iot/devices/{deviceId} \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📚 Next Steps

1. **Test Device Management** - Add and manage devices through the app
2. **Energy Marketplace** - Buy/sell energy (coming next)
3. **Real-time Updates** - MQTT integration for live data
4. **Mobile App** - Deploy to iOS/Android
5. **Production Deployment** - Deploy to cloud

---

## 🆘 Need Help?

- Check logs: `tail -f backend/logs/*.log`
- API docs: [API_DOCUMENTATION.md](./backend/API_DOCUMENTATION.md)
- Troubleshooting: [DEPLOYMENT.md](./backend/DEPLOYMENT.md)

---

**Status:** ✅ Device Management Complete | 🔄 Energy Marketplace Next
