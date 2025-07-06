from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import current_app

def is_rate_limiting_enabled():
    """Check if rate limiting is enabled in current app config."""
    try:
        return current_app.config.get('RATELIMIT_ENABLED', True)
    except RuntimeError:
        # Outside of application context, assume enabled
        return True

# Create the limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    enabled=is_rate_limiting_enabled
) 