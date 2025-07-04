import pytest
import json
from tests.fixtures import sample_user_data, sample_users_data, create_user, create_users


class TestHealthEndpoint:
    """Test the health check endpoint."""
    
    def test_health_check(self, client):
        """Test the health check endpoint returns the correct response."""
        response = client.get('/health')
        assert response.status_code == 200
        assert response.get_data(as_text=True) == 'healthy, thank you!'


class TestGetAllUsers:
    """Test the GET /api/users endpoint."""
    
    def test_get_all_users_empty(self, client):
        """Test getting all users when database is empty."""
        response = client.get('/api/users')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'users' in data
        assert data['users'] == []
    
    def test_get_all_users_with_data(self, client, sample_users_data, create_users):
        """Test getting all users when database has data."""
        create_users(sample_users_data)
        
        response = client.get('/api/users')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'users' in data
        assert len(data['users']) == 3
        
        # Check that each user has the required fields
        for user in data['users']:
            assert 'id' in user
            assert 'username' in user
            assert 'email' in user
            assert 'age' in user
            assert 'role' in user


class TestGetUsersByRole:
    """Test the GET /api/users/role/{role} endpoint."""
    
    def test_get_users_by_role_empty(self, client):
        """Test getting users by role when database is empty."""
        response = client.get('/api/users/role/admin')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'users' in data
        assert data['users'] == []
    
    def test_get_users_by_role_with_data(self, client, sample_users_data, create_users):
        """Test getting users by role when database has data."""
        create_users(sample_users_data)
        
        response = client.get('/api/users/role/admin')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'users' in data
        assert len(data['users']) == 1
        assert data['users'][0]['role'] == 'admin'
        assert data['users'][0]['username'] == 'alice'
    
    def test_get_users_by_role_no_matches(self, client, sample_users_data, create_users):
        """Test getting users by role when no users match."""
        create_users(sample_users_data)
        
        response = client.get('/api/users/role/nonexistent')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'users' in data
        assert data['users'] == []


class TestGetUserById:
    """Test the GET /api/users/{id} endpoint."""
    
    def test_get_user_by_id_success(self, client, create_user):
        """Test getting a user by ID when user exists."""
        user = create_user(username='testuser', email='test@example.com', age=30, role='admin')
        
        response = client.get(f'/api/users/{user["id"]}')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['id'] == user['id']
        assert data['username'] == 'testuser'
        assert data['email'] == 'test@example.com'
        assert data['age'] == 30
        assert data['role'] == 'admin'
    
    def test_get_user_by_id_not_found(self, client):
        """Test getting a user by ID when user doesn't exist."""
        response = client.get('/api/users/999')
        assert response.status_code == 404
        
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'User not found'


class TestCreateUser:
    """Test the POST /api/users endpoint."""
    
    def test_create_user_success(self, client, sample_user_data):
        """Test creating a user with valid data."""
        response = client.post('/api/users', 
                             data=json.dumps(sample_user_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        
        data = response.get_json()
        assert 'id' in data
        assert data['username'] == sample_user_data['username']
        assert data['email'] == sample_user_data['email']
        assert data['age'] == sample_user_data['age']
        assert data['role'] == sample_user_data['role']
    
    def test_create_user_missing_fields(self, client):
        """Test creating a user with missing required fields."""
        incomplete_data = {
            'username': 'testuser',
            'email': 'test@example.com'
            # Missing age and role
        }
        
        response = client.post('/api/users', 
                             data=json.dumps(incomplete_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'Request Pydantic validation failed' in data['error']
    
    def test_create_user_invalid_data_types(self, client):
        """Test creating a user with invalid data types."""
        invalid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'age': 'not_a_number',  # Should be int
            'role': 'admin'
        }
        
        response = client.post('/api/users', 
                             data=json.dumps(invalid_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'Request Pydantic validation failed' in data['error']
    
    def test_create_user_no_json_body(self, client):
        """Test creating a user without JSON body."""
        response = client.post('/api/users', 
                             content_type='application/json')
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
    
    def test_create_user_empty_json(self, client):
        """Test creating a user with empty JSON body."""
        response = client.post('/api/users', 
                             data='{}',
                             content_type='application/json')
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'Request Pydantic validation failed' in data['error']