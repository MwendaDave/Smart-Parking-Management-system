import os

class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'dev-secret-key-change-in-production'
    
    # MySQL Configuration - UPDATE THE PASSWORD
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '000000'  
    MYSQL_DB = 'smart_parking'
    
    JWT_SECRET_KEY = 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}