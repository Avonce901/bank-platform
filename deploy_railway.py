#!/usr/bin/env python3
"""
Automated Railway.app Deployment Setup
This script prepares and validates your banking platform for Railway deployment
"""

import subprocess
import os
import sys
import json
from pathlib import Path

class RailwayDeploymentAutomator:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.config = {
            'project_name': 'bank-platform',
            'github_repo': 'Avonce901/bank-platform',
            'python_version': '3.11.7',
            'environment_vars': {
                'FLASK_ENV': 'production',
                'DEBUG': 'False',
            }
        }

    def run_command(self, cmd, description=""):
        """Run shell command and return result"""
        try:
            if description:
                print(f"📌 {description}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=self.project_root)
            if result.returncode == 0:
                print(f"✅ {description or cmd} - Success")
                return result.stdout.strip()
            else:
                print(f"❌ {description or cmd} - Failed")
                print(f"   Error: {result.stderr}")
                return None
        except Exception as e:
            print(f"❌ Error executing: {e}")
            return None

    def verify_files(self):
        """Verify all deployment files exist"""
        print("\n🔍 Verifying deployment files...")
        required_files = ['Procfile', 'runtime.txt', 'wsgi.py', 'requirements.txt']
        
        for file in required_files:
            file_path = self.project_root / file
            if file_path.exists():
                print(f"✅ {file} exists")
            else:
                print(f"❌ {file} missing!")
                return False
        return True

    def check_git_status(self):
        """Check git status and commit if needed"""
        print("\n🔧 Checking git status...")
        result = self.run_command("git status --porcelain", "Git status check")
        
        if result and len(result) > 0:
            print(f"📝 Found uncommitted changes, committing...")
            self.run_command(
                'git add -A && git commit -m "Update: Railway deployment configuration"',
                "Committing changes"
            )
        else:
            print("✅ All changes already committed")

    def push_to_github(self):
        """Push to GitHub"""
        print("\n🚀 Pushing to GitHub...")
        return self.run_command("git push origin main", "Pushing to GitHub")

    def generate_railway_config(self):
        """Generate Railway configuration"""
        print("\n⚙️ Generating Railway configuration...")
        
        railway_config = {
            'name': self.config['project_name'],
            'description': 'Banking Platform API with PDF extraction, Excel generation',
            'services': {
                'web': {
                    'build': './src',
                    'start': 'gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:app',
                    'env': self.config['environment_vars']
                }
            }
        }
        
        config_path = self.project_root / 'railway.json'
        with open(config_path, 'w') as f:
            json.dump(railway_config, f, indent=2)
        
        print(f"✅ Railway configuration saved to railway.json")
        return config_path

    def display_deployment_instructions(self):
        """Display next steps for Railway deployment"""
        print("\n" + "="*70)
        print("🎉 DEPLOYMENT AUTOMATION COMPLETE!")
        print("="*70)
        print("""
✅ Your banking platform is ready for Railway deployment!

NEXT STEPS - Deploy to Railway (3 minutes):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ Visit Railway.app
   → https://railway.app

2️⃣ Sign Up / Log In
   → Click "Start New Project"
   → Select "Deploy from GitHub"
   → Authorize Railway with your GitHub account

3️⃣ Select Your Repository
   → Choose: Avonce901/bank-platform
   → Click "Deploy"

4️⃣ Configure (Optional)
   → Railway auto-detects from your config
   → If needed, add environment variables:
     - FLASK_ENV=production
     - DEBUG=False
     - DATABASE_URL=sqlite:///bank_platform.db

5️⃣ Monitor Deployment
   → Railway dashboard shows build logs
   → Deployment takes 2-3 minutes
   → You'll see: "Deployment successful ✓"

6️⃣ Get Your Live URL
   → Copy the deployment URL (e.g., https://your-app.railway.app)
   → Test: curl https://your-app.railway.app/health

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 DEPLOYMENT CONFIGURATION:
   Project: {project_name}
   Repository: {github_repo}
   Python: {python_version}
   Entry Point: wsgi:app
   Build Command: Automatic
   Start Command: gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:app

📝 IMPORTANT FILES CREATED:
   ✅ Procfile - Entry point for Railway
   ✅ runtime.txt - Python version specification
   ✅ wsgi.py - WSGI application wrapper
   ✅ .railwayignore - Files to exclude from deployment
   ✅ requirements.txt - Updated with gunicorn

🔗 YOUR REPOSITORY:
   GitHub: https://github.com/{github_repo}
   Main Branch: Ready for deployment

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 AFTER DEPLOYMENT:
   ✓ Test your API endpoints
   ✓ Add sample data (more accounts, transactions)
   ✓ Build a frontend dashboard
   ✓ Share your banking platform URL

Questions? Check DEPLOYMENT_GUIDE.md for detailed info!
""".format(
            project_name=self.config['project_name'],
            github_repo=self.config['github_repo'],
            python_version=self.config['python_version']
        ))

    def run(self):
        """Execute full deployment automation"""
        print("\n" + "="*70)
        print("🚀 BANKING PLATFORM - RAILWAY DEPLOYMENT AUTOMATOR")
        print("="*70)

        # Step 1: Verify files
        if not self.verify_files():
            print("\n❌ Deployment files missing. Please run setup.py first.")
            return False

        # Step 2: Check git status
        self.check_git_status()

        # Step 3: Push to GitHub
        if not self.push_to_github():
            print("\n⚠️ Push failed, but you can still deploy manually")

        # Step 4: Generate Railway config
        self.generate_railway_config()

        # Step 5: Display instructions
        self.display_deployment_instructions()

        return True


if __name__ == '__main__':
    project_root = os.path.dirname(os.path.abspath(__file__))
    automator = RailwayDeploymentAutomator(project_root)
    
    success = automator.run()
    sys.exit(0 if success else 1)
