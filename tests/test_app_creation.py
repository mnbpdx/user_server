import pytest
import os
from flask import Flask
from unittest.mock import patch, MagicMock
from app import create_app, config_setup, setup_database, setup_rate_limiting, setup_api_documentation


class TestAppCreation:
    def test_create_app_returns_flask_instance(self):
        """Test that create_app returns a Flask application instance."""
        app = create_app()
        assert app is not None
        assert hasattr(app, 'config')
        assert hasattr(app, 'route')

    def test_create_app_configures_testing_environment(self):
        """Test that create_app properly configures for testing environment."""
        with patch.dict(os.environ, {'FLASK_ENV': 'testing'}):
            app = create_app()
            assert app.config['TESTING'] is True
            assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'

    def test_create_app_configures_development_environment(self):
        """Test that create_app properly configures for development environment."""
        with patch.dict(os.environ, {'FLASK_ENV': 'development'}):
            app = create_app()
            assert app.config['DEBUG'] is True

    def test_create_app_has_health_endpoint(self):
        """Test that the health endpoint is registered."""
        app = create_app()
        with app.test_client() as client:
            response = client.get('/health')
            assert response.status_code == 200
            assert response.data.decode() == 'healthy, thank you!'


class TestConfigSetup:
    def test_config_setup_default_environment(self):
        """Test config_setup with default environment."""
        app = create_app()
        config_setup(app)
        # In testing environment, DEBUG should be False
        assert app.config.get('DEBUG') is False

    def test_config_setup_with_environment_variable(self):
        """Test config_setup respects FLASK_ENV environment variable."""
        app = create_app()
        with patch.dict(os.environ, {'FLASK_ENV': 'production'}):
            config_setup(app)
            assert app.config.get('DEBUG') is False

    def test_config_setup_with_custom_secret_key(self):
        """Test config_setup with custom secret key."""
        app = create_app()
        with patch.dict(os.environ, {'SECRET_KEY': 'custom-secret'}):
            config_setup(app)
            assert app.config['SECRET_KEY'] == 'custom-secret'


class TestDatabaseSetup:
    @patch('app.db')
    @patch('app.migrate')
    def test_setup_database_initializes_components(self, mock_migrate, mock_db):
        """Test that setup_database initializes database and migrate."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        setup_database(app)
        
        mock_db.init_app.assert_called_once_with(app)
        mock_migrate.init_app.assert_called_once_with(app, mock_db)

    def test_setup_database_with_real_app(self):
        """Test setup_database with real Flask app."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        # This should not raise any exceptions
        setup_database(app)
        assert hasattr(app, 'config')


class TestRateLimitingSetup:
    @patch('app.limiter')
    def test_setup_rate_limiting_initializes_limiter(self, mock_limiter):
        """Test that setup_rate_limiting initializes the limiter."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['RATELIMIT_ENABLED'] = True
        setup_rate_limiting(app)
        
        mock_limiter.init_app.assert_called_once_with(app)
        assert app.config['RATELIMIT_STORAGE_URI'] == 'redis://redis:6379'
        assert app.config['RATELIMIT_HEADERS_ENABLED'] is True

    def test_setup_rate_limiting_with_custom_storage(self):
        """Test setup_rate_limiting with custom storage URI."""
        app = create_app()
        app.config['RATELIMIT_STORAGE_URI'] = 'redis://custom:6379'
        
        setup_rate_limiting(app)
        assert app.config['RATELIMIT_STORAGE_URI'] == 'redis://custom:6379'


class TestApiDocumentationSetup:
    @patch('app.api')
    def test_setup_api_documentation_initializes_api(self, mock_api):
        """Test that setup_api_documentation initializes the API."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        setup_api_documentation(app)
        
        mock_api.init_app.assert_called_once_with(app)

    def test_setup_api_documentation_with_real_app(self):
        """Test setup_api_documentation with real Flask app."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        # This should not raise any exceptions
        setup_api_documentation(app)
        assert hasattr(app, 'config')


class TestAppIntegration:
    def test_full_app_creation_integration(self):
        """Test that full app creation works without errors."""
        app = create_app()
        
        # Test that app is properly configured
        assert app is not None
        assert hasattr(app, 'config')
        
        # Test that health endpoint works
        with app.test_client() as client:
            response = client.get('/health')
            assert response.status_code == 200

    def test_app_has_all_expected_config(self):
        """Test that the app has all expected configuration."""
        app = create_app()
        
        # Database config
        assert 'SQLALCHEMY_DATABASE_URI' in app.config
        assert 'SQLALCHEMY_TRACK_MODIFICATIONS' in app.config
        
        # Rate limiting config
        assert 'RATELIMIT_STORAGE_URI' in app.config
        assert 'RATELIMIT_HEADERS_ENABLED' in app.config
        
        # Logging config
        assert 'REQUEST_LOGGING_ENABLED' in app.config

    def test_app_blueprints_registered(self):
        """Test that blueprints are properly registered."""
        app = create_app()
        
        # Check that users blueprint is registered
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        assert 'users' in blueprint_names 