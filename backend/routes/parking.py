"""Parking management routes"""
from flask import Blueprint, request, jsonify
from middleware.auth_middleware import require_auth, require_admin
from utils.db import db
from utils.logger import system_logger

parking_bp = Blueprint('parking', __name__)

@parking_bp.route('/slots', methods=['GET'])
@require_auth
def get_slots():
    try:
        location = request.args.get('location', '')
        status = request.args.get('status', 'available')
        
        query = "SELECT * FROM parking_slots WHERE status = %s"
        params = [status]
        
        if location:
            query += " AND location LIKE %s"
            params.append(f"%{location}%")
        
        slots = db.execute_query(query, tuple(params))
        
        return jsonify({
            'success': True,
            'count': len(slots),
            'data': slots
        }), 200
        
    except Exception as e:
        system_logger.error('PARKING', f"Error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve slots'}), 500

@parking_bp.route('/occupancy', methods=['GET'])
@require_admin
def get_occupancy():
    try:
        query = """
            SELECT status, COUNT(*) as count 
            FROM parking_slots 
            GROUP BY status
        """
        stats = db.execute_query(query)
        
        return jsonify({
            'success': True,
            'occupancy': stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@parking_bp.route('/slots/<int:slot_id>', methods=['PUT'])
@require_admin
def update_slot(slot_id):
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        query = "UPDATE parking_slots SET status = %s WHERE slot_id = %s"
        db.execute_query(query, (new_status, slot_id), fetch=False)
        
        system_logger.info('PARKING', f"Slot {slot_id} updated to {new_status}")
        
        return jsonify({
            'success': True,
            'message': f'Slot updated to {new_status}'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500