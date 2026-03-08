"""Reservation routes"""
from flask import Blueprint, request, jsonify
from middleware.auth_middleware import require_auth
from utils.db import db
from utils.logger import system_logger
from flask_jwt_extended import get_jwt_identity
from datetime import datetime, timedelta
import qrcode
import io
import base64

reservations_bp = Blueprint('reservations', __name__)

@reservations_bp.route('/', methods=['POST'])
@require_auth
def create_reservation():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()['user_id']
        slot_id = data.get('slot_id')
        duration = data.get('duration', 1)
        
        # Check availability
        slot = db.execute_query(
            "SELECT * FROM parking_slots WHERE slot_id = %s AND status = 'available'",
            (slot_id,)
        )
        
        if not slot:
            return jsonify({'error': 'Slot not available'}), 400
        
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration)
        
        # Generate QR
        qr_data = f"RES-{user_id}-{slot_id}-{int(start_time.timestamp())}"
        qr = qrcode.make(qr_data)
        buffered = io.BytesIO()
        qr.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Transaction
        queries = [
            ("UPDATE parking_slots SET status = 'reserved' WHERE slot_id = %s", (slot_id,)),
            ("""INSERT INTO reservations 
                (user_id, slot_id, start_time, end_time, qr_code, status)
                VALUES (%s, %s, %s, %s, %s, 'pending')""",
             (user_id, slot_id, start_time, end_time, qr_data))
        ]
        
        db.execute_transaction(queries)
        
        res_id = db.execute_query("SELECT LAST_INSERT_ID() as id")[0]['id']
        
        return jsonify({
            'success': True,
            'reservation_id': res_id,
            'qr_code': qr_base64,
            'qr_data': qr_data,
            'total_cost': slot[0]['hourly_rate'] * duration
        }), 201
        
    except Exception as e:
        system_logger.error('RESERVATION', f"Create error: {str(e)}")
        return jsonify({'error': 'Failed to create reservation'}), 500

@reservations_bp.route('/entry', methods=['POST'])
@require_auth
def process_entry():
    try:
        data = request.get_json()
        qr_data = data.get('qr_code')
        
        res = db.execute_query(
            """SELECT r.* FROM reservations r
               WHERE r.qr_code = %s AND r.status = 'pending'""",
            (qr_data,)
        )
        
        if not res:
            return jsonify({'error': 'Invalid QR code'}), 400
        
        entry_time = datetime.now()
        
        queries = [
            ("UPDATE reservations SET entry_time = %s, status = 'active' WHERE res_id = %s",
             (entry_time, res[0]['res_id'])),
            ("UPDATE parking_slots SET status = 'occupied' WHERE slot_id = %s",
             (res[0]['slot_id'],))
        ]
        
        db.execute_transaction(queries)
        
        return jsonify({
            'success': True,
            'entry_time': entry_time.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reservations_bp.route('/exit', methods=['POST'])
@require_auth
def process_exit():
    try:
        data = request.get_json()
        qr_data = data.get('qr_code')
        
        res = db.execute_query(
            """SELECT r.*, p.hourly_rate FROM reservations r
               JOIN parking_slots p ON r.slot_id = p.slot_id
               WHERE r.qr_code = %s AND r.status = 'active'""",
            (qr_data,)
        )
        
        if not res:
            return jsonify({'error': 'No active reservation'}), 400
        
        exit_time = datetime.now()
        entry_time = res[0]['entry_time']
        hours = (exit_time - entry_time).total_seconds() / 3600
        billed_hours = int(hours) + (1 if hours % 1 > 0 else 0)
        amount = billed_hours * res[0]['hourly_rate']
        
        queries = [
            ("UPDATE reservations SET exit_time = %s, status = 'completed' WHERE res_id = %s",
             (exit_time, res[0]['res_id'])),
            ("UPDATE parking_slots SET status = 'available' WHERE slot_id = %s",
             (res[0]['slot_id'],))
        ]
        
        db.execute_transaction(queries)
        
        # Create transaction
        trans_query = """INSERT INTO transactions 
            (user_id, res_id, entry_time, exit_time, duration_hours, amount, payment_status)
            VALUES (%s, %s, %s, %s, %s, %s, 'pending')"""
        
        trans_id = db.execute_query(trans_query,
            (res[0]['user_id'], res[0]['res_id'], entry_time, exit_time, hours, amount),
            fetch=False)
        
        return jsonify({
            'success': True,
            'amount': amount,
            'transaction_id': trans_id,
            'duration_hours': round(hours, 2)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500