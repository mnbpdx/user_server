import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, g, request
from middleware.request_logging import RequestLoggingMiddleware


class TestRequestLoggingMiddleware:
    """Test the RequestLoggingMiddleware class."""
    
    def test_middleware_initialization(self):
        """Test middleware initialization without app."""
        middleware = RequestLoggingMiddleware()
        
        assert middleware.app is None
        assert middleware.logger is not None
    
    def test_middleware_initialization_with_app(self):
        """Test middleware initialization with app."""
        app = Flask(__name__)
        middleware = RequestLoggingMiddleware(app)
        
        assert middleware.app == app
        assert middleware.logger is not None
    
    @patch('middleware.request_logging.get_request_logger')
    def test_init_app(self, mock_get_logger):
        """Test init_app method."""
        app = Flask(__name__)
        middleware = RequestLoggingMiddleware()
        
        middleware.init_app(app)
        
        # Verify logger was retrieved
        mock_get_logger.assert_called_once()
        assert middleware.logger == mock_get_logger.return_value
    
    def test_before_request_sets_globals(self):
        """Test before_request sets g.start_time and g.request_id."""
        app = Flask(__name__)
        middleware = RequestLoggingMiddleware()
        
        with app.test_request_context('/test'):
            with patch('middleware.request_logging.time.time', return_value=1234567890.0):
                with patch('middleware.request_logging.uuid.uuid4') as mock_uuid:
                    mock_uuid.return_value.__str__ = Mock(return_value='test-uuid')
                    middleware.before_request()
                    
                    assert hasattr(g, 'start_time')
                    assert hasattr(g, 'request_id')
                    assert g.start_time == 1234567890.0
                    assert g.request_id == 'test-uuid'
    
    @patch('middleware.request_logging.get_request_logger')
    def test_before_request_logs_request(self, mock_get_logger):
        """Test before_request logs the incoming request."""
        app = Flask(__name__)
        
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        middleware = RequestLoggingMiddleware()
        middleware.logger = mock_logger
        
        with app.test_request_context('/test', method='POST', 
                                     headers={'User-Agent': 'test-agent', 'Content-Type': 'application/json'},
                                     query_string='param=value'):
            with patch('middleware.request_logging.time.time', return_value=1234567890.0):
                with patch('middleware.request_logging.uuid.uuid4') as mock_uuid:
                    mock_uuid.return_value.__str__ = Mock(return_value='test-uuid')
                    middleware.before_request()
                    
                    # Verify logger was called
                    mock_logger.info.assert_called_once()
                    args, kwargs = mock_logger.info.call_args
                    
                    assert args[0] == "Request started"
                    assert kwargs['request_id'] == 'test-uuid'
                    assert kwargs['method'] == 'POST'
                    assert kwargs['path'] == '/test'
                    assert kwargs['user_agent'] == 'test-agent'
                    assert kwargs['content_type'] == 'application/json'
    
    def test_get_client_ip_with_forwarded_for(self):
        """Test get_client_ip with X-Forwarded-For header."""
        app = Flask(__name__)
        middleware = RequestLoggingMiddleware()
        
        with app.test_request_context('/test', headers={'X-Forwarded-For': '192.168.1.1, 10.0.0.1'}):
            ip = middleware.get_client_ip()
            assert ip == '192.168.1.1'
    
    def test_get_client_ip_with_real_ip(self):
        """Test get_client_ip with X-Real-IP header."""
        app = Flask(__name__)
        middleware = RequestLoggingMiddleware()
        
        with app.test_request_context('/test', headers={'X-Real-IP': '192.168.1.1'}):
            ip = middleware.get_client_ip()
            assert ip == '192.168.1.1'
    
    def test_get_client_ip_fallback_to_remote_addr(self):
        """Test get_client_ip falls back to remote_addr."""
        app = Flask(__name__)
        middleware = RequestLoggingMiddleware()
        
        with app.test_request_context('/test', environ_base={'REMOTE_ADDR': '192.168.1.1'}):
            ip = middleware.get_client_ip()
            assert ip == '192.168.1.1'
    
    def test_get_client_ip_unknown_fallback(self):
        """Test get_client_ip returns 'unknown' when no IP available."""
        app = Flask(__name__)
        middleware = RequestLoggingMiddleware()
        
        with app.test_request_context('/test'):
            # Mock request.remote_addr to be None
            with patch('flask.request') as mock_request:
                mock_request.headers = {}
                mock_request.remote_addr = None
                
                ip = middleware.get_client_ip()
                assert ip == 'unknown'
    
    @patch('middleware.request_logging.get_request_logger')
    def test_after_request_logs_response(self, mock_get_logger):
        """Test after_request logs response details."""
        app = Flask(__name__)
        
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        middleware = RequestLoggingMiddleware()
        middleware.logger = mock_logger
        
        with app.test_request_context('/test'):
            # Set up g values as if before_request was called
            g.start_time = 1234567890.0
            g.request_id = 'test-uuid'
            
            # Create a mock response
            response = Mock()
            response.status_code = 200
            response.status = '200 OK'
            response.get_data.return_value = b'{"result": "success"}'
            response.headers = {'Content-Type': 'application/json'}
            
            with patch('middleware.request_logging.time.time', return_value=1234567890.5):
                result = middleware.after_request(response)
                
                # Verify response is returned unchanged
                assert result == response
                
                # Verify logger was called
                mock_logger.info.assert_called_once()
                args, kwargs = mock_logger.info.call_args
                
                assert args[0] == "Request completed"
                assert kwargs['request_id'] == 'test-uuid'
                assert kwargs['status_code'] == 200
                assert kwargs['status'] == '200 OK'
                assert kwargs['duration_seconds'] == 0.5
                assert kwargs['response_size'] == 21  # Length of response data
    
    def test_after_request_adds_request_id_header(self):
        """Test after_request adds X-Request-ID header to response."""
        app = Flask(__name__)
        middleware = RequestLoggingMiddleware()
        
        with app.test_request_context('/test'):
            g.request_id = 'test-uuid'
            
            response = Mock()
            response.status_code = 200
            response.status = '200 OK'
            response.get_data.return_value = b'test'
            response.headers = {}
            
            middleware.after_request(response)
            
            # Verify X-Request-ID header was added
            assert response.headers['X-Request-ID'] == 'test-uuid'
    
    def test_after_request_handles_missing_start_time(self):
        """Test after_request handles case where start_time is not set."""
        app = Flask(__name__)
        middleware = RequestLoggingMiddleware()
        
        with app.test_request_context('/test'):
            g.request_id = 'test-uuid'
            # Don't set g.start_time
            
            response = Mock()
            response.status_code = 200
            response.status = '200 OK'
            response.get_data.return_value = b'test'
            response.headers = {}
            
            with patch('middleware.request_logging.time.time', return_value=1234567890.5):
                result = middleware.after_request(response)
                
                # Should not raise an exception
                assert result == response
    
    def test_after_request_handles_missing_request_id(self):
        """Test after_request handles case where request_id is not set."""
        app = Flask(__name__)
        middleware = RequestLoggingMiddleware()
        
        with app.test_request_context('/test'):
            g.start_time = 1234567890.0
            # Don't set g.request_id
            
            response = Mock()
            response.status_code = 200
            response.status = '200 OK'
            response.get_data.return_value = b'test'
            response.headers = {}
            
            result = middleware.after_request(response)
            
            # Should use 'unknown' as fallback
            assert result == response
            assert response.headers['X-Request-ID'] == 'unknown'
    
    @patch('middleware.request_logging.get_request_logger')
    def test_teardown_request_logs_exception(self, mock_get_logger):
        """Test teardown_request logs exceptions."""
        app = Flask(__name__)
        
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        middleware = RequestLoggingMiddleware()
        middleware.logger = mock_logger
        
        with app.test_request_context('/test'):
            g.start_time = 1234567890.0
            g.request_id = 'test-uuid'
            
            # Create a test exception
            exception = ValueError("Test error")
            
            with patch('middleware.request_logging.time.time', return_value=1234567890.5):
                middleware.teardown_request(exception)
                
                # Verify logger was called
                mock_logger.error.assert_called_once()
                args, kwargs = mock_logger.error.call_args
                
                assert args[0] == "Request failed with exception"
                assert kwargs['request_id'] == 'test-uuid'
                assert kwargs['duration_seconds'] == 0.5
                assert kwargs['exception'] == 'Test error'
                assert kwargs['exception_type'] == 'ValueError'
    
    def test_teardown_request_no_exception(self):
        """Test teardown_request does nothing when no exception."""
        app = Flask(__name__)
        middleware = RequestLoggingMiddleware()
        
        with app.test_request_context('/test'):
            # Should not raise any exception
            middleware.teardown_request(None)
    
    def test_teardown_request_handles_missing_globals(self):
        """Test teardown_request handles missing g values."""
        app = Flask(__name__)
        middleware = RequestLoggingMiddleware()
        
        with app.test_request_context('/test'):
            # Don't set g.start_time or g.request_id
            exception = ValueError("Test error")
            
            # Should not raise an exception
            middleware.teardown_request(exception)
    
    def test_middleware_integration_with_app(self):
        """Test middleware integration with Flask app."""
        app = Flask(__name__)
        
        # Initialize middleware
        middleware = RequestLoggingMiddleware(app)
        
        # Test that hooks are registered
        assert len(app.before_request_funcs[None]) >= 1
        assert len(app.after_request_funcs[None]) >= 1
        assert len(app.teardown_appcontext_funcs) >= 1
    
    @patch('middleware.request_logging.get_request_logger')
    def test_full_request_cycle(self, mock_get_logger):
        """Test complete request cycle with middleware."""
        app = Flask(__name__)
        
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        middleware = RequestLoggingMiddleware(app)
        
        @app.route('/test')
        def test_route():
            return 'Test response'
        
        with app.test_client() as client:
            response = client.get('/test')
            
            # Verify response is successful
            assert response.status_code == 200
            assert response.get_data(as_text=True) == 'Test response'
            
            # Verify request logging was called
            assert mock_logger.info.call_count >= 2  # Before and after request
            
            # Verify X-Request-ID header is present
            assert 'X-Request-ID' in response.headers
    
    def test_middleware_with_json_request(self):
        """Test middleware with JSON request."""
        app = Flask(__name__)
        middleware = RequestLoggingMiddleware()
        
        with app.test_request_context('/test', method='POST', 
                                     data='{"key": "value"}',
                                     content_type='application/json'):
            # Should handle JSON request without error
            middleware.before_request()
            
            assert hasattr(g, 'start_time')
            assert hasattr(g, 'request_id')
    
    def test_middleware_with_large_response(self):
        """Test middleware with large response."""
        app = Flask(__name__)
        middleware = RequestLoggingMiddleware()
        
        with app.test_request_context('/test'):
            g.start_time = 1234567890.0
            g.request_id = 'test-uuid'
            
            # Create a large response
            large_data = 'x' * 10000
            response = Mock()
            response.status_code = 200
            response.status = '200 OK'
            response.get_data.return_value = large_data.encode()
            response.headers = {}
            
            result = middleware.after_request(response)
            
            # Should handle large response without error
            assert result == response
    
    def test_middleware_with_special_characters_in_url(self):
        """Test middleware with special characters in URL."""
        app = Flask(__name__)
        middleware = RequestLoggingMiddleware()
        
        with app.test_request_context('/test%20path?param=value%20with%20spaces'):
            # Should handle special characters without error
            middleware.before_request()
            
            assert hasattr(g, 'start_time')
            assert hasattr(g, 'request_id')


class TestRequestLoggingMiddlewareInitFunction:
    """Test the init_request_logging function."""
    
    def test_init_request_logging(self):
        """Test init_request_logging function."""
        from middleware.request_logging import init_request_logging
        
        app = Flask(__name__)
        
        # Initialize middleware
        middleware = init_request_logging(app)
        
        # Verify middleware is returned
        assert isinstance(middleware, RequestLoggingMiddleware)
        assert middleware.app == app
        
        # Verify hooks are registered
        assert len(app.before_request_funcs[None]) >= 1
        assert len(app.after_request_funcs[None]) >= 1
        assert len(app.teardown_appcontext_funcs) >= 1 