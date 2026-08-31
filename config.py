import os
from datetime import timedelta

# Ensure instance folder exists
INSTANCE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(INSTANCE_PATH, exist_ok=True)

class Config:
    """Application configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{os.path.join(INSTANCE_PATH, "bookstore.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Application settings
    APP_NAME = 'Book Ninja'
    APP_DESCRIPTION = 'A modern bookstore for the discerning reader'
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Admin settings
    ADMIN_EMAIL = 'admin@bookninja.com'
    
    # Cart settings
    FREE_SHIPPING_THRESHOLD = 500  # INR
    SHIPPING_COST = 50  # INR