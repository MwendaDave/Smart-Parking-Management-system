"""System logging utility"""
import logging
from utils.db import db

class SystemLogger:
    def __init__(self):
        self.logger = logging.getLogger('SPMS')
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
    def log(self, level, component, message, user_id=None):
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(f"[{component}] {message}")
        
        try:
            query = """
                INSERT INTO system_logs (level, component, message, user_id)
                VALUES (%s, %s, %s, %s)
            """
            db.execute_query(query, (level, component, message, user_id), fetch=False)
        except Exception as e:
            self.logger.error(f"Failed to log to database: {e}")
    
    def info(self, component, message, user_id=None):
        self.log('INFO', component, message, user_id)
    
    def warning(self, component, message, user_id=None):
        self.log('WARNING', component, message, user_id)
    
    def error(self, component, message, user_id=None):
        self.log('ERROR', component, message, user_id)
    
    def critical(self, component, message, user_id=None):
        self.log('CRITICAL', component, message, user_id)

system_logger = SystemLogger()