import os

class Config:
    """Base configuration class for the Flask application.
    
    Contains common configuration settings that can be inherited by
    environment-specific configuration classes.
    
    Attributes:
        SECRET_KEY: Secret key for Flask session management and security.
        SQLALCHEMY_DATABASE_URI: Database connection string.
        SQLALCHEMY_TRACK_MODIFICATIONS: Disable SQLAlchemy modification tracking for performance.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Development environment configuration.
    
    Inherits from Config and enables debug mode for development.
    """
    DEBUG = True

class ProductionConfig(Config):
    """Production environment configuration.
    
    Inherits from Config and disables debug mode for production deployment.
    """
    DEBUG = False

class TestingConfig(Config):
    """Testing environment configuration.
    
    Inherits from Config and configures settings for testing.
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
