import os

class Config:
    """Base configuration class for the Flask application.
    
    Contains common configuration settings that can be inherited by
    environment-specific configuration classes.
    
    Attributes:
        SECRET_KEY: Secret key for Flask session management and security.
        SQLALCHEMY_DATABASE_URI: Database connection string.
        SQLALCHEMY_TRACK_MODIFICATIONS: Disable SQLAlchemy modification tracking for performance.
        LOG_LEVEL: Logging level for the application.
        LOG_DIR: Directory for log files.
        REQUEST_LOGGING_ENABLED: Enable/disable request logging.
        LOG_RETENTION_DAYS: Number of days to retain log files.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_DIR = os.environ.get('LOG_DIR', 'logs')
    REQUEST_LOGGING_ENABLED = os.environ.get('REQUEST_LOGGING_ENABLED', 'true').lower() == 'true'
    LOG_RETENTION_DAYS = int(os.environ.get('LOG_RETENTION_DAYS', '30'))
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', '10485760'))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', '5'))

class DevelopmentConfig(Config):
    """Development environment configuration.
    
    Inherits from Config and enables debug mode for development.
    """
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production environment configuration.
    
    Inherits from Config and disables debug mode for production deployment.
    """
    DEBUG = False
    LOG_LEVEL = 'INFO'

class TestingConfig(Config):
    """Testing environment configuration.
    
    Inherits from Config and configures settings for testing.
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    REQUEST_LOGGING_ENABLED = False  # Disable request logging in tests
    LOG_LEVEL = 'WARNING'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
