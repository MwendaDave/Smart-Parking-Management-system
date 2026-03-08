"""Database connection utility with transaction support"""
import mysql.connector
from mysql.connector import Error
from flask import current_app
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.connection = None
        
    def get_connection(self):
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connection = mysql.connector.connect(
                    host=current_app.config['MYSQL_HOST'],
                    user=current_app.config['MYSQL_USER'],
                    password=current_app.config['MYSQL_PASSWORD'],
                    database=current_app.config['MYSQL_DB'],
                    autocommit=False
                )
            return self.connection
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            raise
    
    def execute_query(self, query, params=None, fetch=True):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            if fetch:
                result = cursor.fetchall()
            else:
                result = cursor.lastrowid
            conn.commit()
            return result
        except Error as e:
            conn.rollback()
            logger.error(f"Query error: {e}")
            raise
        finally:
            cursor.close()
    
    def execute_transaction(self, queries):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            for query, params in queries:
                cursor.execute(query, params or ())
            conn.commit()
            return True
        except Error as e:
            conn.rollback()
            logger.error(f"Transaction error: {e}")
            raise
        finally:
            cursor.close()

db = Database()