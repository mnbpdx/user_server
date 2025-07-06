import structlog
import logging
import logging.handlers
import os
from datetime import datetime
import json


def setup_logging():
    """Configure structlog for request logging.
    
    Sets up structured logging with JSON format, log rotation, and appropriate
    processors for development and production environments.
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
        handlers=[
            logging.StreamHandler(),
        ]
    )
    
    # Set root logger level explicitly
    logging.getLogger().setLevel(logging.INFO)
    
    # Add file handler with rotation if log directory exists or create it
    log_dir = os.environ.get('LOG_DIR', 'logs')
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except PermissionError:
            # If we can't create the directory, fall back to /tmp or current directory
            log_dir = os.environ.get('TMPDIR', '/tmp')
            if not os.path.exists(log_dir):
                log_dir = '.'
    
    # Add rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, 'user_server.log'),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    
    # Add request log handler
    request_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, 'requests.log'),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    request_handler.setLevel(logging.INFO)
    
    # Add handlers to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name=None):
    """Get a structlog logger instance.
    
    Args:
        name (str, optional): Logger name. Defaults to None.
        
    Returns:
        structlog.BoundLogger: Configured logger instance.
    """
    return structlog.get_logger(name)


def get_request_logger():
    """Get a logger specifically for request logging.
    
    Returns:
        structlog.BoundLogger: Logger configured for request logging.
    """
    return structlog.get_logger("requests") 