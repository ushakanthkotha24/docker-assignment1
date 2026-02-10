import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class for the application"""
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database configuration
    DATABASE_USER = os.getenv('DATABASE_USER', 'admin')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'password123')
    DATABASE_HOST = os.getenv('DATABASE_HOST', 'postgres')
    DATABASE_PORT = os.getenv('DATABASE_PORT', '5432')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'python_app_db')
    
    DATABASE_URL = (
        f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@"
        f"{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    )
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

# Select configuration based on environment
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
