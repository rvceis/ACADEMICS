# Build Android APK - Step by Step

## Current Status ✅
- All frontend packages installed ✅
- EAS CLI installed ✅
- Backend connected: `https://sol-bridge.onrender.com` ✅
- APK configuration ready ✅

## What You Need to Do

### Step 1: Create Expo Account (if you don't have one)
Go to https://expo.dev and create a free account. Remember your email/username and password.

### Step 2: Login to Expo
Run this command in your terminal:

```bash
cd /home/akash/Desktop/SOlar_Sharing/frontend
eas login
```

Then enter:
- **Email/Username**: Your Expo account email or username
- **Password**: Your Expo password

### Step 3: Build the APK
After login, run:

```bash
npm run build:android:preview
```

This will:
1. Upload your code to Expo servers
2. Build APK in the cloud (takes 10-15 minutes)
3. Show you a download link when complete

### Step 4: Download & Install on Android Phone
1. Click the download link from the build output
2. Transfer APK to your Android phone
3. Open the APK file and tap "Install"
4. If prompted, enable "Install from unknown sources"
5. Open and test the app

---

## Alternative: Local Build (Without Cloud)

If you want to build locally without Expo cloud:

### Prerequisites:
- Android Studio installed
- Android SDK configured
- Java Development Kit (JDK) installed

### Command:
```bash
cd /home/akash/Desktop/SOlar_Sharing/frontend
npm run build:android:local
```

This builds APK directly on your computer (takes longer but no Expo account needed).

---

## Files Ready to Build

Your APK configuration is complete:

| File | Purpose |
|------|---------|
| `app.json` | App metadata (name, package, permissions) |
| `eas.json` | EAS Build profiles |
| `package.json` | Build scripts |
| `frontend/src/api/config.ts` | Backend URL: `https://sol-bridge.onrender.com` |
| `.env.production` | Production environment variables |

---

## Troubleshooting

### "eas: command not found"
```bash
sudo npm install -g eas-cli
```

### "Not logged in"
```bash
eas login
```

### Build failed?
Check the build logs at https://expo.dev/projects/your-project

### Backend URL wrong?
Edit: `frontend/src/api/config.ts`
- Development: `https://sol-bridge.onrender.com` ✅ (Already set)
- Production: Update if you deploy to different server

---

## Need Help?

- Expo Documentation: https://docs.expo.dev/
- EAS Build Guide: https://docs.expo.dev/build/setup/
- Mobile App Testing: https://docs.expo.dev/build/internal-distribution/

**Next Step:** Run `eas login` to get started! 🚀
