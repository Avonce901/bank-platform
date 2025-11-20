#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Banking API Live
"""
import subprocess
import time
import os
import sys

def start_api():
    """Start the API server"""
    print("\n" + "="*70)
    print("STARTING BANK PLATFORM API")
    print("="*70 + "\n")
    
    os.chdir(r"C:\Users\antho\bank_platform")
    
    print("Starting Flask server on port 5000...")
    print("API will be available at: http://localhost:5000\n")
    
    try:
        subprocess.run([sys.executable, "src/api/main.py"], check=True)
    except KeyboardInterrupt:
        print("\n\nAPI stopped.")
    except Exception as e:
        print(f"Error starting API: {e}")

if __name__ == "__main__":
    start_api()
