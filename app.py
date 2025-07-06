from flask import Flask
from flask_migrate import Migrate
from models import db
from routes import register_blueprints
from rate_limiting import limiter
from api_docs import api
import os
from config import config
from logging_config import setup_logging, get_logger
from middleware import init_request_logging

logger = get_logger(__name__)
migrate = Migrate()

def config_setup(app):
    """Configure the Flask application with environment-specific settings.
    
    Args:
        app: The Flask application instance to configure.
    """
    config_name = os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[config_name]())
    
    logger.info("Application configured", 
                environment=config_name,
                debug=app.config.get('DEBUG', False),
                request_logging_enabled=app.config.get('REQUEST_LOGGING_ENABLED', True))


def setup_database(app):
    """Initialize the database and Flask-Migrate.
    
    Args:
        app: The Flask application instance to configure database for.
    """
    # initialize database
    db.init_app(app)

    # initialize Flask-Migrate
    migrate.init_app(app, db)
    
    logger.info("Database and Flask-Migrate initialized")

def setup_rate_limiting(app):
    """Initialize Flask-Limiter for rate limiting.
    
    Args:
        app: The Flask application instance to configure rate limiting for.
    """
    # Skip rate limiting setup if disabled
    if not app.config.get('RATELIMIT_ENABLED', True):
        logger.info("Rate limiting disabled")
        return
    
    # configure rate limiting storage
    app.config['RATELIMIT_STORAGE_URI'] = app.config.get('RATELIMIT_STORAGE_URI', 'redis://redis:6379')
    app.config['RATELIMIT_HEADERS_ENABLED'] = app.config.get('RATELIMIT_HEADERS_ENABLED', True)
    
    # initialize Flask-Limiter
    limiter.init_app(app)
    
    logger.info("Flask-Limiter initialized with storage: %s", app.config['RATELIMIT_STORAGE_URI'])

def setup_logging_middleware(app):
    """Setup request logging middleware if enabled.
    
    Args:
        app: The Flask application instance to configure middleware for.
    """
    if app.config.get('REQUEST_LOGGING_ENABLED', True):
        init_request_logging(app)
        logger.info("Request logging middleware initialized")
    else:
        logger.info("Request logging middleware disabled")

def setup_api_documentation(app):
    """Initialize Flask-RESTX API documentation.
    
    Args:
        app: The Flask application instance to configure API documentation for.
    """
    # Initialize Flask-RESTX API
    api.init_app(app)
    
    logger.info("Flask-RESTX API documentation initialized at /docs")

def create_app():
    """Create and configure the Flask application.
    
    Returns:
        Flask: The configured Flask application instance.
    """
    setup_logging()
    logger.info("Creating Flask application")
    
    app = Flask(__name__)

    config_setup(app)
    setup_database(app)
    setup_rate_limiting(app)
    setup_logging_middleware(app)
    setup_api_documentation(app)
    register_blueprints(app)

    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring application status.
        
        Returns:
            str: A simple health status message.
        """
        logger.debug("Health check requested")
        return 'healthy, thank you!'

    logger.info("Flask application created and configured")
    return app

# Create the app for Flask CLI
app = create_app()

if __name__ == '__main__':
    logger.info("Starting Flask application", 
                host='0.0.0.0', 
                port=5003, 
                debug=app.config.get('DEBUG', False))
    
    app.run(host='0.0.0.0', debug=True, port=5003)
