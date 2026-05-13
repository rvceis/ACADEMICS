# 🚀 Quick Start - Android/Expo Setup

## Prerequisites
- Node.js installed
- Expo Go app installed on Android phone
- Backend `.env` configured

## Option 1: Automatic Setup (Recommended)

```bash
# From project root
cd /home/akash/Desktop/SOlar_Sharing
chmod +x start.sh
./start.sh
```

This will:
1. Kill any stuck processes
2. Start backend server
3. Clear Expo cache
4. Start Expo dev server
5. Show QR code to scan

---

## Option 2: Manual Setup

### Terminal 1 - Backend
```bash
cd /home/akash/Desktop/SOlar_Sharing/backend
npm start
```

Wait for: `Server running on port 5000`

### Terminal 2 - Frontend
```bash
cd /home/akash/Desktop/SOlar_Sharing/frontend

# Clear cache first time
rm -rf .expo node_modules/.cache

# Start Expo
npx expo start --clear
```

### Connect Android
1. Open Expo Go app on Android phone
2. Scan the QR code shown in terminal
3. App will load on your device

---

## Option 3: Android Emulator

After starting frontend, press **`a`** in the Expo terminal:
```
› Press a │ open Android
```

---

## Troubleshooting

### App not loading after scan
**Solution:** Clear cache and restart
```bash
cd frontend
rm -rf .expo node_modules/.cache
npx expo start --clear
```

### Port already in use
**Solution:** Kill stuck processes
```bash
pkill -f "expo" || true
pkill -f "npm" || true
sleep 2
npx expo start --clear
```

### Metro bundler takes too long
**Solution:** It's rebuilding cache (normal first time)
- Wait 1-2 minutes
- Check console for errors
- Reload app (press `r`)

### White screen / Module not found
**Symptoms:** 
- App starts but shows white screen
- Console shows "Cannot find module"

**Solution:**
```bash
# Full clean
rm -rf node_modules .expo
npm install
npx expo start --clear
```

### API calls failing
**Solution:** Ensure backend is running
```bash
# Check backend
curl http://localhost:5000/health || curl http://localhost:5000/api/v1/health
```

---

## Development Tips

### Hot Reload
- Press `r` in Expo terminal to reload app
- Changes auto-sync to device

### Debugging
- Press `j` in Expo terminal to open debugger
- Or use Chrome DevTools at `http://localhost:19002`

### Logs
- Real-time logs appear in Expo terminal
- Filter by: `Press e to show errors`

### Switch Devices
```
› Press a │ open Android emulator
› Press i │ open iOS simulator  
› Press w │ open web
```

---

## File Locations

- Backend: `/home/akash/Desktop/SOlar_Sharing/backend`
- Frontend: `/home/akash/Desktop/SOlar_Sharing/frontend`
- Start script: `/home/akash/Desktop/SOlar_Sharing/start.sh`

---

## Commands Reference

| Command | Effect |
|---------|--------|
| `r` | Reload app |
| `a` | Open Android emulator |
| `w` | Open web browser |
| `i` | Open iOS simulator |
| `j` | Open debugger |
| `m` | Show more options |
| `?` | Show all commands |
| `q` | Quit |

---

## Common Issues & Fixes

### Issue: "Port 8081 already in use"
```bash
pkill -f "expo" && sleep 2
npx expo start --clear
```

### Issue: "Cannot find module" errors
```bash
cd frontend
npm install  # reinstall deps
rm -rf .expo node_modules/.cache
npx expo start --clear
```

### Issue: App crashes on load
```bash
# Check console for specific error
# Likely: missing import or API endpoint
# Fix: Check Recent changes and revert if needed
git status
```

### Issue: Android phone doesn't connect
```bash
# Ensure phone and computer on same WiFi
# Restart Expo server
pkill -f "expo"
npx expo start --clear

# Try again from Expo Go app
```

---

## Next Steps

1. ✅ Backend running on port 5000
2. ✅ Frontend serving on port 8081
3. ✅ Android connected via Expo Go
4. 🎯 Start developing!

---

**Created:** January 16, 2026
**Status:** Production Ready

