"""
Smart Parking Management System - Flask Backend
SPMS v1.0
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from datetime import timedelta

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Database config
app.config['MYSQL_HOST'] = os.environ.get('DB_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('DB_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('DB_PASSWORD', '')
app.config['MYSQL_DB'] = os.environ.get('DB_NAME', 'smart_parking')

# Initialize extensions
CORS(app)
jwt = JWTManager(app)

# Import and register blueprints
from routes.auth import auth_bp
from routes.parking import parking_bp
from routes.reservations import reservations_bp
from routes.payments import payments_bp
from routes.reports import reports_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(parking_bp, url_prefix='/api/parking')
app.register_blueprint(reservations_bp, url_prefix='/api/reservations')
app.register_blueprint(payments_bp, url_prefix='/api/payments')
app.register_blueprint(reports_bp, url_prefix='/api/reports')

@app.route('/')
def index():
    return jsonify({
        'message': 'Smart Parking Management System API',
        'version': '1.0',
        'status': 'operational',
        'endpoints': {
            'auth': '/api/auth',
            'parking': '/api/parking',
            'reservations': '/api/reservations',
            'payments': '/api/payments',
            'reports': '/api/reports'
        }
    })

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'SPMS API'}), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)