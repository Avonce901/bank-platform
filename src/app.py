"""
Banking Platform - Flask Application
Production-ready minimal entry point
"""

import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'Banking Platform API', 'version': '1.0.0'})

@app.route('/status', methods=['GET'])
def status():
    return jsonify({'status': 'running', 'version': '1.0.0'})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
