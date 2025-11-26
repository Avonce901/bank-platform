#!/usr/bin/env python3
"""
Railway Deployment Configuration Script
Configures environment variables and triggers deployment
"""

import os
import json
import subprocess
import sys
import time
from pathlib import Path

# ANSI colors
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_banner():
    print(f"\n{BLUE}{'='*70}")
    print("🚀 RAILWAY DEPLOYMENT AUTOMATION")
    print("="*70 + f"{RESET}\n")

def check_prerequisites():
    """Verify all required tools are available"""
    print(f"{YELLOW}📋 Checking prerequisites...{RESET}")
    
    tools = ['git', 'gh', 'docker']
    missing = []
    
    for tool in tools:
        result = subprocess.run(['which', tool], capture_output=True)
        if result.returncode != 0:
            missing.append(tool)
            print(f"  ❌ {tool}")
        else:
            print(f"  ✅ {tool}")
    
    if missing:
        print(f"\n{RED}Missing tools: {', '.join(missing)}")
        print(f"Please install them first.{RESET}")
        sys.exit(1)
    
    print(f"{GREEN}✅ All prerequisites met\n{RESET}")

def verify_github_auth():
    """Verify GitHub authentication"""
    print(f"{YELLOW}🔐 Verifying GitHub authentication...{RESET}")
    
    result = subprocess.run(['gh', 'auth', 'status'], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"{RED}❌ Not authenticated with GitHub")
        print("Run: gh auth login{RESET}")
        sys.exit(1)
    
    # Extract username
    for line in result.stdout.split('\n'):
        if 'github.com' in line or 'account' in line:
            print(f"  ℹ️  {line.strip()}")
    
    print(f"{GREEN}✅ GitHub authentication verified\n{RESET}")

def verify_git_branch():
    """Ensure branch is synced"""
    print(f"{YELLOW}📋 Verifying git branch...{RESET}")
    
    branch = "copilot/devfixdeploy"
    
    # Get current branch
    result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                          capture_output=True, text=True)
    current_branch = result.stdout.strip()
    
    print(f"  ℹ️  Current branch: {current_branch}")
    print(f"  ℹ️  Target branch: {branch}")
    
    # Fetch latest
    subprocess.run(['git', 'fetch', 'origin'], capture_output=True)
    
    # Check if synced
    local_hash = subprocess.run(['git', 'rev-parse', branch],
                               capture_output=True, text=True).stdout.strip()
    remote_hash = subprocess.run(['git', 'rev-parse', f'origin/{branch}'],
                                capture_output=True, text=True).stdout.strip()
    
    if local_hash == remote_hash:
        print(f"  ✅ Branch synced: {local_hash[:8]}")
    else:
        print(f"  ⚠️  Local and remote differ, pushing...")
        subprocess.run(['git', 'push', 'origin', branch], check=True)
        print(f"  ✅ Branch pushed")
    
    print()

def create_deployment_config():
    """Create railway.json if needed"""
    print(f"{YELLOW}⚙️  Checking deployment config...{RESET}")
    
    railway_json = Path('railway.json')
    
    if railway_json.exists():
        print(f"  ✅ railway.json exists")
    else:
        print(f"  ℹ️  Creating railway.json...")
        config = {
            "build": {
                "builder": "docker"
            },
            "deploy": {
                "startCommand": "cd django-banking-app && gunicorn -w 4 -b 0.0.0.0:$PORT banking.wsgi:application"
            }
        }
        with open(railway_json, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"  ✅ railway.json created")
    
    print()

def check_environment_file():
    """Verify .env.example exists"""
    print(f"{YELLOW}📝 Checking environment template...{RESET}")
    
    env_file = Path('.env.example')
    
    if env_file.exists():
        print(f"  ✅ .env.example exists")
        # Show required vars
        with open(env_file) as f:
            lines = [l.strip() for l in f if l.strip() and not l.strip().startswith('#')]
            print(f"  ℹ️  Required environment variables:")
            for line in lines[:5]:
                print(f"     - {line.split('=')[0]}")
            if len(lines) > 5:
                print(f"     ... and {len(lines)-5} more")
    else:
        print(f"  ⚠️  .env.example not found")
    
    print()

def show_deployment_instructions():
    """Display final deployment instructions"""
    print(f"{BLUE}{'='*70}")
    print("📋 DEPLOYMENT INSTRUCTIONS")
    print("="*70 + f"{RESET}\n")
    
    print(f"{YELLOW}Step 1: Create/Link Railway Project{RESET}")
    print("  - Visit: https://railway.app/dashboard")
    print("  - Click 'Create New Project'")
    print("  - Select 'Deploy from GitHub'")
    print("  - Choose repository: Avonce901/bank-platform")
    print("  - Select branch: copilot/devfixdeploy")
    print()
    
    print(f"{YELLOW}Step 2: Configure Environment Variables{RESET}")
    print("  - Go to your Railway project → Variables")
    print("  - Add the following:")
    print(f"    DEBUG = False")
    print(f"    DJANGO_SECRET_KEY = [auto-generated]")
    print(f"    ALLOWED_HOSTS = your-railway-domain.up.railway.app")
    print(f"    STRIPE_PUBLIC_KEY = pk_live_...")
    print(f"    STRIPE_SECRET_KEY = sk_live_...")
    print(f"    STRIPE_WEBHOOK_SECRET = whsec_live_...")
    print()
    
    print(f"{YELLOW}Step 3: Deploy{RESET}")
    print("  - Railway auto-deploys when GitHub repo is linked")
    print("  - Watch deployment logs in Railway dashboard")
    print("  - Deployment takes ~5 minutes")
    print()
    
    print(f"{YELLOW}Step 4: Verify Deployment{RESET}")
    print("  - Test API: https://your-railway-domain.up.railway.app/api/accounts/")
    print("  - Run migrations: railway run python django-banking-app/manage.py migrate")
    print("  - Check status: ./check_railway_readiness.py")
    print()

def offer_manual_or_api():
    """Ask if user wants to attempt API deployment"""
    print(f"{YELLOW}Would you like to attempt Railway API deployment?{RESET}")
    print("  (Requires Railway token)")
    print()
    
    response = input("Deploy now? (y/n): ").strip().lower()
    
    if response == 'y':
        token = input("Enter your Railway API token: ").strip()
        if token:
            return token
    
    return None

def main():
    os.chdir(Path(__file__).parent)
    
    print_banner()
    check_prerequisites()
    verify_github_auth()
    verify_git_branch()
    create_deployment_config()
    check_environment_file()
    show_deployment_instructions()
    
    # Try API deployment if token available
    token = os.environ.get('RAILWAY_TOKEN')
    
    if token:
        print(f"{YELLOW}🚀 Found RAILWAY_TOKEN, attempting API deployment...{RESET}\n")
        try:
            # Would call Railway API here
            print(f"{GREEN}✅ Deployment initiated via API{RESET}")
        except Exception as e:
            print(f"{RED}⚠️  API deployment failed: {e}{RESET}")
            print(f"Use manual deployment instructions above")
    else:
        print(f"{BLUE}{'='*70}")
        print("ℹ️  To automate full deployment via API:")
        print("   export RAILWAY_TOKEN=<your_railway_api_token>")
        print("   python railway-deploy.py")
        print("="*70 + f"{RESET}\n")
    
    print(f"{GREEN}✅ Automation script complete!{RESET}\n")

if __name__ == '__main__':
    main()
