"""
API Routes Definition
"""
from flask import Blueprint, jsonify, request, send_file
from src.modules.pdf_extractor import extract_pdf as extract_pdf_module
from src.modules.excel_generator import generate_excel as generate_excel_module
from src.modules.takeoff_calculator import calculate_takeoff as calculate_takeoff_module

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

@api_bp.route('/status', methods=['GET'])
def get_status():
    """Get API status"""
    return jsonify({'status': 'running'}), 200

@api_bp.route('/extract-pdf', methods=['POST'])
def extract_pdf():
    """Extract data from PDF
    
    Expects: multipart/form-data with 'file' field containing PDF
    Returns: JSON with extracted text, tables, and metadata
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        pdf_file = request.files['file']
        
        if pdf_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not pdf_file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'File must be a PDF'}), 400
        
        # Extract data
        result = extract_pdf_module(pdf_file)
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({
            'error': f'PDF extraction failed: {str(e)}',
            'extraction_status': 'failed'
        }), 500

@api_bp.route('/generate-excel', methods=['POST'])
def generate_excel():
    """Generate Excel file
    
    Expects: JSON with 'data' (list of dicts) and optional 'title' and 'report_type'
    Returns: Excel file or JSON
    """
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        data = request_data.get('data', [])
        title = request_data.get('title', 'Report')
        report_type = request_data.get('report_type', 'simple')
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if report_type == 'financial':
            # Financial report expects accounts and transactions
            accounts = request_data.get('accounts', [])
            transactions = request_data.get('transactions', [])
            excel_file = generate_excel_module.generate_financial_report(accounts, transactions)
        else:
            # Simple report
            excel_file = generate_excel_module(data, title)
        
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'{title.replace(" ", "_")}.xlsx'
        )
    except Exception as e:
        return jsonify({
            'error': f'Excel generation failed: {str(e)}',
            'generation_status': 'failed'
        }), 500

@api_bp.route('/calculate-takeoff', methods=['POST'])
def calculate_takeoff():
    """Calculate project takeoff
    
    Expects: JSON with project_name, description, markup_percentage, tax_rate, and line_items
    Example:
    {
        "project_name": "Building Construction",
        "description": "Commercial building takeoff",
        "markup_percentage": 15,
        "tax_rate": 0.08,
        "line_items": [
            {
                "description": "Concrete Foundation",
                "quantity": 100,
                "unit": "cy",
                "unit_price": 150.00
            }
        ]
    }
    Returns: JSON with takeoff calculation
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        if 'project_name' not in data:
            return jsonify({'error': 'project_name is required'}), 400
        
        if 'line_items' not in data or not isinstance(data['line_items'], list):
            return jsonify({'error': 'line_items must be a list'}), 400
        
        # Calculate takeoff
        result = calculate_takeoff_module(data)
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({
            'error': f'Takeoff calculation failed: {str(e)}',
            'calculation_status': 'failed'
        }), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'bank-platform-api',
        'version': '1.0.0'
    }), 200

def register_routes(app):
    """Register all API blueprints"""
    app.register_blueprint(api_bp)
