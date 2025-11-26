#!/bin/bash
#  Railway Deployment Automation Script
# Deploys bank-platform to Railway from copilot/devfixdeploy branch

set -e

echo " Railway Deployment Automation"
echo "================================"

# Check for Railway CLI
if ! command -v railway &> /dev/null; then
    echo " Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Check GitHub authentication
echo " Checking GitHub authentication..."
gh auth status > /dev/null || {
    echo "❌ Not authenticated with GitHub. Run: gh auth login"
    exit 1
}

# Verify branch is synced
echo " Verifying branch is synced..."
git fetch origin
BRANCH="copilot/devfixdeploy"
LOCAL=$(git rev-parse $BRANCH)
REMOTE=$(git rev-parse origin/$BRANCH)

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "  Branch not synced. Pushing..."
    git push origin $BRANCH
fi

echo " Branch is synced: $LOCAL"

# Check if Railway project exists
echo " Checking Railway project..."
railway status > /dev/null 2>&1 || {
    echo " No Railway project linked. Configure manually at https://railway.app/dashboard"
    echo "   Then run: railway link"
    exit 1
}

# Deploy from GitHub
echo " Deploying to Railway from $BRANCH..."
railway up \
    --service banking \
    --branch $BRANCH \
    --from Avonce901/bank-platform

echo ""
echo " Deployment initiated. Watching logs..."
sleep 5

# Show deployment logs
railway logs --tail 100

echo ""
echo " Deployment started!"
echo ""
echo " Next steps:"
echo "  1. Visit https://railway.app/dashboard"
echo "  2. Go to Variables tab"
echo "  3. Add production Stripe keys:"
echo "     - STRIPE_PUBLIC_KEY = pk_live_..."
echo "     - STRIPE_SECRET_KEY = sk_live_..."
echo "     - STRIPE_WEBHOOK_SECRET = whsec_live_..."
echo "  4. Railway auto-redeploys (2-3 min)"
echo ""
echo " Done!"
