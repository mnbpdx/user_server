import time
import uuid
from flask import request, g
from logging_config import get_request_logger
import structlog


class RequestLoggingMiddleware:
    """Middleware for logging all Flask requests and responses.
    
    This middleware captures comprehensive information about each request
    including timing, request details, response information, and client data.
    """
    
    def __init__(self, app=None):
        """Initialize the request logging middleware.
        
        Args:
            app (Flask, optional): Flask application instance. Defaults to None.
        """
        self.app = app
        self.logger = get_request_logger()
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with a Flask app.
        
        Args:
            app (Flask): Flask application instance.
        """
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_appcontext(self.teardown_request)
    
    def before_request(self):
        """Execute before each request to capture start time and request ID."""
        g.start_time = time.time()
        g.request_id = str(uuid.uuid4())
        
        # Log the incoming request
        self.logger.info(
            "Request started",
            request_id=g.request_id,
            method=request.method,
            url=request.url,
            path=request.path,
            remote_addr=self.get_client_ip(),
            user_agent=request.headers.get('User-Agent', 'Unknown'),
            content_type=request.headers.get('Content-Type', 'Unknown'),
            content_length=request.headers.get('Content-Length', 0),
            query_params=dict(request.args),
            headers=dict(request.headers),
            is_json=request.is_json
        )
    
    def after_request(self, response):
        """Execute after each request to log response details.
        
        Args:
            response: Flask response object.
            
        Returns:
            response: The unmodified response object.
        """
        # Calculate request duration
        duration = time.time() - g.start_time if hasattr(g, 'start_time') else 0
        
        # Log the response
        self.logger.info(
            "Request completed",
            request_id=getattr(g, 'request_id', 'unknown'),
            method=request.method,
            url=request.url,
            path=request.path,
            status_code=response.status_code,
            status=response.status,
            duration_seconds=round(duration, 4),
            response_size=len(response.get_data()) if response.get_data() else 0,
            content_type=response.headers.get('Content-Type', 'Unknown'),
            remote_addr=self.get_client_ip(),
            user_agent=request.headers.get('User-Agent', 'Unknown')
        )
        
        # Add request ID to response headers for tracking
        response.headers['X-Request-ID'] = getattr(g, 'request_id', 'unknown')
        
        return response
    
    def teardown_request(self, exception=None):
        """Execute after request teardown to log any exceptions.
        
        Args:
            exception: Exception that occurred during request processing, if any.
        """
        if exception:
            duration = time.time() - g.start_time if hasattr(g, 'start_time') else 0
            
            self.logger.error(
                "Request failed with exception",
                request_id=getattr(g, 'request_id', 'unknown'),
                method=request.method,
                url=request.url,
                path=request.path,
                duration_seconds=round(duration, 4),
                exception=str(exception),
                exception_type=type(exception).__name__,
                remote_addr=self.get_client_ip(),
                user_agent=request.headers.get('User-Agent', 'Unknown')
            )
    
    def get_client_ip(self):
        """Get the client's IP address, accounting for proxies.
        
        Returns:
            str: Client IP address.
        """
        # Check for forwarded headers (common in production deployments)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            # Take the first IP if multiple are present
            return forwarded_for.split(',')[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        # Fall back to remote address
        return request.remote_addr or 'unknown'


def init_request_logging(app):
    """Initialize request logging middleware for a Flask app.
    
    Args:
        app (Flask): Flask application instance.
    """
    middleware = RequestLoggingMiddleware(app)
    return middleware 