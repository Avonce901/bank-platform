#  Railway Deployment - Quick Start

##  One-Click Deploy (Fastest)

### Step 1: Link Repository to Railway
```bash
# Visit: https://railway.app/dashboard
# Click "Create New Project" → "Deploy from GitHub"
# Select: Avonce901/bank-platform
# Branch: copilot/devfixdeploy
```

### Step 2: Add Environment Variables
Once project is created in Railway dashboard:

1. Go to **Variables** tab
2. Add these variables:

```
DEBUG = False
DJANGO_SECRET_KEY = django-insecure-your-secret-key-here
ALLOWED_HOSTS = *.railway.app
STRIPE_PUBLIC_KEY = pk_live_[your-live-public-key]
STRIPE_SECRET_KEY = sk_live_[your-live-secret-key]
STRIPE_WEBHOOK_SECRET = whsec_live_[your-webhook-secret]
```

3. **Save** - Railway auto-deploys (2-3 minutes)

---

##  Automated Deployment (Local)

### Using Python Script (Recommended)
```bash
# Verify everything is ready
python railway-deploy.py
```

Output shows:
-  Prerequisites verified
-  GitHub auth confirmed
-  Branch synced to remote
-  Deployment instructions

### Using Bash Script
```bash
# Requires railway CLI installed
./railway-deploy.sh
```

---

##  GitHub Actions Auto-Deploy

Once configured, every push to `copilot/devfixdeploy` triggers:

1.  Code pushed to GitHub
2.  GitHub Actions workflow runs
3.  Railway detects new commits
4.  Auto-redeploy begins
5.  ~5 minutes to production

### To Enable Auto-Deploy:
1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `RAILWAY_TOKEN`
4. Value: Get from https://railway.app/dashboard → Account → Tokens
5. Save

---

##  What Gets Deployed

| Component | Status |
|-----------|--------|
| Django REST API |  Ready |
| PostgreSQL Database |  Railway provides |
| Stripe Integration |  Ready |
| Migrations |  Auto-run |
| Static Files |  Configured |
| Gunicorn WSGI |  Ready |
| Environment Config | Railway managed |

---

##  Verify Deployment

### After Railway deployment completes:

```bash
# Test API health
curl https://your-app.railway.app/api/accounts/

# Check migrations
railway run python django-banking-app/manage.py migrate --list

# Run verification script
python verify_production_deployment.py
```

---

##  Security Checklist

-  Never commit `.env` file (only `.env.example`)
-  Use `DEBUG = False` in production
-  Django secret key is random/secure
-  ALLOWED_HOSTS configured for your domain
-  HTTPS enforced by Railway
-  Database backups: Railway auto-backup

---

##  Troubleshooting

### Deployment stuck?
```bash
# View live logs
railway logs --tail 100
```

### Wrong branch deployed?
```bash
# Verify branch
git branch -a
git checkout copilot/devfixdeploy
git push origin copilot/devfixdeploy
```

### Environment variables not loading?
1. Go to Railway dashboard
2. Variables tab
3. Verify all keys are set
4. Click redeploy button

### Stripe integration not working?
1. Verify keys in Railway Variables
2. Check webhook secret matches
3. Visit https://dashboard.stripe.com/webhooks to verify endpoint

---

##  Deployment Timeline

##  Deployment Timeline


| Step | Time | Status |
|------|------|--------|
| Push code to GitHub | 1 min |  Done |
| Railway detects changes | 1 min | Automatic |
| Pull & build Docker image | 2 min | Auto-build |
| Run migrations | 1 min | Auto-run |
| Health checks | 1 min | Auto-verify |
| **Total** | **~5 min** | **Live!** |

---##  Next Steps

1.  All code automated and pushed
2.  Go to https://railway.app/dashboard
3.  Link your GitHub repository
4.  Add Stripe live API keys
5.  Deploy!

**That's it! Your banking platform will be live in ~5 minutes** 

---

Generated: November 26, 2025
Repository: Avonce901/bank-platform
Branch: copilot/devfixdeploy
