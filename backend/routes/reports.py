"""Reporting routes"""
from flask import Blueprint, request, jsonify
from middleware.auth_middleware import require_admin
from utils.db import db
from utils.logger import system_logger
from datetime import datetime, timedelta

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/usage', methods=['GET'])
@require_admin
def usage_report():
    try:
        report_type = request.args.get('type', 'daily')
        
        if report_type == 'daily':
            query = """
                SELECT DATE(created_at) as date, 
                       COUNT(*) as total,
                       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
                FROM reservations
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                GROUP BY DATE(created_at)
            """
        else:
            query = """
                SELECT DATE_FORMAT(created_at, '%Y-%m') as month,
                       COUNT(*) as total
                FROM reservations
                GROUP BY DATE_FORMAT(created_at, '%Y-%m')
            """
        
        data = db.execute_query(query)
        
        return jsonify({
            'success': True,
            'type': report_type,
            'data': data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/logs', methods=['GET'])
@require_admin
def system_logs():
    try:
        limit = int(request.args.get('limit', 100))
        logs = db.execute_query(
            "SELECT * FROM system_logs ORDER BY timestamp DESC LIMIT %s",
            (limit,)
        )
        
        return jsonify({
            'success': True,
            'count': len(logs),
            'data': logs
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500