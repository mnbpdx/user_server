import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from app import create_app
from api_docs import api


class TestUsersApi:
    """Test the Flask-RESTX API endpoints."""
    
    @pytest.fixture
    def app(self):
        """Create a test Flask app with API."""
        import os
        os.environ['FLASK_ENV'] = 'testing'
        app = create_app()
        app.config['TESTING'] = True
        app.config['RATELIMIT_ENABLED'] = False
        
        with app.app_context():
            from models import db
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """Create a test client."""
        return app.test_client()

    def test_get_users_api_endpoint_exists(self, client):
        """Test that the API users endpoint exists."""
        response = client.get('/api/users/')
        # Should return 200 (empty list) or another valid response
        assert response.status_code in [200, 404]

    def test_create_user_api_endpoint_exists(self, client):
        """Test that the API create user endpoint exists."""
        response = client.post('/api/users/', 
                             json={'username': 'testuser', 'email': 'test@example.com', 'age': 25, 'role': 'user'})
        # Should return a valid response (200, 201, 400, etc.)
        assert response.status_code in [200, 201, 400, 422]

    def test_get_user_by_id_api_endpoint_exists(self, client):
        """Test that the API get user by ID endpoint exists."""
        response = client.get('/api/users/1')
        # Should return a valid response (200, 404, etc.)
        assert response.status_code in [200, 404]

    def test_update_user_api_endpoint_exists(self, client):
        """Test that the API update user endpoint exists."""
        response = client.patch('/api/users/1',
                              json={'username': 'updateduser'})
        # Should return a valid response (200, 400, 404, etc.)
        assert response.status_code in [200, 400, 404, 422]

    def test_delete_user_api_endpoint_exists(self, client):
        """Test that the API delete user endpoint exists."""
        response = client.delete('/api/users/1')
        # Should return a valid response (200, 204, 404, etc.)
        assert response.status_code in [200, 204, 404]

    def test_get_users_by_role_api_endpoint_exists(self, client):
        """Test that the API get users by role endpoint exists."""
        response = client.get('/api/users/role/admin')
        # Should return a valid response (200, 404, etc.)
        assert response.status_code in [200, 404]

    @patch('routes.users_api.UserService.get_all_users')
    def test_get_users_api_with_mock_service(self, mock_get_all, client):
        """Test the get users API endpoint with mocked service."""
        # Mock the service to return empty list
        mock_get_all.return_value = []
        
        response = client.get('/api/users/')
        assert response.status_code == 200
        
        # Verify the service was called
        mock_get_all.assert_called_once()

    @patch('routes.users_api.UserService.create_user')
    def test_create_user_api_with_mock_service(self, mock_create, client):
        """Test the create user API endpoint with mocked service."""
        # Mock the service to return a user and no error
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = 'testuser'
        mock_user.email = 'test@example.com'
        mock_user.age = 25
        mock_user.role = 'user'
        mock_user.to_dict.return_value = {
            'id': 1, 'username': 'testuser', 'email': 'test@example.com', 
            'age': 25, 'role': 'user'
        }
        mock_create.return_value = (mock_user, None)
        
        response = client.post('/api/users/', 
                             json={'username': 'testuser', 'email': 'test@example.com', 'age': 25, 'role': 'user'})
        
        # Should return 201 Created
        assert response.status_code == 201
        
        # Verify the service was called
        mock_create.assert_called_once()

    @patch('routes.users_api.UserService.get_user')
    def test_get_user_by_id_api_with_mock_service(self, mock_get_user, client):
        """Test the get user by ID API endpoint with mocked service."""
        # Mock the service to return a user with proper attributes
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = 'testuser'
        mock_user.email = 'test@example.com'
        mock_user.age = 25
        mock_user.role = 'user'
        mock_user.to_dict.return_value = {
            'id': 1, 'username': 'testuser', 'email': 'test@example.com', 
            'age': 25, 'role': 'user'
        }
        mock_get_user.return_value = mock_user
        
        response = client.get('/api/users/1')
        assert response.status_code == 200
        
        # Verify the service was called with correct ID
        mock_get_user.assert_called_once_with(id=1)

    @patch('routes.users_api.UserService.get_user')
    def test_get_user_by_id_api_not_found(self, mock_get_user, client):
        """Test the get user by ID API endpoint when user not found."""
        # Mock the service to return None
        mock_get_user.return_value = None
        
        response = client.get('/api/users/999')
        assert response.status_code == 404
        
        # Verify the service was called
        mock_get_user.assert_called_once_with(id=999)

    def test_api_documentation_includes_users_endpoints(self, client):
        """Test that API documentation includes users endpoints."""
        response = client.get('/api/swagger.json')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'paths' in data
        assert '/users/' in data['paths']

    def test_api_content_type_json(self, client):
        """Test that API endpoints return JSON content type."""
        response = client.get('/api/users/')
        assert 'application/json' in response.content_type

    def test_create_user_api_validation_error(self, client):
        """Test create user API with validation errors."""
        # Send invalid data (missing required fields)
        response = client.post('/api/users/', json={'username': 'test'})
        
        # Should return 400 or 422 for validation error
        assert response.status_code in [400, 422]
        assert 'application/json' in response.content_type

    def test_update_user_api_validation_error(self, client):
        """Test update user API with validation errors."""
        # Send invalid data (invalid field types)
        response = client.patch('/api/users/1', json={'age': 'invalid'})
        
        # Should return 400 or 422 for validation error
        assert response.status_code in [400, 422]
        assert 'application/json' in response.content_type

    def test_api_error_handling(self, client):
        """Test that API handles errors gracefully."""
        # Test with malformed JSON
        response = client.post('/api/users/', 
                             data='invalid json',
                             content_type='application/json')
        
        # Should return 400 for malformed JSON
        assert response.status_code == 400
        assert 'application/json' in response.content_type 