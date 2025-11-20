# Bank Platform - API Documentation

## Overview

The Bank Platform API provides three core modules for banking operations:
- **PDF Extractor** - Extract data from PDF documents
- **Excel Generator** - Generate Excel reports
- **Takeoff Calculator** - Calculate project costs and estimates

## Base URL

```
http://localhost:5000/api/v1
```

## Authentication

Currently, no authentication is required. Add JWT authentication in production.

---

## Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Check if the API is running

**Response:**
```json
{
  "status": "healthy",
  "service": "bank-platform-api",
  "version": "1.0.0"
}
```

**Status Code:** `200 OK`

---

### 2. API Status

**Endpoint:** `GET /status`

**Description:** Get API status

**Response:**
```json
{
  "status": "running"
}
```

**Status Code:** `200 OK`

---

### 3. Extract PDF

**Endpoint:** `POST /extract-pdf`

**Description:** Extract text, tables, and metadata from a PDF file

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: Form data with `file` field containing PDF

**Example cURL:**
```bash
curl -X POST -F "file=@document.pdf" http://localhost:5000/api/v1/extract-pdf
```

**Response (Success):**
```json
{
  "success": true,
  "text": "Extracted text from PDF...",
  "tables": [
    {
      "page": 1,
      "table_index": 1,
      "data": [
        {"Column1": "Value1", "Column2": "Value2"},
        {"Column1": "Value3", "Column2": "Value4"}
      ]
    }
  ],
  "metadata": {
    "total_pages": 5,
    "metadata": {
      "Producer": "PDF producer info"
    }
  },
  "extraction_status": "completed"
}
```

**Status Code:** `200 OK`

**Response (Error):**
```json
{
  "error": "No file provided"
}
```

**Status Code:** `400 Bad Request` or `500 Internal Server Error`

---

### 4. Generate Excel

**Endpoint:** `POST /generate-excel`

**Description:** Generate an Excel file from data

**Request:**
- Method: `POST`
- Content-Type: `application/json`

**Simple Report:**
```json
{
  "data": [
    {"Name": "John Doe", "Amount": 5000, "Status": "Active"},
    {"Name": "Jane Smith", "Amount": 7500, "Status": "Active"},
    {"Name": "Bob Johnson", "Amount": 3200, "Status": "Pending"}
  ],
  "title": "Account Report"
}
```

**Financial Report:**
```json
{
  "report_type": "financial",
  "accounts": [
    {"name": "Account 1", "balance": 50000},
    {"name": "Account 2", "balance": 75000}
  ],
  "transactions": [
    {"from": "Account 1", "to": "Account 2", "amount": 1000, "date": "2025-01-15"},
    {"from": "Account 2", "to": "Account 1", "amount": 500, "date": "2025-01-16"}
  ]
}
```

**Example cURL:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d @data.json \
  http://localhost:5000/api/v1/generate-excel
```

**Response:**
- Returns Excel file (.xlsx) as binary attachment
- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

**Status Code:** `200 OK`

**Response (Error):**
```json
{
  "error": "Excel generation failed: No data provided",
  "generation_status": "failed"
}
```

**Status Code:** `400 Bad Request` or `500 Internal Server Error`

---

### 5. Calculate Takeoff

**Endpoint:** `POST /calculate-takeoff`

**Description:** Calculate project cost estimates with markups and taxes

**Request:**
- Method: `POST`
- Content-Type: `application/json`

**Example Request:**
```json
{
  "project_name": "Downtown Building Construction",
  "description": "Commercial 10-story office building",
  "markup_percentage": 15,
  "tax_rate": 0.08,
  "line_items": [
    {
      "description": "Concrete Foundation",
      "quantity": 150,
      "unit": "cy",
      "unit_price": 150.00
    },
    {
      "description": "Steel Framing",
      "quantity": 75,
      "unit": "ton",
      "unit_price": 2000.00
    },
    {
      "description": "Electrical Wiring",
      "quantity": 2500,
      "unit": "ft",
      "unit_price": 35.00
    },
    {
      "description": "HVAC System",
      "quantity": 1,
      "unit": "unit",
      "unit_price": 125000.00
    }
  ]
}
```

**Response (Success):**
```json
{
  "success": true,
  "takeoff_id": "takeoff_1",
  "project_name": "Downtown Building Construction",
  "description": "Commercial 10-story office building",
  "line_items": [
    {
      "description": "Concrete Foundation",
      "quantity": 150,
      "unit": "cy",
      "unit_price": "$150.00",
      "total": "$22,500.00"
    },
    {
      "description": "Steel Framing",
      "quantity": 75,
      "unit": "ton",
      "unit_price": "$2,000.00",
      "total": "$150,000.00"
    },
    {
      "description": "Electrical Wiring",
      "quantity": 2500,
      "unit": "ft",
      "unit_price": "$35.00",
      "total": "$87,500.00"
    },
    {
      "description": "HVAC System",
      "quantity": 1,
      "unit": "unit",
      "unit_price": "$125,000.00",
      "total": "$125,000.00"
    }
  ],
  "subtotal": "$385,000.00",
  "markup_percentage": 15,
  "markup_amount": "$57,750.00",
  "subtotal_with_markup": "$442,750.00",
  "tax_rate": "8.0%",
  "tax_amount": "$35,420.00",
  "total_price": "$478,170.00",
  "item_count": 4
}
```

**Status Code:** `200 OK`

**Response (Error):**
```json
{
  "error": "project_name is required",
  "calculation_status": "failed"
}
```

**Status Code:** `400 Bad Request` or `500 Internal Server Error`

---

## Units for Takeoff

Supported units for line items:
- `ft` - Linear Feet
- `sf` - Square Feet
- `cy` - Cubic Yards
- `ton` - Tons
- `unit` - Individual Units
- `gal` - Gallons

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Description of what went wrong",
  "status_code": 400
}
```

