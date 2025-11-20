"""
Unit tests for Bank Platform API
"""

import pytest
import json
from src.api.main import create_app


@pytest.fixture
def client():
    """Create test client"""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check_returns_200(self, client):
        """Health check should return 200 status"""
        response = client.get('/health')
        assert response.status_code == 200
    
    def test_health_check_returns_healthy_status(self, client):
        """Health check should return healthy status"""
        response = client.get('/health')
        data = json.loads(response.data)
        assert data['status'] == 'healthy'


class TestAPIStatus:
    """Test API status endpoint"""
    
    def test_api_status_returns_200(self, client):
        """API status should return 200 status"""
        response = client.get('/api/v1/status')
        assert response.status_code == 200
    
    def test_api_status_returns_running(self, client):
        """API status should return running status"""
        response = client.get('/api/v1/status')
        data = json.loads(response.data)
        assert data['status'] == 'running'


class TestPDFExtraction:
    """Test PDF extraction endpoint"""
    
    def test_extract_pdf_endpoint_exists(self, client):
        """PDF extraction endpoint should be available"""
        response = client.post('/api/v1/extract-pdf')
        assert response.status_code in [200, 400, 422]
    
    def test_extract_pdf_returns_json(self, client):
        """PDF extraction should return JSON response"""
        response = client.post('/api/v1/extract-pdf')
        assert response.content_type == 'application/json'


class TestExcelGeneration:
    """Test Excel generation endpoint"""
    
    def test_generate_excel_endpoint_exists(self, client):
        """Excel generation endpoint should be available"""
        response = client.post('/api/v1/generate-excel')
        assert response.status_code in [200, 400, 422]
    
    def test_generate_excel_returns_json(self, client):
        """Excel generation should return JSON response"""
        response = client.post('/api/v1/generate-excel')
        assert response.content_type == 'application/json'


class TestTakeoffCalculation:
    """Test takeoff calculation endpoint"""
    
    def test_calculate_takeoff_endpoint_exists(self, client):
        """Takeoff calculation endpoint should be available"""
        response = client.post('/api/v1/calculate-takeoff')
        assert response.status_code in [200, 400, 422]
    
    def test_calculate_takeoff_returns_json(self, client):
        """Takeoff calculation should return JSON response"""
        response = client.post('/api/v1/calculate-takeoff')
        assert response.content_type == 'application/json'


class TestErrorHandling:
    """Test error handling"""
    
    def test_nonexistent_endpoint_returns_404(self, client):
        """Non-existent endpoint should return 404"""
        response = client.get('/api/v1/nonexistent')
        assert response.status_code == 404
