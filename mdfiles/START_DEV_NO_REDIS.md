# 🚀 Quick Start - No Redis Required!

Backend now runs in dev mode **WITHOUT Redis**. Caching is automatically disabled.

## ✅ Requirements
- ✅ Node.js v16+ 
- ✅ PostgreSQL v12+
- ❌ Redis NOT needed

---

## 🔧 Step 1: Install Backend Dependencies

```bash
cd /home/akash/Desktop/SOlar_Sharing/backend
npm install
```

---

## 📦 Step 2: Ensure PostgreSQL is Running

```bash
# macOS
brew services start postgresql

# Ubuntu
sudo service postgresql start

# Windows
# Use PostgreSQL application installer
```

Verify:
```bash
psql -U postgres -c "SELECT 1"
```

---

## 🚀 Step 3: Start Backend (Dev Mode)

```bash
cd /home/akash/Desktop/SOlar_Sharing/backend
npm run dev
```

**Expected Output:**
```
✅ Server running on http://localhost:3000
✅ Database connected
⚠️  Redis error (caching disabled)
✅ API version: v1
```

**That's it!** The server will work without Redis. No caching, but everything else works perfectly.

---

## 🧪 Step 4: Test Backend is Running

In a new terminal:
```bash
curl http://localhost:3000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-05T10:30:00.000Z",
  "uptime": 2.345
}
```

---

## 📱 Step 5: Start Frontend (Optional)

In another terminal:
```bash
cd /home/akash/Desktop/SOlar_Sharing/frontend
npm install
npm start
# Press 'w' for web
```

**Expected:** Opens http://localhost:19006

---

## 🔍 What Changed?

| Feature | With Redis | Without Redis |
|---------|-----------|---------------|
| **Caching** | ✅ Enabled | ⚠️ Disabled |
| **Rate Limiting** | ✅ Enabled | ⚠️ Disabled |
| **Auth** | ✅ Works | ✅ Works |
| **API** | ✅ Works | ✅ Works |
| **Database** | ✅ Works | ✅ Works |

**All features work the same, just without caching/rate-limiting.**

---

## 🆘 Troubleshooting

### "Database connection failed"
```bash
# Make sure PostgreSQL is running
psql -U postgres -c "SELECT 1"

# Check .env file has correct DB_PASSWORD
cat backend/.env | grep DB_
```

### "Port 3000 already in use"
```bash
# Kill process using port 3000
lsof -i :3000
kill -9 <PID>
```

### "npm start hangs"
```bash
# Clear npm cache
npm cache clean --force

# Reinstall
rm -rf backend/node_modules
npm install
npm run dev
```

---

## ✨ You're Ready!

The server is now running **without any Redis dependency**. Perfect for development! 🎉

Want to add Redis later? Just:
1. Install Redis (`brew install redis`)
2. Start it (`redis-server`)
3. Restart backend - it will auto-detect and enable caching

