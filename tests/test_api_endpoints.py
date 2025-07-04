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
        assert 'code' in data
        assert 'message' in data
        assert data['error'] == 'Resource Not Found'
        assert data['code'] == 'RESOURCE_NOT_FOUND'
        assert 'User not found with id: 999' in data['message']


class TestDeleteUser:
    """Test the DELETE /api/users/{id} endpoint."""
    
    def test_delete_user_success(self, client, create_user):
        """Test deleting a user that exists returns 204 No Content."""
        user = create_user(username='testuser', email='test@example.com', age=30, role='admin')
        
        response = client.delete(f'/api/users/{user["id"]}')
        assert response.status_code == 204
        assert response.get_data() == b''
    
    def test_delete_user_not_found(self, client):
        """Test deleting a user that doesn't exist returns 404 Not Found."""
        response = client.delete('/api/users/999')
        assert response.status_code == 404
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert data['error'] == 'Resource Not Found'
        assert data['code'] == 'RESOURCE_NOT_FOUND'
        assert 'User not found with id: 999' in data['message']
    
    def test_delete_user_removes_from_database(self, client, create_user):
        """Test that deleted user is completely removed from database."""
        user = create_user(username='testuser', email='test@example.com', age=30, role='admin')
        user_id = user['id']
        
        # Verify user exists before deletion
        response = client.get(f'/api/users/{user_id}')
        assert response.status_code == 200
        
        # Delete the user
        response = client.delete(f'/api/users/{user_id}')
        assert response.status_code == 204
        
        # Verify user no longer exists
        response = client.get(f'/api/users/{user_id}')
        assert response.status_code == 404
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert data['error'] == 'Resource Not Found'
        assert data['code'] == 'RESOURCE_NOT_FOUND'
        assert f'User not found with id: {user_id}' in data['message']
    
    def test_delete_user_not_in_all_users_list(self, client, create_user):
        """Test that deleted user is not included in get all users response."""
        user = create_user(username='testuser', email='test@example.com', age=30, role='admin')
        user_id = user['id']
        
        # Verify user is in all users list before deletion
        response = client.get('/api/users')
        assert response.status_code == 200
        data = response.get_json()
        user_ids = [u['id'] for u in data['users']]
        assert user_id in user_ids
        assert len(data['users']) == 1
        
        # Delete the user
        response = client.delete(f'/api/users/{user_id}')
        assert response.status_code == 204
        
        # Verify user is not in all users list after deletion
        response = client.get('/api/users')
        assert response.status_code == 200
        data = response.get_json()
        user_ids = [u['id'] for u in data['users']]
        assert user_id not in user_ids
        assert len(data['users']) == 0
    
    def test_delete_user_multiple_users(self, client, create_users, sample_users_data):
        """Test deleting one user doesn't affect other users."""
        create_users(sample_users_data)
        
        # Get all users before deletion
        response = client.get('/api/users')
        assert response.status_code == 200
        data = response.get_json()
        initial_count = len(data['users'])
        assert initial_count == 3
        
        # Get the first user ID
        user_id_to_delete = data['users'][0]['id']
        
        # Delete one user
        response = client.delete(f'/api/users/{user_id_to_delete}')
        assert response.status_code == 204
        
        # Verify other users still exist
        response = client.get('/api/users')
        assert response.status_code == 200
        data = response.get_json()
        remaining_count = len(data['users'])
        assert remaining_count == initial_count - 1
        
        # Verify the deleted user is not in the list
        remaining_user_ids = [u['id'] for u in data['users']]
        assert user_id_to_delete not in remaining_user_ids


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
        assert 'code' in data
        assert 'message' in data
        assert 'details' in data
        assert data['error'] == 'Validation Error'
        assert data['code'] == 'VALIDATION_ERROR'
        assert data['message'] == 'Request validation failed'
        assert len(data['details']) == 2  # Missing age and role
    
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
        assert 'code' in data
        assert 'message' in data
        assert 'details' in data
        assert data['error'] == 'Validation Error'
        assert data['code'] == 'VALIDATION_ERROR'
        assert data['message'] == 'Request validation failed'
        assert len(data['details']) == 1  # Invalid age type
    
    def test_create_user_no_json_body(self, client):
        """Test creating a user without JSON body."""
        response = client.post('/api/users', 
                             content_type='application/json')
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert data['error'] == 'Invalid JSON'
        assert data['code'] == 'INVALID_JSON'
        assert 'Request body must be valid JSON' in data['message']
    
    def test_create_user_empty_json(self, client):
        """Test creating a user with empty JSON body."""
        response = client.post('/api/users', 
                             data='{}',
                             content_type='application/json')
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert 'details' in data
        assert data['error'] == 'Validation Error'
        assert data['code'] == 'VALIDATION_ERROR'
        assert data['message'] == 'Request validation failed'
        assert len(data['details']) == 4  # Missing username, email, age, role
    
    def test_create_user_username_empty(self, client):
        """Test creating a user with empty username."""
        invalid_data = {
            'username': '',
            'email': 'test@example.com',
            'age': 25,
            'role': 'admin'
        }
        
        response = client.post('/api/users', 
                             data=json.dumps(invalid_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert 'details' in data
        assert data['error'] == 'Validation Error'
        assert data['code'] == 'VALIDATION_ERROR'
        assert data['message'] == 'Request validation failed'
        assert any('username' in detail['field'] and 'at least 3 characters' in detail['message'] for detail in data['details'])
    
    def test_create_user_username_too_short(self, client):
        """Test creating a user with username shorter than 3 characters."""
        invalid_data = {
            'username': 'ab',  # 2 characters
            'email': 'test@example.com',
            'age': 25,
            'role': 'admin'
        }
        
        response = client.post('/api/users', 
                             data=json.dumps(invalid_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert 'details' in data
        assert data['error'] == 'Validation Error'
        assert data['code'] == 'VALIDATION_ERROR'
        assert data['message'] == 'Request validation failed'
        assert any('username' in detail['field'] and 'at least 3 characters' in detail['message'] for detail in data['details'])
    
    def test_create_user_username_minimum_length(self, client):
        """Test creating a user with username of minimum valid length (3 characters)."""
        valid_data = {
            'username': 'abc',  # 3 characters - minimum valid
            'email': 'test@example.com',
            'age': 25,
            'role': 'admin'
        }
        
        response = client.post('/api/users', 
                             data=json.dumps(valid_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        
        data = response.get_json()
        assert 'id' in data
        assert data['username'] == 'abc'
        assert data['email'] == 'test@example.com'
        assert data['age'] == 25
        assert data['role'] == 'admin'
    
    def test_create_user_username_maximum_length(self, client):
        """Test creating a user with username of maximum valid length (50 characters)."""
        valid_data = {
            'username': 'a' * 50,  # 50 characters - maximum valid
            'email': 'test@example.com',
            'age': 25,
            'role': 'admin'
        }
        
        response = client.post('/api/users', 
                             data=json.dumps(valid_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        
        data = response.get_json()
        assert 'id' in data
        assert data['username'] == 'a' * 50
        assert data['email'] == 'test@example.com'
        assert data['age'] == 25
        assert data['role'] == 'admin'
    
    def test_create_user_username_too_long(self, client):
        """Test creating a user with username longer than 50 characters."""
        invalid_data = {
            'username': 'a' * 51,  # 51 characters - too long
            'email': 'test@example.com',
            'age': 25,
            'role': 'admin'
        }
        
        response = client.post('/api/users', 
                             data=json.dumps(invalid_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert 'details' in data
        assert data['error'] == 'Validation Error'
        assert data['code'] == 'VALIDATION_ERROR'
        assert data['message'] == 'Request validation failed'
        assert any('username' in detail['field'] and 'at most 50 characters' in detail['message'] for detail in data['details'])
    
    def test_create_user_email_maximum_length(self, client):
        """Test creating a user with email of maximum valid length (100 characters)."""
        valid_data = {
            'username': 'testuser',
            'email': 'a' * 88 + '@example.com',  # 100 characters total
            'age': 25,
            'role': 'admin'
        }
        
        response = client.post('/api/users', 
                             data=json.dumps(valid_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        
        data = response.get_json()
        assert 'id' in data
        assert data['username'] == 'testuser'
        assert data['email'] == 'a' * 88 + '@example.com'
        assert data['age'] == 25
        assert data['role'] == 'admin'
    
    def test_create_user_email_too_long(self, client):
        """Test creating a user with email longer than 100 characters."""
        invalid_data = {
            'username': 'testuser',
            'email': 'a' * 89 + '@example.com',  # 101 characters total
            'age': 25,
            'role': 'admin'
        }
        
        response = client.post('/api/users', 
                             data=json.dumps(invalid_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert 'details' in data
        assert data['error'] == 'Validation Error'
        assert data['code'] == 'VALIDATION_ERROR'
        assert data['message'] == 'Request validation failed'
        assert any('email' in detail['field'] and 'at most 100 characters' in detail['message'] for detail in data['details'])
    
    def test_create_user_role_maximum_length(self, client):
        """Test creating a user with role of maximum valid length (20 characters)."""
        valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'age': 25,
            'role': 'a' * 20  # 20 characters - maximum valid
        }
        
        response = client.post('/api/users', 
                             data=json.dumps(valid_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        
        data = response.get_json()
        assert 'id' in data
        assert data['username'] == 'testuser'
        assert data['email'] == 'test@example.com'
        assert data['age'] == 25
        assert data['role'] == 'a' * 20
    
    def test_create_user_role_too_long(self, client):
        """Test creating a user with role longer than 20 characters."""
        invalid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'age': 25,
            'role': 'a' * 21  # 21 characters - too long
        }
        
        response = client.post('/api/users', 
                             data=json.dumps(invalid_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert 'details' in data
        assert data['error'] == 'Validation Error'
        assert data['code'] == 'VALIDATION_ERROR'
        assert data['message'] == 'Request validation failed'
        assert any('role' in detail['field'] and 'at most 20 characters' in detail['message'] for detail in data['details'])