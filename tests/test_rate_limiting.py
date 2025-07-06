import pytest
from flask import Flask
from rate_limiting import limiter


class TestRateLimiting:
    """Test the rate limiting module."""
    
    def test_limiter_exists(self):
        """Test that limiter instance exists."""
        assert limiter is not None
        
    def test_limiter_configuration(self):
        """Test that limiter has correct configuration."""
        # Check that limiter has default limits (using private attribute)
        assert limiter._default_limits_cost == 1
        
    def test_limiter_key_function(self):
        """Test that limiter has a key function."""
        assert limiter._key_func is not None
        
    def test_limiter_initialization_with_app(self):
        """Test that limiter can be initialized with Flask app."""
        app = Flask(__name__)
        app.config['RATELIMIT_STORAGE_URI'] = 'memory://'
        
        # Initialize limiter with app
        limiter.init_app(app)
        
        # Check that limiter is properly bound to app
        assert hasattr(app, 'extensions')
        assert 'limiter' in app.extensions
        
    def test_limiter_with_test_app(self):
        """Test limiter with a test Flask app."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['RATELIMIT_STORAGE_URI'] = 'memory://'
        
        limiter.init_app(app)
        
        @app.route('/test')
        @limiter.limit("1 per minute")
        def test_endpoint():
            return "test"
            
        with app.test_client() as client:
            # First request should succeed
            response = client.get('/test')
            assert response.status_code == 200
            
            # Second request within the same minute should be rate limited
            response = client.get('/test')
            assert response.status_code == 429  # Too Many Requests 