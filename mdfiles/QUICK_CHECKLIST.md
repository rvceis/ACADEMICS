# 🚀 Quick Setup Checklist

## Pre-requisites ✅
- [ ] Node.js v18+ installed (`node --version`)
- [ ] npm v9+ installed (`npm --version`)
- [ ] PostgreSQL v14+ installed and running
- [ ] Redis v7+ installed and running
- [ ] Git installed

## Backend Setup
- [ ] `cd backend && npm install`
- [ ] Create `.env` file with database credentials
- [ ] Verify PostgreSQL database created
- [ ] Verify Redis is running
- [ ] `npm run dev` - Backend should start on port 3000

## Frontend Setup
- [ ] `cd frontend && npm install`
- [ ] Create `.env.local` with API URL
- [ ] Update IP address in `src/api/config.ts` if needed (currently: 10.167.159.193)

## Running the Application

### Terminal 1 (Backend)
```bash
cd /home/akash/Desktop/SOlar_Sharing/backend
npm run dev
```
✅ Should see: "Server running on http://localhost:3000"

### Terminal 2 (Frontend Web)
```bash
cd /home/akash/Desktop/SOlar_Sharing/frontend
npm start
# Press 'w' for web
```
✅ Should open http://localhost:19006

### Terminal 3 (Frontend Mobile - Optional)
```bash
# Same as Terminal 2, press 'a' for Android or 'i' for iOS
```

## Test Login
- **Email:** test@example.com
- **Password:** Test123!@#

## ✨ What's Included

### Backend
- ✅ Authentication (register, login, JWT)
- ✅ Device Management (register, list, view, update, delete)
- ✅ Energy tracking
- ✅ Wallet system
- ✅ User profiles
- ✅ Role-based access (host, buyer, investor)

### Frontend
- ✅ Authentication screens
- ✅ Device Management (NEW!)
  - List devices
  - Add device
  - Edit device
  - Delete device
- ✅ Energy dashboard
- ✅ Wallet
- ✅ Profile
- ✅ Bottom tab navigation

## 🎯 Next Features to Implement
1. Energy Marketplace (buy/sell energy)
2. Real-time device data (MQTT)
3. Push notifications
4. Advanced analytics
5. Mobile app deployment

## 🔗 Useful Links
- Backend API Docs: `backend/API_DOCUMENTATION.md`
- Setup Guide: `SETUP_GUIDE.md`
- API Testing: `backend/API_TESTING_GUIDE.md`

---

**Everything is ready to run! Start with the Backend first, then Frontend.**
