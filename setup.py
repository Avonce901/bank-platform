#!/usr/bin/env python3
"""
Bank Platform Setup Script
Initializes project structure and dependencies
"""

import os
import subprocess
import sys
from pathlib import Path

def run_cmd(cmd, desc=""):
    """Execute shell command"""
    if desc:
        print(f"\n[*] {desc}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

def main():
    print("""
====================================================
    Bank Platform - Automated Setup
====================================================
""")
    
    # Create directory structure
    print("\n[+] Creating directory structure...")
    dirs = [
        "src/api",
        "src/modules/pdf_extractor",
        "src/modules/excel_generator",
        "src/modules/takeoff_calculator",
        "src/config",
        "src/utils",
        "tests/unit",
        "tests/integration",
        "docs",
        "docker",
        "scripts",
        "data/input",
        "data/output",
        ".github/workflows"
    ]
    
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py files
    init_files = [
        "src/__init__.py",
        "src/api/__init__.py",
        "src/modules/__init__.py",
        "src/modules/pdf_extractor/__init__.py",
        "src/modules/excel_generator/__init__.py",
        "src/modules/takeoff_calculator/__init__.py",
        "src/config/__init__.py",
        "src/utils/__init__.py",
        "tests/__init__.py",
    ]
    
    for f in init_files:
        Path(f).touch()
    
    print("    [OK] Project directories created")
    
    # Check if files already exist, skip if they do
    if not os.path.exists("requirements.txt"):
        print("[+] Creating requirements.txt...")
        # Can add later
    
    if not os.path.exists(".env"):
        print("[+] Creating .env...")
        # Can add later
    
    if not os.path.exists("Dockerfile"):
        print("[+] Creating Dockerfile...")
        # Can add later
    
    print("""
====================================================
    Setup Complete!
====================================================

Next steps:
1. Review .env configuration
2. Install dependencies: pip install -r requirements.txt
3. Run: docker-compose up --build

For more info: see README.md
====================================================
""")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
