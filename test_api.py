#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify API implementation
"""
import sys
import json

# Test imports
try:
    from src.modules.pdf_extractor import PDFExtractor, extract_pdf
    print("[OK] PDF Extractor imported successfully")
except ImportError as e:
    print(f"[FAIL] PDF Extractor import failed: {e}")
    sys.exit(1)

try:
    from src.modules.excel_generator import ExcelGenerator, generate_excel
    print("[OK] Excel Generator imported successfully")
except ImportError as e:
    print(f"[FAIL] Excel Generator import failed: {e}")
    sys.exit(1)

try:
    from src.modules.takeoff_calculator import TakeoffCalculator, calculate_takeoff
    print("[OK] Takeoff Calculator imported successfully")
except ImportError as e:
    print(f"[FAIL] Takeoff Calculator import failed: {e}")
    sys.exit(1)

try:
    from src.api.routes import api_bp
    print("[OK] API Routes imported successfully")
except ImportError as e:
    print(f"[FAIL] API Routes import failed: {e}")
    sys.exit(1)

# Test Takeoff Calculator
print("\n=== Testing Takeoff Calculator ===")
test_data = {
    "project_name": "Sample Building",
    "description": "Commercial construction project",
    "markup_percentage": 15,
    "tax_rate": 0.08,
    "line_items": [
        {
            "description": "Concrete Foundation",
            "quantity": 100,
            "unit": "cy",
            "unit_price": 150.00
        },
        {
            "description": "Steel Framing",
            "quantity": 50,
            "unit": "ton",
            "unit_price": 2000.00
        },
        {
            "description": "Electrical Work",
            "quantity": 1000,
            "unit": "ft",
            "unit_price": 25.00
        }
    ]
}

result = calculate_takeoff(test_data)
if result.get('success'):
    print(f"[OK] Takeoff calculation successful")
    print(f"  Project: {result['project_name']}")
    print(f"  Items: {result['item_count']}")
    print(f"  Subtotal: {result['subtotal']}")
    print(f"  Total: {result['total_price']}")
else:
    print(f"[FAIL] Takeoff calculation failed: {result.get('error')}")

# Test Excel Generation
print("\n=== Testing Excel Generator ===")
test_excel_data = [
    {"Name": "John Doe", "Account": "ACC001", "Balance": "$50,000"},
    {"Name": "Jane Smith", "Account": "ACC002", "Balance": "$75,000"},
    {"Name": "Business Corp", "Account": "ACC003", "Balance": "$45,000"}
]

try:
    excel_file = generate_excel(test_excel_data, "Accounts Report")
    if excel_file:
        print(f"[OK] Excel file generated successfully ({excel_file.getbuffer().nbytes} bytes)")
    else:
        print("[FAIL] Excel generation returned None")
except Exception as e:
    print(f"[FAIL] Excel generation failed: {e}")

print("\n=== All Module Tests Complete ===")
print("\nAPI Endpoints available:")
print("  GET  /api/v1/status - API status")
print("  GET  /api/v1/health - Health check")
print("  POST /api/v1/extract-pdf - Extract data from PDF")
print("  POST /api/v1/generate-excel - Generate Excel file")
print("  POST /api/v1/calculate-takeoff - Calculate project takeoff")
