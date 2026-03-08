"""Routes package"""
from .auth import auth_bp
from .parking import parking_bp
from .reservations import reservations_bp
from .payments import payments_bp
from .reports import reports_bp

__all__ = ['auth_bp', 'parking_bp', 'reservations_bp', 'payments_bp', 'reports_bp']