**Common Status Codes:**
- `200 OK` - Request successful
- `400 Bad Request` - Invalid input or missing required fields
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server-side error

---

## Example Usage

### Python with Requests

```python
import requests
import json

# Test Health Check
response = requests.get('http://localhost:5000/api/v1/health')
print(response.json())

# Test Takeoff Calculation
data = {
    "project_name": "Sample Project",
    "description": "Test project",
    "markup_percentage": 10,
    "tax_rate": 0.08,
    "line_items": [
        {
            "description": "Labor",
            "quantity": 100,
            "unit": "ft",
            "unit_price": 50.00
        }
    ]
}

response = requests.post(
    'http://localhost:5000/api/v1/calculate-takeoff',
    json=data
)
print(response.json())

# Test Excel Generation
data = {
    "data": [
        {"Name": "John", "Amount": 1000},
        {"Name": "Jane", "Amount": 2000}
    ],
    "title": "Report"
}

response = requests.post(
    'http://localhost:5000/api/v1/generate-excel',
    json=data
)

# Save Excel file
with open('report.xlsx', 'wb') as f:
    f.write(response.content)
```

### JavaScript/Node.js with Fetch

```javascript
// Health Check
fetch('http://localhost:5000/api/v1/health')
  .then(r => r.json())
  .then(d => console.log(d));

// Takeoff Calculation
const takeoffData = {
  project_name: "Sample Project",
  description: "Test project",
  markup_percentage: 10,
  tax_rate: 0.08,
  line_items: [
    {
      description: "Labor",
      quantity: 100,
      unit: "ft",
      unit_price: 50.00
    }
  ]
};

fetch('http://localhost:5000/api/v1/calculate-takeoff', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify(takeoffData)
})
  .then(r => r.json())
  .then(d => console.log(d));
```

---

## Running the API

### Local Development

```bash
cd bank_platform
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
python src/api/main.py
```

API will start at `http://localhost:5000`

### Docker

```bash
docker-compose up --build
```

API will be available inside the Docker network on port 5000.

---

## Module Details

### PDF Extractor

**Location:** `src/modules/pdf_extractor/__init__.py`

**Features:**
- Extract all text from PDF pages
- Extract tables with structure preservation
- Extract PDF metadata

**Classes:**
- `PDFExtractor` - Main extraction class
- `extract_pdf()` - Convenience function

### Excel Generator

**Location:** `src/modules/excel_generator/__init__.py`

**Features:**
- Create formatted Excel reports
- Generate financial reports with multiple sheets
- Auto-adjust column widths
- Apply professional styling

**Classes:**
- `ExcelGenerator` - Main generation class
- `generate_excel()` - Simple report generation
- `generate_financial_report()` - Financial report generation

### Takeoff Calculator

**Location:** `src/modules/takeoff_calculator/__init__.py`

**Features:**
- Create project takeoffs
- Add multiple line items
- Calculate subtotals, markups, and taxes
- Format currency output

**Classes:**
- `TakeoffCalculator` - Main calculation engine
- `Takeoff` - Takeoff data model
- `LineItem` - Individual line item
- `calculate_takeoff()` - Convenience function

---

## Testing

Run tests to verify all functionality:

```bash
pytest
pytest --cov=src  # With coverage
pytest tests/test_api.py  # API tests only
```

Or run the quick API test:
```bash
python test_api.py
```

---

## Version History

- **v1.0.0** (2025-01-19)
  - Initial API implementation
  - PDF extraction module
  - Excel generation module
  - Takeoff calculator module
  - All endpoints functional and tested

---

## Support & Troubleshooting

**API won't start:**
- Verify Python 3.10+ is installed
- Check all dependencies: `pip install -r requirements.txt`
- Ensure port 5000 is available

**PDF extraction fails:**
- Verify PDF is not corrupted
- Check file is readable and not password-protected
- Ensure pdfplumber is installed: `pip install pdfplumber`

**Excel generation issues:**
- Verify all data is serializable (no complex objects)
- Check openpyxl is installed: `pip install openpyxl`
- Ensure disk space available for file creation

For more help, check GitHub issues: https://github.com/Avonce901/bank-platform

