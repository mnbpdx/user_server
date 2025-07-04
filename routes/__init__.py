from .users import users_bp

def register_blueprints(app):
    """Register all application blueprints with the Flask app.
    
    Args:
        app: The Flask application instance to register blueprints with.
    """
    app.register_blueprint(users_bp)
