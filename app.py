from flask import Flask
from models import db
from routes import register_blueprints
import os
from config import config

def config_setup(app):
    """Configure the Flask application with environment-specific settings.
    
    Args:
        app: The Flask application instance to configure.
    """
    config_name = os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])


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

if __name__ == '__main__':
    app = Flask(__name__)

    config_setup(app)
    setup_database(app)
    register_blueprints(app)

    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring application status.
        
        Returns:
            str: A simple health status message.
        """
        return 'healthy, thank you!'


    app.run(host='0.0.0.0', debug=True, port=5003)
