# 🚀 Railway Deployment Guide - Banking Platform

## Quick Start (3 minutes)

Your banking platform is **fully automated** and ready for deployment!

### ✅ What's Configured
- ✅ Procfile - Entry point for Railway
- ✅ runtime.txt - Python 3.11.7
- ✅ wsgi.py - Production WSGI app
- ✅ requirements.txt - All dependencies + gunicorn
- ✅ GitHub repo - Synced and pushed

---

## 🎯 Deploy Now (Choose One Method)

### **METHOD 1: Railway Dashboard (Easiest - 2 mins)**

1. **Visit Railway.app**
   ```
   https://railway.app
   ```

2. **Sign Up / Log In**
   - Click "Start New Project"
   - Select "Deploy from GitHub"
   - Authorize Railway with your GitHub account

3. **Select Your Repo**
   - Search for: `Avonce901/bank-platform`
   - Click "Deploy"

4. **Wait for Build**
   - Railway automatically detects `Procfile`
   - Build takes ~2-3 minutes
   - Check logs in dashboard

5. **Get Your URL**
   - Once deployed, Railway shows your URL
   - Example: `https://bank-platform-xxxxx.railway.app`

6. **Test Your API**
   ```bash
   curl https://your-url/health
   # Expected: {"status": "healthy"}
   ```

---

### **METHOD 2: Railway CLI (Advanced - 5 mins)**

**Step 1: Install Railway CLI**
```bash
npm install -g @railway/cli
```

**Step 2: Run Deployment Script**
```bash
cd C:\Users\antho\bank_platform
./deploy.bat
```

Or manually:
```bash
railway login
railway project create bank-platform
railway link Avonce901/bank-platform
railway up
```

**Step 3: Get URL**
```bash
railway env
```

---

## 📊 What Gets Deployed

| Component | Details |
|-----------|---------|
| **API** | Flask 2.3.2 with 30+ endpoints |
| **Database** | SQLite (included) or PostgreSQL |
| **Authentication** | JWT tokens with role-based access |
| **Features** | PDF extraction, Excel generation, banking workflows |
| **Admin** | Streamlit dashboard (optional) |
| **Port** | Auto-assigned by Railway ($PORT) |

---

## 🔧 Environment Variables (Optional)

Railway auto-configures from your code, but you can override:

```env
FLASK_ENV=production
DEBUG=False
API_HOST=0.0.0.0
API_PORT=$PORT
DATABASE_URL=sqlite:///bank_platform.db
SECRET_KEY=your-secret-key
```

**To Add in Railway Dashboard:**
1. Go to Project Settings
2. Click "Variables"
3. Add key-value pairs
4. Redeploy

---

## 🧪 Test Your Deployed API

### Health Check
```bash
curl https://your-app.railway.app/health
```
Expected:
```json
{"status": "healthy"}
```

### Login
```bash
curl -X POST https://your-app.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "anthony_doe",
    "password": "SecurePassword123!"
  }'
```

### Get Accounts
```bash
curl https://your-app.railway.app/api/v1/banking/accounts \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📝 Deployment Status

| Step | Status |
|------|--------|
| Procfile | ✅ Created |
| runtime.txt | ✅ Created |
| wsgi.py | ✅ Created |
| requirements.txt | ✅ Updated with gunicorn |
| GitHub | ✅ Pushed |
| Railway Ready | ✅ YES |

---

## 🚨 Troubleshooting

### Build Failed
**Solution:** Check Railway logs
```
railway logs --follow
```

### Port/Host Issues
**Solution:** Railway auto-detects `$PORT` env var (already in Procfile)

### Database Connection
**Solution:** SQLite is included by default. For PostgreSQL:
1. Add PostgreSQL plugin in Railway
2. Set DATABASE_URL env var

### Cold Start Issues
**Solution:** Railway provides 2 free hours/month. After that:
- Upgrade plan or
- Redeploy to restart

---

## 🎉 After Deployment

### Next Steps:
1. ✅ Test all endpoints (see above)
2. ✅ Add sample data
3. ✅ Build frontend dashboard
4. ✅ Share your API URL
5. ✅ Monitor logs and performance

### Access Logs:
```bash
railway logs --follow
```

### View Metrics:
- Railway Dashboard > Project > Monitoring

### Redeploy:
Just push to main branch:
```bash
git push origin main
```
Railway auto-redeploys on every push!

---

## 📚 Resources

- **Railway Docs:** https://docs.railway.app
- **Gunicorn Docs:** https://gunicorn.org
- **Flask Docs:** https://flask.palletsprojects.com
- **Your API Docs:** See `API_DOCUMENTATION.md`

---

## 💡 Tips

✓ **Auto-Redeploy:** Every git push automatically redeploys  
✓ **Free Tier:** $5/month free credits  
✓ **Custom Domain:** Add in Railway settings  
✓ **SSL/TLS:** Automatic with Railway  
✓ **Monitoring:** Built-in logs and metrics  

---

**Ready to deploy?** Start with METHOD 1 (Dashboard)!

**Questions?** Check the troubleshooting section or Railway docs.

🚀 **Your banking platform is production-ready!**
