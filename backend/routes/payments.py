"""Payment routes"""
from flask import Blueprint, request, jsonify
from middleware.auth_middleware import require_auth
from utils.db import db
from utils.logger import system_logger
from flask_jwt_extended import get_jwt_identity

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/process', methods=['POST'])
@require_auth
def process_payment():
    try:
        data = request.get_json()
        trans_id = data.get('transaction_id')
        user_id = get_jwt_identity()['user_id']
        
        trans = db.execute_query(
            "SELECT * FROM transactions WHERE trans_id = %s AND user_id = %s",
            (trans_id, user_id)
        )
        
        if not trans:
            return jsonify({'error': 'Transaction not found'}), 404
        
        if trans[0]['payment_status'] == 'completed':
            return jsonify({'error': 'Already paid'}), 400
        
        # Mock payment processing
        payment_ref = f"PAY-{trans_id}-{int(datetime.now().timestamp())}"
        
        db.execute_query(
            "UPDATE transactions SET payment_status = 'completed', payment_ref = %s WHERE trans_id = %s",
            (payment_ref, trans_id),
            fetch=False
        )
        
        system_logger.info('PAYMENT', f"Payment {payment_ref} completed", user_id)
        
        return jsonify({
            'success': True,
            'payment_ref': payment_ref,
            'amount': trans[0]['amount']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/history', methods=['GET'])
@require_auth
def payment_history():
    try:
        user_id = get_jwt_identity()['user_id']
        query = """SELECT t.*, p.slot_number 
                   FROM transactions t
                   JOIN reservations r ON t.res_id = r.res_id
                   JOIN parking_slots p ON r.slot_id = p.slot_id
                   WHERE t.user_id = %s
                   ORDER BY t.created_at DESC"""
        
        transactions = db.execute_query(query, (user_id,))
        
        return jsonify({
            'success': True,
            'data': transactions
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500