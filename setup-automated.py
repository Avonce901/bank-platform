#!/usr/bin/env python3
"""
🚀 Bank Platform - Complete Automated Setup
Handles: environment setup, dependencies, database, test data, and deployment
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Tuple, Optional

# ANSI Colors
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

class BankPlatformSetup:
    """Automated setup orchestrator"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.django_dir = self.root_dir / 'django-banking-app'
        self.venv_dir = self.root_dir / '.venv'
        self.python_exe = self.venv_dir / 'bin' / 'python'
        self.pip_exe = self.venv_dir / 'bin' / 'pip'
        self.manage_py = self.django_dir / 'manage.py'
        
    def print_banner(self):
        """Display setup banner"""
        print(f"\n{BLUE}{'='*70}")
        print("🚀 BANK PLATFORM - AUTOMATED SETUP")
        print("="*70 + f"{RESET}\n")
    
    def print_section(self, title: str):
        """Print section header"""
        print(f"\n{YELLOW}{'─'*70}")
        print(f"📋 {title}")
        print(f"{'─'*70}{RESET}\n")
    
    def run_cmd(self, cmd: list, desc: str = "", cwd: Optional[Path] = None) -> Tuple[int, str, str]:
        """Run command and return exit code, stdout, stderr"""
        if desc:
            print(f"  ⏳ {desc}...")
        
        result = subprocess.run(
            cmd,
            cwd=cwd or self.root_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            if desc:
                print(f"  ✅ {desc}")
        else:
            if desc:
                print(f"  ❌ {desc}")
            print(f"     Error: {result.stderr[:200]}")
        
        return result.returncode, result.stdout, result.stderr
    
    def check_python(self) -> bool:
        """Check if Python 3.8+ is available"""
        self.print_section("Checking Python Installation")
        
        code, stdout, _ = self.run_cmd(['python3', '--version'], "Checking Python version")
        if code == 0:
            print(f"  ℹ️  {stdout.strip()}")
            return True
        return False
    
    def setup_virtualenv(self) -> bool:
        """Create or activate virtual environment"""
        self.print_section("Setting Up Virtual Environment")
        
        if self.venv_dir.exists():
            print(f"  ℹ️  Virtual environment already exists")
            return True
        
        print(f"  ⏳ Creating virtual environment...")
        code, _, _ = self.run_cmd(['python3', '-m', 'venv', str(self.venv_dir)])
        if code == 0:
            print(f"  ✅ Virtual environment created")
            return True
        else:
            print(f"  ❌ Failed to create virtual environment")
            return False
    
    def install_dependencies(self) -> bool:
        """Install Python dependencies"""
        self.print_section("Installing Dependencies")
        
        req_file = self.root_dir / 'requirements.txt'
        if not req_file.exists():
            print(f"  ⚠️  requirements.txt not found")
            return False
        
        print(f"  ⏳ Upgrading pip...")
        self.run_cmd([str(self.pip_exe), 'install', '--upgrade', 'pip'], "")
        
        print(f"  ⏳ Installing packages from requirements.txt...")
        code, _, stderr = self.run_cmd([str(self.pip_exe), 'install', '-r', str(req_file)])
        if code == 0:
            print(f"  ✅ All dependencies installed")
            return True
        else:
            print(f"  ❌ Failed to install dependencies")
            return False
    
    def create_env_file(self) -> bool:
        """Create .env file from template"""
        self.print_section("Configuring Environment Variables")
        
        env_template = self.root_dir / '.env.example'
        env_file = self.root_dir / '.env'
        
        if env_file.exists():
            print(f"  ℹ️  .env already exists")
            return True
        
        if not env_template.exists():
            print(f"  ⚠️  .env.example not found")
            return False
        
        print(f"  ⏳ Creating .env from template...")
        with open(env_template) as f:
            content = f.read()
        
        # Replace placeholder values for local development
        content = content.replace('your-secret-key-here', 'dev-secret-key-12345')
        content = content.replace('localhost:8000', 'localhost:8000')
        content = content.replace('DEBUG=', 'DEBUG=True  # Set to False for production')
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print(f"  ✅ .env file created")
        return True
    
    def run_migrations(self) -> bool:
        """Run Django migrations"""
        self.print_section("Running Database Migrations")
        
        print(f"  ⏳ Running makemigrations...")
        code, _, _ = self.run_cmd(
            [str(self.python_exe), str(self.manage_py), 'makemigrations'],
            "",
            cwd=self.django_dir
        )
        
        if code != 0:
            print(f"  ⚠️  makemigrations had issues (may be normal)")
        
        print(f"  ⏳ Running migrate...")
        code, _, _ = self.run_cmd(
            [str(self.python_exe), str(self.manage_py), 'migrate'],
            "",
            cwd=self.django_dir
        )
        
        if code == 0:
            print(f"  ✅ Database migrations completed")
            return True
        else:
            print(f"  ❌ Migration failed")
            return False
    
    def create_test_data(self) -> bool:
        """Create test users and accounts"""
        self.print_section("Creating Test Data")
        
        script = f"""
import os
from django import setup
setup()

from django.contrib.auth import get_user_model
from accounts.models import Account
from rest_framework.authtoken.models import Token
from decimal import Decimal

User = get_user_model()

# Create test users
users_data = [
    ('sender_test', 'sender@test.com', '5000.00'),
    ('receiver_test', 'receiver@test.com', '100.00'),
]

for username, email, balance in users_data:
    user, created = User.objects.get_or_create(username=username, defaults={{'email': email}})
    if created:
        user.set_password('password123')
        user.save()
        print(f'  ✅ Created user: {{username}}')
    
    account, created = Account.objects.get_or_create(user=user, defaults={{
        'account_number': f'{{username.upper()}}_{{user.id}}',
        'name': f'{{username.replace("_", " ").title()}} Account'
    }})
    
    if created or account.balance == 0:
        account.balance = Decimal(balance)
        account.is_active = True
        account.save()
        print(f'  ✅ Created account: {{account.account_number}} (Balance: ${{balance}})')
    
    token, created = Token.objects.get_or_create(user=user)
    if created:
        print(f'  🔑 Token for {{username}}: {{token.key}}')

print('\\n✅ Test data setup complete!')
"""
        
        env = os.environ.copy()
        env['DJANGO_SETTINGS_MODULE'] = 'banking.settings'
        
        result = subprocess.run(
            [str(self.python_exe), '-c', script],
            cwd=self.django_dir,
            capture_output=True,
            text=True,
            env=env
        )
        
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"  ⚠️  Could not create test data")
            print(f"     {result.stderr[:200]}")
            return False
    
    def verify_setup(self) -> bool:
        """Verify everything is set up"""
        self.print_section("Verifying Setup")
        
        checks = [
            (self.venv_dir.exists(), "Virtual environment exists"),
            (self.python_exe.exists(), "Python executable found"),
            (self.manage_py.exists(), "Django manage.py found"),
            ((self.root_dir / '.env').exists(), ".env file created"),
            ((self.django_dir / 'db.sqlite3').exists(), "Database created"),
        ]
        
        all_good = True
        for check, desc in checks:
            status = "✅" if check else "❌"
            print(f"  {status} {desc}")
            if not check:
                all_good = False
        
        return all_good
    
    def show_next_steps(self):
        """Display next steps"""
        self.print_section("Next Steps")
        
        print(f"{GREEN}1️⃣  Start Development Server{RESET}")
        print(f"    cd django-banking-app")
        print(f"    python manage.py runserver\n")
        
        print(f"{GREEN}2️⃣  Test API Endpoints{RESET}")
        print(f"    curl -H 'Authorization: Token sender_test_token' \\")
        print(f"         http://localhost:8000/api/accounts/\n")
        
        print(f"{GREEN}3️⃣  Deploy to Railway{RESET}")
        print(f"    Visit: https://railway.app/dashboard")
        print(f"    Deploy from: Avonce901/bank-platform (copilot/devfixdeploy branch)\n")
        
        print(f"{GREEN}4️⃣  Configure Stripe Keys{RESET}")
        print(f"    Add to Railway Variables:")
        print(f"    - STRIPE_PUBLIC_KEY = pk_live_...")
        print(f"    - STRIPE_SECRET_KEY = sk_live_...\n")
        
        print(f"{GREEN}5️⃣  Make Real-Time Payments{RESET}")
        print(f"    POST /api/payments/create_payment_intent/")
        print(f"    POST /api/payments/confirm_payment/\n")
    
    def run_full_setup(self) -> bool:
        """Run complete setup"""
        self.print_banner()
        
        steps = [
            ("Checking Python", self.check_python),
            ("Setting up virtual environment", self.setup_virtualenv),
            ("Installing dependencies", self.install_dependencies),
            ("Creating environment file", self.create_env_file),
            ("Running migrations", self.run_migrations),
            ("Creating test data", self.create_test_data),
            ("Verifying setup", self.verify_setup),
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                print(f"\n{RED}❌ Setup failed at: {step_name}{RESET}")
                return False
        
        self.show_next_steps()
        
        print(f"\n{BLUE}{'='*70}")
        print(f"✅ SETUP COMPLETE - Your bank platform is ready! 🎉")
        print(f"{'='*70}{RESET}\n")
        
        return True

def main():
    """Main entry point"""
    setup = BankPlatformSetup()
    success = setup.run_full_setup()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
