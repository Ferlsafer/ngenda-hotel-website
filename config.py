import os

class Config:
    """Configuration class for Ngenda Hotel Flask Application"""
    
    # Basic Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ngenda-hotel-secret-key-2024'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', 'on', '1']
    
    # Hotel Management System API Configuration
    HMS_API_URL = os.environ.get('HMS_API_URL') or 'http://localhost:5000'
    HMS_API_KEY = os.environ.get('HMS_API_KEY') or 'ngenda_website_key'
    
    # HMS Authentication Configuration
    HMS_AUTH_EMAIL = os.environ.get('HMS_AUTH_EMAIL') or 'website@ngendahotel.com'
    HMS_AUTH_PASSWORD = os.environ.get('HMS_AUTH_PASSWORD') or 'website-service-account-2026'
    HMS_HOTEL_ID = os.environ.get('HMS_HOTEL_ID') or '1'
    
    # HMS Endpoint Configuration
    HMS_PUBLIC_ROOMS_ENDPOINT = '/api/public/rooms'  # No token needed
    HMS_BOOKINGS_ENDPOINT = '/api/bookings/'        # Requires JWT token
    HMS_AUTH_ENDPOINT = '/api/auth/login'           # Authentication endpoint
    
    # Database Configuration (for future use)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///ngenda_hotel.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Static Files Configuration
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    
    # Hotel Specific Settings
    HOTEL_NAME = 'Ngenda Hotel'
    HOTEL_LOCATION = 'Mbeya, Tanzania'
    HOTEL_CURRENCY = 'TZS'
    
    # Booking Configuration
    MAX_GUESTS_PER_ROOM = 4
    MIN_BOOKING_DAYS = 1
    MAX_BOOKING_DAYS = 30
    
    # API Configuration
    API_TIMEOUT = 30  # seconds
    API_RETRY_ATTEMPTS = 3
    
    @staticmethod
    def init_app(app):
        """Initialize Flask app with configuration"""
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    HMS_API_URL = 'http://localhost:5000'  # Development API URL

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    HMS_API_URL = os.environ.get('HMS_API_URL') or 'https://api.ngendahotel.com'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    HMS_API_URL = 'http://localhost:5001'  # Test API URL

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
