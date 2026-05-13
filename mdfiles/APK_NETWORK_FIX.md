# APK Network Error - Fix Instructions

## Problem
The Android APK cannot login and shows "network error" while local development works fine with the Render backend.

## Root Cause
React Native/Expo apps don't use `process.env` the same way web apps do. The APK was not properly configured to use the deployed backend URL.

## Changes Made

### 1. Updated API Configuration (`frontend/src/api/config.ts`)
✅ Changed to use Expo Constants instead of process.env
✅ Hardcoded backend URL: `https://sol-bridge.onrender.com`
✅ Added debug logging to show which URL is being used
✅ Fixed environment detection for React Native

### 2. Updated App Configuration (`frontend/app.json`)
✅ Added INTERNET permission for Android
✅ Added ACCESS_NETWORK_STATE permission
✅ Added backend URL to `extra` config for Expo Constants
✅ Set EXPO_PUBLIC_ENV=production

## Rebuild APK

You need to rebuild the APK for these changes to take effect:

```bash
cd /home/akash/Desktop/SOlar_Sharing/frontend

# Option 1: EAS Build (Cloud - Recommended)
npm run build:android:preview

# Option 2: Local build (if you have Android Studio)
npm run build:android:local
```

## Verification Steps

### After Rebuilding:

1. **Download & Install New APK**
   - Download from EAS build link
   - Install on your Android phone
   - Replace the old version

2. **Check Logs (in app)**
   - Open the app
   - Look for console logs showing:
     ```
     === API CONFIG DEBUG ===
     Environment: development
     Platform: android
     Backend Base URL: https://sol-bridge.onrender.com
     Backend ML URL: http://localhost:8001
     =======================
     ```

3. **Test Login**
   - Try logging in with your credentials
   - Should connect to: `https://sol-bridge.onrender.com/api/v1/auth/login`

4. **If Still Network Error:**
   - Check your Render backend is running: https://sol-bridge.onrender.com/health
   - Check phone has internet connection
   - Check backend logs on Render dashboard

## Testing Backend Connection

### From Your Phone Browser:
```
Visit: https://sol-bridge.onrender.com/health
```

Should show:
```json
{
  "status": "healthy",
  "database": "connected",
  ...
}
```

### From Terminal:
```bash
curl https://sol-bridge.onrender.com/health
```

## Troubleshooting

### Backend is Sleeping (Render Free Tier)
Render free tier spins down after 15 minutes of inactivity.

**Solution:**
1. Open backend URL in browser: https://sol-bridge.onrender.com/health
2. Wait 30-60 seconds for backend to wake up
3. Try logging in from app again

### Still Network Error After Rebuild

**Check 1: Backend URL in Code**
```bash
grep -r "sol-bridge" frontend/src/api/config.ts
# Should show: https://sol-bridge.onrender.com
```

**Check 2: App Has Internet Permission**
```bash
grep -A 10 "permissions" frontend/app.json
# Should include: "INTERNET"
```

**Check 3: Clear App Cache**
- Uninstall old APK completely
- Install new APK fresh
- Try login again

### Alternative: Use Local IP (For Testing Only)

If you want to test with local backend:

1. Find your computer's local IP:
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   # Example output: inet 192.168.1.100
   ```

2. Update config.ts:
   ```typescript
   development: {
     base: 'http://192.168.1.100:3000',  // Your local IP
     mlService: 'http://192.168.1.100:8001',
   },
   ```

3. Start local backend:
   ```bash
   cd backend && npm start
   ```

4. Rebuild APK

**Note:** This only works when phone and computer are on same WiFi network.

## Summary of Permissions Added

```json
"permissions": [
  "INTERNET",              // NEW - Required for network access
  "ACCESS_NETWORK_STATE",   // NEW - Check network status
  "ACCESS_FINE_LOCATION",   // Existing
  "CAMERA",                 // Existing
  "READ_EXTERNAL_STORAGE",  // Existing
  "WRITE_EXTERNAL_STORAGE"  // Existing
]
```

## Expected API Endpoints

When app makes requests, it will connect to:

- Login: `https://sol-bridge.onrender.com/api/v1/auth/login`
- Register: `https://sol-bridge.onrender.com/api/v1/auth/register`
- Profile: `https://sol-bridge.onrender.com/api/v1/users/profile`
- Devices: `https://sol-bridge.onrender.com/api/v1/iot/devices`

## Quick Commands

```bash
# Rebuild APK
cd frontend
npm run build:android:preview

# Check backend health
curl https://sol-bridge.onrender.com/health

# Check logs (during app usage)
# Use React Native Debugger or Expo DevTools

# Local backend (alternative)
cd backend
npm start
```

## Next Steps

1. **Rebuild APK** with fixed configuration
2. **Install new APK** on Android device
3. **Test login** - should work now!
4. If issues persist, check Render backend logs

---

**Fixed Issues:**
- ✅ Backend URL hardcoded for mobile
- ✅ INTERNET permission added
- ✅ Expo Constants integration
- ✅ Debug logging added
- ✅ Network state permission added

**Status:** Ready to rebuild APK
