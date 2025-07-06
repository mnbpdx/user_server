from flask import Flask
from models import db
from routes import register_blueprints
import os
from config import config
from logging_config import setup_logging, get_logger
from middleware import init_request_logging

logger = get_logger(__name__)

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
    """Initialize the database and create tables if they don't exist.
    
    Args:
        app: The Flask application instance to configure database for.
    """
    # initialize database
    db.init_app(app)

    # create empty tables if they don't exist yet
    with app.app_context():
        db.create_all()
        logger.info("Database initialized and tables created")

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

if __name__ == '__main__':
    setup_logging()  # Move this here
    logger.info("Starting Flask application")
    
    app = Flask(__name__)

    config_setup(app)
    setup_database(app)
    setup_logging_middleware(app)
    register_blueprints(app)

    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring application status.
        
        Returns:
            str: A simple health status message.
        """
        logger.debug("Health check requested")
        return 'healthy, thank you!'

    logger.info("Flask application ready to start", 
                host='0.0.0.0', 
                port=5003, 
                debug=app.config.get('DEBUG', False))
    
    app.run(host='0.0.0.0', debug=True, port=5003)
