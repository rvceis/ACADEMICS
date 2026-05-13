# 🚀 Quick Start Guide - Solar Sharing Platform

## Complete Setup in 5 Minutes

### Prerequisites
```bash
✓ Node.js 18+ installed
✓ PostgreSQL 16+ running
✓ Expo CLI installed (npm install -g expo-cli)
```

---

## Backend Setup

### 1. Install Dependencies
```bash
cd backend
npm install
```

### 2. Configure Environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
DB_HOST=localhost
DB_PORT=5432
DB_NAME=solar_sharing
DB_USER=postgres
DB_PASSWORD=your_password
JWT_SECRET=your-super-secret-key-change-this-in-production
JWT_REFRESH_SECRET=another-secret-for-refresh-tokens
```

### 3. Create Database
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE solar_sharing;
\q
```

### 4. Run Migrations
```bash
npm run setup-db
```

This creates all tables with indexes and constraints.

### 5. Seed Test Data
```bash
node seed-location-data.js
```

Creates 40 users, 30 listings, devices across Bangalore.

### 6. Start Backend
```bash
npm run dev
```

Backend running at: http://localhost:3000

---

## Frontend Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Configure API URL
```bash
# Edit frontend/src/api/config.ts
# Update LOCAL_IP with your computer's IP address

const LOCAL_IP = '192.168.1.100';  # Your IP here
```

Find your IP:
```bash
# Mac/Linux
ifconfig | grep "inet "

# Windows
ipconfig
```

### 3. Start Frontend
```bash
npm start
```

### 4. Open in Expo
- Scan QR code with Expo Go app (iOS/Android)
- Press `a` for Android emulator
- Press `i` for iOS simulator
- Press `w` for web browser

---

## Test the App

### 1. Login
```
Email: buyer1@solar.test
Password: Test@123456
```

Or register a new account.

### 2. Test Nearby Users
1. Navigate to "Nearby" tab
2. Enable location permission
3. See users within radius
4. Filter by type (host, investor, buyer)
5. Adjust radius slider

### 3. Test Marketplace
1. Navigate to "Marketplace" tab
2. Browse active listings
3. Tap a listing to see details
4. Click "Buy Energy" to purchase
5. View "My Transactions"

### 4. Test Device Management
1. Go to "Marketplace" → "Devices"
2. Add a new device
3. Edit device details
4. Delete a device

### 5. Test Smart Allocation
1. Go to "Nearby" → "Smart Allocation"
2. Enter energy needed (e.g., 50 kWh)
3. Set preferences (distance, price)
4. View AI-ranked sellers with scores
5. Buy in bulk

---

## Quick API Tests (cURL)

### Register
```bash
curl -X POST http://localhost:3000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "test@example.com",
    "password": "Test@123456",
    "fullName": "Test User",
    "phone": "+919876543210",
    "role": "buyer",
    "profile": {
      "address": "Koramangala",
      "city": "Bangalore",
      "state": "Karnataka",
      "pincode": "560001"
    }
  }'
```

### Login
```bash
curl -X POST http://localhost:3000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "buyer1@solar.test",
    "password": "Test@123456"
  }'
```

Save the `accessToken` from response.

### Get Nearby Users
```bash
curl "http://localhost:3000/api/v1/location/nearby-users?latitude=12.9352&longitude=77.6245&radius=10&types=host"
```

### Browse Listings
```bash
curl "http://localhost:3000/api/v1/marketplace/listings?status=active"
```

### Update Location (Auth Required)
```bash
TOKEN="your_access_token_here"

curl -X PUT http://localhost:3000/api/v1/location/update \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "latitude": 12.9352,
    "longitude": 77.6245
  }'
```

---

## Troubleshooting

### Backend won't start
```bash
# Check PostgreSQL is running
pg_isready

# Check port 3000 is free
lsof -i :3000
# If occupied: kill -9 <PID>

# Check .env file exists
cat backend/.env

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### Frontend connection issues
```bash
# Verify backend URL in config.ts matches your IP
# Ensure both devices on same WiFi network
# Check firewall isn't blocking port 3000

