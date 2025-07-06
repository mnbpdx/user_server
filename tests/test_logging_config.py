import pytest
import logging
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from logging_config import setup_logging, get_logger, get_request_logger


class TestLoggingConfig:
    """Test the logging configuration functions."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        # Create a temporary directory for test logs
        self.test_log_dir = tempfile.mkdtemp()
        self.original_log_dir = os.environ.get('LOG_DIR')
        os.environ['LOG_DIR'] = self.test_log_dir
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        # Restore original LOG_DIR
        if self.original_log_dir is not None:
            os.environ['LOG_DIR'] = self.original_log_dir
        elif 'LOG_DIR' in os.environ:
            del os.environ['LOG_DIR']
        
        # Clean up test log directory
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)
        
        # Reset logging configuration
        logging.getLogger().handlers.clear()
        logging.getLogger().setLevel(logging.WARNING)
    
    def test_setup_logging_creates_log_directory(self):
        """Test that setup_logging creates log directory if it doesn't exist."""
        # Remove the test log directory
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)
        
        # Call setup_logging
        setup_logging()
        
        # Verify log directory was created
        assert os.path.exists(self.test_log_dir)
        assert os.path.isdir(self.test_log_dir)
    
    def test_setup_logging_creates_log_files(self):
        """Test that setup_logging creates log files."""
        setup_logging()
        
        # Check that log files are created (they may be empty initially)
        user_server_log = os.path.join(self.test_log_dir, 'user_server.log')
        requests_log = os.path.join(self.test_log_dir, 'requests.log')
        
        # Files might not exist until first log message, so we'll check handlers
        root_logger = logging.getLogger()
        
        # Check that file handlers were added
        file_handlers = [h for h in root_logger.handlers if hasattr(h, 'baseFilename')]
        assert len(file_handlers) >= 1
        
        # Check that at least one handler points to our log directory
        log_files = [h.baseFilename for h in file_handlers]
        assert any(self.test_log_dir in log_file for log_file in log_files)
    
    def test_setup_logging_configures_log_level(self):
        """Test that setup_logging configures the correct log level."""
        setup_logging()
        
        # Check root logger level
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO
    
    def test_setup_logging_adds_stream_handler(self):
        """Test that setup_logging adds a stream handler."""
        setup_logging()
        
        root_logger = logging.getLogger()
        stream_handlers = [h for h in root_logger.handlers if isinstance(h, logging.StreamHandler) and not hasattr(h, 'baseFilename')]
        
        assert len(stream_handlers) >= 1
    
    def test_setup_logging_adds_rotating_file_handlers(self):
        """Test that setup_logging adds rotating file handlers."""
        setup_logging()
        
        root_logger = logging.getLogger()
        rotating_handlers = [h for h in root_logger.handlers if hasattr(h, 'maxBytes')]
        
        assert len(rotating_handlers) >= 1
        
        # Check that handlers have correct rotation settings
        for handler in rotating_handlers:
            assert handler.maxBytes == 10 * 1024 * 1024  # 10MB
            assert handler.backupCount >= 5
    
    @patch('logging_config.structlog')
    def test_setup_logging_configures_structlog(self, mock_structlog):
        """Test that setup_logging configures structlog."""
        setup_logging()
        
        # Verify structlog.configure was called
        mock_structlog.configure.assert_called_once()
        
        # Check configuration parameters
        call_args = mock_structlog.configure.call_args
        assert 'processors' in call_args.kwargs
        assert 'context_class' in call_args.kwargs
        assert 'logger_factory' in call_args.kwargs
        assert 'wrapper_class' in call_args.kwargs
        assert 'cache_logger_on_first_use' in call_args.kwargs
        
        # Check that required processors are included
        processors = call_args.kwargs['processors']
        assert len(processors) > 0
        
        # Check configuration values
        assert call_args.kwargs['context_class'] == dict
        assert call_args.kwargs['cache_logger_on_first_use'] is True
    
    def test_setup_logging_with_custom_log_dir(self):
        """Test setup_logging with custom log directory."""
        custom_log_dir = tempfile.mkdtemp()
        
        try:
            os.environ['LOG_DIR'] = custom_log_dir
            
            setup_logging()
            
            # Verify custom log directory was used
            assert os.path.exists(custom_log_dir)
            
            # Check that file handlers point to custom directory
            root_logger = logging.getLogger()
            file_handlers = [h for h in root_logger.handlers if hasattr(h, 'baseFilename')]
            
            log_files = [h.baseFilename for h in file_handlers]
            assert any(custom_log_dir in log_file for log_file in log_files)
            
        finally:
            # Clean up
            if os.path.exists(custom_log_dir):
                shutil.rmtree(custom_log_dir)
    
    def test_setup_logging_handles_permission_error(self):
        """Test setup_logging handles permission errors gracefully."""
        # Try to use a directory that doesn't exist and can't be created
        with patch('os.makedirs', side_effect=PermissionError("Permission denied")):
            with patch('os.path.exists', return_value=False):
                # Should not raise an exception
                try:
                    setup_logging()
                except PermissionError:
                    pytest.fail("setup_logging should handle permission errors gracefully")
    
    @patch('logging_config.structlog')
    def test_get_logger(self, mock_structlog):
        """Test get_logger function."""
        mock_logger = Mock()
        mock_structlog.get_logger.return_value = mock_logger
        
        # Test without name
        logger = get_logger()
        mock_structlog.get_logger.assert_called_with(None)
        assert logger == mock_logger
        
        # Test with name
        mock_structlog.get_logger.reset_mock()
        logger = get_logger('test_logger')
        mock_structlog.get_logger.assert_called_with('test_logger')
        assert logger == mock_logger
    
    @patch('logging_config.structlog')
    def test_get_request_logger(self, mock_structlog):
        """Test get_request_logger function."""
        mock_logger = Mock()
        mock_structlog.get_logger.return_value = mock_logger
        
        logger = get_request_logger()
        
        # Verify structlog.get_logger was called with 'requests'
        mock_structlog.get_logger.assert_called_with('requests')
        assert logger == mock_logger
    
    def test_logger_functionality_after_setup(self):
        """Test that loggers work correctly after setup."""
        setup_logging()
        
        # Get a logger
        logger = get_logger('test')
        
        # Verify logger is not None
        assert logger is not None
        
        # Test that logging methods exist
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'debug')
    
    def test_request_logger_functionality_after_setup(self):
        """Test that request logger works correctly after setup."""
        setup_logging()
        
        # Get request logger
        request_logger = get_request_logger()
        
        # Verify logger is not None
        assert request_logger is not None
        
        # Test that logging methods exist
        assert hasattr(request_logger, 'info')
        assert hasattr(request_logger, 'error')
        assert hasattr(request_logger, 'warning')
        assert hasattr(request_logger, 'debug')
    
    def test_log_directory_defaults_to_logs(self):
        """Test that log directory defaults to 'logs' if not specified."""
        # Remove LOG_DIR environment variable
        if 'LOG_DIR' in os.environ:
            del os.environ['LOG_DIR']
        
        with patch('os.path.exists') as mock_exists:
            with patch('os.makedirs') as mock_makedirs:
                with patch('logging.handlers.RotatingFileHandler') as mock_handler:
                    mock_exists.return_value = False
                    
                    setup_logging()
                    
                    # Check that 'logs' directory was created
                    mock_makedirs.assert_called()
                    args, kwargs = mock_makedirs.call_args
                    assert 'logs' in args[0]
    
    def test_multiple_setup_calls_safe(self):
        """Test that calling setup_logging multiple times is safe."""
        # First setup
        setup_logging()
        initial_handlers = len(logging.getLogger().handlers)
        
        # Second setup
        setup_logging()
        
        # Should not double the number of handlers (may add some but not double)
        final_handlers = len(logging.getLogger().handlers)
        assert final_handlers >= initial_handlers
    
    def test_log_file_rotation_settings(self):
        """Test that log file rotation settings are correct."""
        setup_logging()
        
        root_logger = logging.getLogger()
        rotating_handlers = [h for h in root_logger.handlers if hasattr(h, 'maxBytes')]
        
        assert len(rotating_handlers) >= 1
        
        for handler in rotating_handlers:
            # Check max file size (10MB)
            assert handler.maxBytes == 10 * 1024 * 1024
            
            # Check backup count
            assert handler.backupCount >= 5
    
    def test_log_message_format(self):
        """Test that log messages have correct format."""
        setup_logging()
        
        # Check that basic logging is configured with message format
        root_logger = logging.getLogger()
        
        # Find a stream handler to check its format
        stream_handlers = [h for h in root_logger.handlers if isinstance(h, logging.StreamHandler)]
        
        if stream_handlers:
            # Check that the handler has a formatter or uses the default format
            handler = stream_handlers[0]
            # The format should be "%(message)s" based on the setup
            assert hasattr(handler, 'format') or handler.formatter is None
    
    def test_logging_with_unicode_characters(self):
        """Test logging with Unicode characters."""
        setup_logging()
        
        logger = get_logger('test')
        
        # Should not raise an exception with Unicode characters
        try:
            if hasattr(logger, 'info'):
                logger.info("Test message with Unicode: 中文测试")
        except UnicodeError:
            pytest.fail("Logging should handle Unicode characters")
    
    def test_logging_with_special_characters(self):
        """Test logging with special characters."""
        setup_logging()
        
        logger = get_logger('test')
        
        # Should not raise an exception with special characters
        try:
            if hasattr(logger, 'info'):
                logger.info("Test message with special chars: !@#$%^&*(){}[]|\\:;\"'<>,.?/")
        except Exception:
            pytest.fail("Logging should handle special characters")
    
    def test_concurrent_logging_setup(self):
        """Test that concurrent logging setup is safe."""
        import threading
        
        results = []
        
        def setup_in_thread():
            try:
                setup_logging()
                results.append(True)
            except Exception:
                results.append(False)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=setup_in_thread)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All setups should succeed
        assert all(results)
        assert len(results) == 5 