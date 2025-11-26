# 🚀 Railway Deployment Guide - Django Banking Platform

## Overview
Your banking platform with Stripe integration is ready for production deployment on Railway.

### What's Ready
- ✅ Django 4.2.7 REST API with Stripe payment processing
- ✅ Accounts, transfers, virtual cards, transactions
- ✅ SQLite (dev) / PostgreSQL (production) compatible
- ✅ Gunicorn WSGI configured
- ✅ requirements.txt with all dependencies
- ✅ Environment-based settings (DEBUG, ALLOWED_HOSTS, etc.)

---

## Step 1: Prepare for Deployment

### 1a. Update railway.json (DONE)
Already configured with:
```json
{
  "build": "./django-banking-app",
  "start": "gunicorn -w 4 -b 0.0.0.0:$PORT banking.wsgi:application"
}
```

### 1b. Verify .env.example (DONE)
Contains all required env vars (keys NOT included):
- DJANGO_SECRET_KEY
- STRIPE_PUBLIC_KEY, STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
- ALLOWED_HOSTS
- DEBUG=False

---

## Step 2: Deploy to Railway

### Option A: Railway Dashboard (Easiest)

1. **Go to [Railway.app](https://railway.app)**
2. **Sign in / Create account**
3. **Click "New Project" → "Deploy from GitHub"**
4. **Select**: `Avonce901/bank-platform`
5. **Choose branch**: `copilot/devfixdeploy` or `main`
6. **Railway auto-detects** `railway.json` and `Procfile`
7. **Build starts automatically** (~3-5 mins)

### Option B: Railway CLI

```bash
npm install -g @railway/cli
railway login
railway link  # Select your project
railway up    # Deploys current branch
```

---

## Step 3: Configure Environment Variables

### In Railway Dashboard:

1. Go to your project → **Variables** tab
2. **Add these (never paste secrets in code)**:

```
DEBUG=False
DJANGO_SECRET_KEY=your-50-char-random-secret-key
ALLOWED_HOSTS=bank-platform-xxxx.up.railway.app,yourdomain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

STRIPE_PUBLIC_KEY=pk_live_your_public_key
STRIPE_SECRET_KEY=sk_live_your_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

CORS_ALLOWED_ORIGINS=https://bank-platform-xxxx.up.railway.app
```

**Where to get Stripe keys**:
1. Login to [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. Copy `Publishable key` → `STRIPE_PUBLIC_KEY`
3. Copy `Secret key` → `STRIPE_SECRET_KEY`
4. Go to Webhooks → Create endpoint → Copy `Signing secret` → `STRIPE_WEBHOOK_SECRET`

---

## Step 4: Run Initial Migration

After deployment starts, run migrations:

### Option A: Railway CLI
```bash
railway run python django-banking-app/manage.py migrate
```

### Option B: Add to Procfile
Add this line to trigger on each deploy:
```
release: cd django-banking-app && python manage.py migrate
```

---

## Step 5: Create Admin User (Optional)

```bash
railway run python django-banking-app/manage.py createsuperuser
# Enter username, email, password
# Access admin at: https://your-domain/admin
```

---

## Step 6: Test Live Endpoints

Once deployed, test your API:

```bash
DOMAIN="bank-platform-xxxx.up.railway.app"

# Health check
curl https://$DOMAIN/health

# List accounts (requires auth token)
curl -H "Authorization: Token your-token" \
  https://$DOMAIN/api/accounts/

# Create payment intent
curl -X POST https://$DOMAIN/api/payments/create_payment_intent/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "50.00",
    "description": "Test deposit"
  }'
```

---

## Step 7: Configure Stripe Webhooks

For payment processing to work end-to-end:

1. **Stripe Dashboard** → **Webhooks**
2. **Add Endpoint**:
   - URL: `https://your-domain/api/webhooks/stripe/`
   - Events: `payment_intent.succeeded`, `charge.refunded`, `payment_method.attached`
3. **Copy Signing Secret** → Set as `STRIPE_WEBHOOK_SECRET` in Railway

---

## Step 8: Enable GitHub Auto-Deploy (Optional)

1. In Railway, go to **Project Settings** → **GitHub**
2. Enable **"Auto-deploy on push"**
3. Every push to your branch auto-deploys

---

## Production Security Checklist

- [ ] DEBUG=False
- [ ] DJANGO_SECRET_KEY generated and set
- [ ] SECURE_SSL_REDIRECT=True
- [ ] CSRF_COOKIE_SECURE=True
- [ ] SESSION_COOKIE_SECURE=True
- [ ] ALLOWED_HOSTS configured correctly
- [ ] Stripe keys are **live** (not test)
- [ ] CORS restricted to your domain only
- [ ] Database backed up (if using PostgreSQL)

---

## Troubleshooting

### Build Fails
- Check logs: `railway logs`
- Ensure `django-banking-app/` has `requirements.txt` and `banking/wsgi.py`

### Import Errors
- Verify `DJANGO_SETTINGS_MODULE=banking.settings` is set
- Check all Stripe keys are valid

### Static Files 404
- Add to Procfile: `collectstatic: python django-banking-app/manage.py collectstatic --noinput`

### Database Errors
- First deploy: migrations run automatically via release command
- Check Railway logs for errors

---

## Support

- **Django Docs**: https://docs.djangoproject.com/
- **Stripe API**: https://stripe.com/docs/api
- **Railway Docs**: https://docs.railway.app/
- **GitHub Issues**: Create issue in your repo

---

## Next Steps (After Deployment)

1. ✅ **Test all endpoints** with real Stripe keys
2. ✅ **Configure DNS** to point your domain
3. ✅ **Set up monitoring** (Sentry, DataDog, etc.)
4. ✅ **Enable backups** for production database
5. ✅ **Add rate limiting** for public endpoints
6. ✅ **Document API** for frontend team

Deployment is **ready**. Your banking platform is production-grade! 🎉
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
