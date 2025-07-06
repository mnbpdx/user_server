import pytest
from flask import Flask
from api_docs import api, users_ns, user_model, user_create_model, user_update_model, user_response_model, error_model


class TestApiDocsSetup:
    def test_api_instance_creation(self):
        """Test that API instance is created with correct configuration."""
        assert api is not None
        assert api.title == 'User Server API'
        assert api.version == '1.0'
        assert api.description == 'A simple user management API with Flask'
        assert api._doc == '/docs/'
        assert api.prefix == '/api'

    def test_users_namespace_exists(self):
        """Test that users namespace is created."""
        assert users_ns is not None
        assert users_ns.name == 'users'
        assert users_ns.description == 'User operations'

    def test_api_initialization_with_app(self):
        """Test that API can be initialized with Flask app."""
        app = Flask(__name__)
        api.init_app(app)
        
        # Check that API is properly bound to app
        assert hasattr(app, 'extensions')
        assert 'restx' in app.extensions


class TestApiModels:
    def test_user_model_definition(self):
        """Test that user model is properly defined."""
        assert user_model is not None
        assert user_model.name == 'User'
        
        # Check that all required fields are present
        expected_fields = ['id', 'username', 'email', 'age', 'role']
        for field in expected_fields:
            assert field in user_model
            
    def test_user_create_model_definition(self):
        """Test that user create model is properly defined."""
        assert user_create_model is not None
        assert user_create_model.name == 'UserCreate'
        
        # Check that all required fields are present (no id field)
        expected_fields = ['username', 'email', 'age', 'role']
        for field in expected_fields:
            assert field in user_create_model
            
        # Ensure id field is not present
        assert 'id' not in user_create_model

    def test_user_update_model_definition(self):
        """Test that user update model is properly defined."""
        assert user_update_model is not None
        assert user_update_model.name == 'UserUpdate'
        
        # Check that all optional fields are present
        expected_fields = ['username', 'email', 'age', 'role']
        for field in expected_fields:
            assert field in user_update_model

    def test_user_response_model_definition(self):
        """Test that user response model is properly defined."""
        assert user_response_model is not None
        assert user_response_model.name == 'UserResponse'
        
        # Check that users field is present
        assert 'users' in user_response_model

    def test_error_model_definition(self):
        """Test that error model is properly defined."""
        assert error_model is not None
        assert error_model.name == 'Error'
        
        # Check that error fields are present
        expected_fields = ['error', 'code', 'details']
        for field in expected_fields:
            assert field in error_model


class TestApiIntegration:
    def test_api_with_flask_app(self):
        """Test API integration with Flask app."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        # Initialize API with app
        api.init_app(app)
        
        # Test that documentation endpoint is accessible
        with app.test_client() as client:
            response = client.get('/docs/')
            assert response.status_code == 200
            
    def test_api_namespace_registration(self):
        """Test that namespace is properly registered with API."""
        app = Flask(__name__)
        api.init_app(app)
        
        # Check that users namespace is registered
        namespace_names = [ns.name for ns in api.namespaces]
        assert 'users' in namespace_names

    def test_api_swagger_json(self):
        """Test that Swagger JSON is generated correctly."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        api.init_app(app)
        
        with app.test_client() as client:
            response = client.get('/api/swagger.json')
            assert response.status_code == 200
            assert response.content_type == 'application/json'
            
            # Check that response contains expected API information
            data = response.get_json()
            assert data['info']['title'] == 'User Server API'
            assert data['info']['version'] == '1.0' 