# Test backend reachable
curl http://YOUR_IP:3000/api/v1/health
```

### Database errors
```bash
# Reset database
npm run setup-db

# Re-seed data
node seed-location-data.js

# Check connection
psql -U postgres -d solar_sharing -c "SELECT COUNT(*) FROM users;"
```

### Location not working
```bash
# Android: Enable location in device settings
# iOS: Allow location permission when prompted
# Web: Browser will ask for location permission

# Test with hardcoded coordinates first
```

### No nearby results
```bash
# Increase radius to 50km
# Verify test data was seeded
# Check coordinates are in Bangalore area (12-13°N, 77-78°E)
```

---

## Project Structure

```
solar-sharing/
├── backend/
│   ├── src/
│   │   ├── controllers/     # Request handlers
│   │   ├── services/        # Business logic
│   │   ├── routes/          # API routes
│   │   ├── middleware/      # Auth, validation, etc.
│   │   ├── database/        # DB connection, schema
│   │   └── utils/           # Helpers, logger
│   ├── seed-location-data.js
│   ├── .env
│   └── server.js
│
└── frontend/
    ├── src/
    │   ├── screens/         # UI screens
    │   ├── navigation/      # App navigation
    │   ├── store/           # State management (Zustand)
    │   ├── api/             # API client
    │   ├── components/      # Reusable components
    │   └── theme/           # Colors, typography
    ├── App.tsx
    └── app.json
```

---

## Key Features Implemented

✅ **Authentication**
- JWT-based login/register
- Automatic token refresh
- Secure password hashing (bcrypt)
- Role-based access (host, buyer, investor)

✅ **Location Features**
- GPS-based user location
- Find nearby users within radius
- Distance calculations (km)
- Location-based listing search
- Energy heatmap visualization

✅ **Marketplace**
- Browse active energy listings
- Create/edit/delete listings
- Purchase energy with validation
- Transaction history
- Rating system

✅ **AI/ML Optimization**
- Optimal seller allocation (multi-factor scoring)
- Dynamic pricing recommendations
- Investment opportunity ranking
- Demand prediction (7-day forecast)

✅ **Device Management**
- Add/edit/delete devices
- Device location tracking
- Multiple device types supported

✅ **Database**
- PostgreSQL with indexes
- ACID transactions for purchases
- Spatial queries optimized
- Foreign key constraints

---

## Next Steps

1. **Add Real Payments**: Integrate Razorpay/Stripe
2. **Real-time Updates**: WebSocket for live listing changes
3. **Push Notifications**: Alert buyers of new nearby listings
4. **IoT Integration**: Connect actual solar meters
5. **Admin Dashboard**: Monitor platform metrics
6. **ML Model Training**: Improve price/demand predictions
7. **KYC Verification**: Implement document upload/verification
8. **Chat/Messaging**: Enable buyer-seller communication

---

## Useful Commands

```bash
# Backend
npm run dev          # Start development server
npm run setup-db     # Create database schema
npm test            # Run tests
node seed-location-data.js  # Seed test data

# Frontend
npm start           # Start Expo
npm run android     # Open Android
npm run ios         # Open iOS
npm run web         # Open web browser
```

---

## Documentation

- [Architecture Overview](./ARCHITECTURE.md)
- [API Testing Guide](./LOCATION_MARKETPLACE_TESTING.md)
- [Complete API Docs](./API_DOCUMENTATION.md)
- [Database Schema](./src/database/schema.js)

---

## Support

- Backend logs: Check terminal running `npm run dev`
- Frontend logs: Check Expo console and device logs
- Database queries: Enable query logging in `.env` with `DEBUG=true`

---

**You're all set! 🎉**

Test login: `buyer1@solar.test` / `Test@123456`
