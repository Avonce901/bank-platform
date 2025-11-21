"""Utility functions and classes"""
from functools import wraps
from flask import request, jsonify

def rate_limit(calls=100, period=60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)
        return decorated_function
    return decorator

class ResponseFormatter:
    """Format API responses"""
    @staticmethod
    def success(data=None, message='Success'):
        return {'status': 'success', 'message': message, 'data': data}
    
    @staticmethod
    def error(message='Error', code=400):
        return {'status': 'error', 'message': message}, code

class RateLimiter:
    """Rate limiter class"""
    def __init__(self):
        self.calls = {}
    
    def check_rate_limit(self, key, calls=100, period=60):
        return True

class MetricsCollector:
    """Collect metrics"""
    def __init__(self):
        self.metrics = {}
    
    def record(self, key, value):
        pass
