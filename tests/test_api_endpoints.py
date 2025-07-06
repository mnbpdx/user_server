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
        """Test creating a user with valid data returns 201 Created."""
        response = client.post('/api/users', json=sample_user_data)
        
        assert response.status_code == 201
        
        data = response.get_json()
        assert 'id' in data
        assert data['username'] == sample_user_data['username']
        assert data['email'] == sample_user_data['email']
        assert data['age'] == sample_user_data['age']
        assert data['role'] == sample_user_data['role']
        
        # Verify user was created in database
        user_id = data['id']
        get_response = client.get(f'/api/users/{user_id}')
        assert get_response.status_code == 200
        get_data = get_response.get_json()
        assert get_data == data
    
    def test_create_user_missing_fields(self, client):
        """Test creating a user with missing required fields returns 400 Bad Request."""
        incomplete_data = {
            'username': 'testuser',
            'email': 'test@example.com'
            # Missing age and role
        }
        
        response = client.post('/api/users', json=incomplete_data)
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert data['error'] == 'Validation Error'
        assert data['code'] == 'VALIDATION_ERROR'
        assert 'Field required' in data['message']
    
    def test_create_user_invalid_data_types(self, client):
        """Test creating a user with invalid data types returns 400 Bad Request."""
        invalid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'age': 'not_an_integer',  # Invalid type
            'role': 'admin'
        }
        
        response = client.post('/api/users', json=invalid_data)
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert data['error'] == 'Validation Error'
        assert data['code'] == 'VALIDATION_ERROR'
        assert 'Input should be a valid integer' in data['message']
    
    def test_create_user_no_json_body(self, client):
        """Test creating a user without JSON body returns 400 Bad Request."""
        response = client.post('/api/users')
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert data['error'] == 'Invalid JSON'
        assert data['code'] == 'INVALID_JSON'
        assert 'Request must have JSON content type' in data['message']
    
    def test_create_user_empty_json(self, client):
        """Test creating a user with empty JSON body returns 400 Bad Request."""
        empty_json = {}
        
        response = client.post('/api/users', json=empty_json)
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert data['error'] == 'Validation Error'
        assert data['code'] == 'VALIDATION_ERROR'
        assert 'Field required' in data['message']
    
    def test_create_user_username_empty(self, client):
        """Test creating a user with empty username returns 400 Bad Request."""
        invalid_data = {
            'username': '',
            'email': 'test@example.com',
            'age': 30,
            'role': 'admin'
        }
        
        response = client.post('/api/users', json=invalid_data)
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert data['error'] == 'Validation Error'
        assert data['code'] == 'VALIDATION_ERROR'
        assert 'String should have at least 3 characters' in data['message']
    
    def test_create_user_username_too_short(self, client):
        """Test creating a user with username too short returns 400 Bad Request."""
        invalid_data = {
            'username': 'ab',  # Too short
            'email': 'test@example.com',
            'age': 30,
            'role': 'admin'
        }
        
        response = client.post('/api/users', json=invalid_data)
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert data['error'] == 'Validation Error'
        assert data['code'] == 'VALIDATION_ERROR'
        assert 'String should have at least 3 characters' in data['message']
    
    def test_create_user_username_minimum_length(self, client):
        """Test creating a user with username at minimum length succeeds."""
        valid_data = {
            'username': 'abc',  # Minimum length
            'email': 'test@example.com',
            'age': 30,
            'role': 'admin'
        }
        
        response = client.post('/api/users', json=valid_data)
        assert response.status_code == 201
        
        data = response.get_json()
        assert 'id' in data
        assert data['username'] == 'abc'
        assert data['email'] == 'test@example.com'
        assert data['age'] == 30
        assert data['role'] == 'admin'
    
    def test_create_user_username_maximum_length(self, client):
        """Test creating a user with username at maximum length succeeds."""
        max_username = 'a' * 50  # Maximum length
        valid_data = {
            'username': max_username,
            'email': 'test@example.com',
            'age': 30,
            'role': 'admin'
        }
        
        response = client.post('/api/users', json=valid_data)
        assert response.status_code == 201
        
        data = response.get_json()
        assert 'id' in data
        assert data['username'] == max_username
        assert data['email'] == 'test@example.com'
        assert data['age'] == 30
        assert data['role'] == 'admin'
    
    def test_create_user_username_too_long(self, client):
        """Test creating a user with username too long returns 400 Bad Request."""
        long_username = 'a' * 51  # Too long
        invalid_data = {
            'username': long_username,
            'email': 'test@example.com',
            'age': 30,
            'role': 'admin'
        }
        
        response = client.post('/api/users', json=invalid_data)
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert data['error'] == 'Validation Error'
        assert data['code'] == 'VALIDATION_ERROR'
        assert 'String should have at most 50 characters' in data['message']
    
    def test_create_user_email_maximum_length(self, client):
        """Test creating a user with email at maximum length succeeds."""
        max_email = 'a' * 90 + '@email.com'  # Maximum length (100 chars)
        valid_data = {
            'username': 'testuser',
            'email': max_email,
            'age': 30,
            'role': 'admin'
        }
        
        response = client.post('/api/users', json=valid_data)
        assert response.status_code == 201
        
        data = response.get_json()
        assert 'id' in data
        assert data['username'] == 'testuser'
        assert data['email'] == max_email
        assert data['age'] == 30
        assert data['role'] == 'admin'
    
    def test_create_user_email_too_long(self, client):
        """Test creating a user with email too long returns 400 Bad Request."""
        long_email = 'a' * 91 + '@email.com'  # Too long (101 chars)
        invalid_data = {
            'username': 'testuser',
            'email': long_email,
            'age': 30,
            'role': 'admin'
        }
        
        response = client.post('/api/users', json=invalid_data)
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert data['error'] == 'Validation Error'
        assert data['code'] == 'VALIDATION_ERROR'
        assert 'String should have at most 100 characters' in data['message']
    
    def test_create_user_role_maximum_length(self, client):
        """Test creating a user with role at maximum length succeeds."""
        max_role = 'a' * 20  # Maximum length
        valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'age': 30,
            'role': max_role
        }
        
        response = client.post('/api/users', json=valid_data)
        assert response.status_code == 201
        
        data = response.get_json()
        assert 'id' in data
        assert data['username'] == 'testuser'
        assert data['email'] == 'test@example.com'
        assert data['age'] == 30
        assert data['role'] == max_role
    
    def test_create_user_role_too_long(self, client):
        """Test creating a user with role too long returns 400 Bad Request."""
        long_role = 'a' * 21  # Too long
        invalid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'age': 30,
            'role': long_role
        }
        
        response = client.post('/api/users', json=invalid_data)
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert data['error'] == 'Validation Error'
        assert data['code'] == 'VALIDATION_ERROR'
        assert 'String should have at most 20 characters' in data['message']


class TestUpdateUser:
    """Test the PATCH /api/users/{id} endpoint."""
    
    def test_update_user_success_full_update(self, client, create_user):
        """Test updating a user with all fields returns 200 OK."""
        user = create_user(username='testuser', email='test@example.com', age=30, role='admin')
        
        update_data = {
            'username': 'updateduser',
            'email': 'updated@example.com',
            'age': 35,
            'role': 'user'
        }
        
        response = client.patch(f'/api/users/{user["id"]}', json=update_data)
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['id'] == user['id']
        assert data['username'] == 'updateduser'
        assert data['email'] == 'updated@example.com'
        assert data['age'] == 35
        assert data['role'] == 'user'
    
    def test_update_user_success_partial_update(self, client, create_user):
        """Test updating a user with only some fields returns 200 OK."""
        user = create_user(username='testuser', email='test@example.com', age=30, role='admin')
        
        update_data = {
            'username': 'updateduser',
            'age': 35
        }
        
        response = client.patch(f'/api/users/{user["id"]}', json=update_data)
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['id'] == user['id']
        assert data['username'] == 'updateduser'
        assert data['email'] == 'test@example.com'  # Unchanged
        assert data['age'] == 35
        assert data['role'] == 'admin'  # Unchanged
    
    def test_update_user_success_single_field(self, client, create_user):
        """Test updating a user with a single field returns 200 OK."""
        user = create_user(username='testuser', email='test@example.com', age=30, role='admin')
        
        update_data = {
            'age': 35
        }
        
        response = client.patch(f'/api/users/{user["id"]}', json=update_data)
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['id'] == user['id']
        assert data['username'] == 'testuser'  # Unchanged
        assert data['email'] == 'test@example.com'  # Unchanged
        assert data['age'] == 35
        assert data['role'] == 'admin'  # Unchanged
    
    def test_update_user_not_found(self, client):
        """Test updating a user that doesn't exist returns 404 Not Found."""
        update_data = {
            'username': 'updateduser'
        }
        
        response = client.patch('/api/users/999', json=update_data)
        assert response.status_code == 404
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert data['error'] == 'Resource Not Found'
        assert data['code'] == 'RESOURCE_NOT_FOUND'
        assert 'User not found with id: 999' in data['message']
    
    def test_update_user_no_json_body(self, client, create_user):
        """Test updating a user without JSON body returns 400 Bad Request."""
        user = create_user(username='testuser', email='test@example.com', age=30, role='admin')
        
        response = client.patch(f'/api/users/{user["id"]}')
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert data['error'] == 'Invalid JSON'
        assert data['code'] == 'INVALID_JSON'
        assert 'Request must have JSON content type' in data['message']
    
    def test_update_user_empty_json(self, client, create_user):
        """Test updating a user with empty JSON body returns 400 Bad Request."""
        user = create_user(username='testuser', email='test@example.com', age=30, role='admin')
        
        empty_json = {}
        
        response = client.patch(f'/api/users/{user["id"]}', json=empty_json)
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert data['error'] == 'Invalid JSON'
        assert data['code'] == 'INVALID_JSON'
        assert 'At least one field must be provided for update' in data['message']
    
    def test_update_user_invalid_data_types(self, client, create_user):
        """Test updating a user with invalid data types returns 400 Bad Request."""
        user = create_user(username='testuser', email='test@example.com', age=30, role='admin')
        
        invalid_data = {
            'age': 'not_an_integer'  # Invalid type
        }
        
        response = client.patch(f'/api/users/{user["id"]}', json=invalid_data)
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert data['error'] == 'Validation Error'
        assert data['code'] == 'VALIDATION_ERROR'
        assert 'Input should be a valid integer' in data['message']
    
    def test_update_user_username_too_short(self, client, create_user):
        """Test updating a user with username too short returns 400 Bad Request."""
        user = create_user(username='testuser', email='test@example.com', age=30, role='admin')
        
        invalid_data = {
            'username': 'ab'  # Too short
        }
        
        response = client.patch(f'/api/users/{user["id"]}', json=invalid_data)
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert data['error'] == 'Validation Error'
        assert data['code'] == 'VALIDATION_ERROR'
        assert 'String should have at least 3 characters' in data['message']
    
    def test_update_user_username_too_long(self, client, create_user):
        """Test updating a user with username too long returns 400 Bad Request."""
        user = create_user(username='testuser', email='test@example.com', age=30, role='admin')
        
        invalid_data = {
            'username': 'a' * 51  # Too long
        }
        
        response = client.patch(f'/api/users/{user["id"]}', json=invalid_data)
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert data['error'] == 'Validation Error'
        assert data['code'] == 'VALIDATION_ERROR'
        assert 'String should have at most 50 characters' in data['message']
    
    def test_update_user_email_too_long(self, client, create_user):
        """Test updating a user with email too long returns 400 Bad Request."""
        user = create_user(username='testuser', email='test@example.com', age=30, role='admin')
        
        invalid_data = {
            'email': 'a' * 91 + '@email.com'  # Too long (101 chars)
        }
        
        response = client.patch(f'/api/users/{user["id"]}', json=invalid_data)
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert data['error'] == 'Validation Error'
        assert data['code'] == 'VALIDATION_ERROR'
        assert 'String should have at most 100 characters' in data['message']
    
    def test_update_user_role_too_long(self, client, create_user):
        """Test updating a user with role too long returns 400 Bad Request."""
        user = create_user(username='testuser', email='test@example.com', age=30, role='admin')
        
        invalid_data = {
            'role': 'a' * 21  # Too long
        }
        
        response = client.patch(f'/api/users/{user["id"]}', json=invalid_data)
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert data['error'] == 'Validation Error'
        assert data['code'] == 'VALIDATION_ERROR'
        assert 'String should have at most 20 characters' in data['message']
    
    def test_update_user_username_already_exists(self, client, create_user):
        """Test updating a user with an already existing username returns 409 Conflict."""
        user1 = create_user(username='user1', email='user1@example.com', age=30, role='admin')
        user2 = create_user(username='user2', email='user2@example.com', age=25, role='user')
        
        update_data = {
            'username': 'user1'  # Already exists
        }
        
        response = client.patch(f'/api/users/{user2["id"]}', json=update_data)
        assert response.status_code == 409
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert data['error'] == 'Resource Already Exists'
        assert data['code'] == 'RESOURCE_ALREADY_EXISTS'
        assert 'User already exists with username: user1' in data['message']
    
    def test_update_user_email_already_exists(self, client, create_user):
        """Test updating a user with an already existing email returns 409 Conflict."""
        user1 = create_user(username='user1', email='user1@example.com', age=30, role='admin')
        user2 = create_user(username='user2', email='user2@example.com', age=25, role='user')
        
        update_data = {
            'email': 'user1@example.com'  # Already exists
        }
        
        response = client.patch(f'/api/users/{user2["id"]}', json=update_data)
        assert response.status_code == 409
        
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'message' in data
        assert data['error'] == 'Resource Already Exists'
        assert data['code'] == 'RESOURCE_ALREADY_EXISTS'
        assert 'User already exists with email: user1@example.com' in data['message']
    
    def test_update_user_same_username_no_conflict(self, client, create_user):
        """Test updating a user with their own username succeeds."""
        user = create_user(username='testuser', email='test@example.com', age=30, role='admin')
        
        update_data = {
            'username': 'testuser',  # Same as current username
            'age': 35
        }
        
        response = client.patch(f'/api/users/{user["id"]}', json=update_data)
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['id'] == user['id']
        assert data['username'] == 'testuser'
        assert data['email'] == 'test@example.com'
        assert data['age'] == 35
        assert data['role'] == 'admin'
    
    def test_update_user_same_email_no_conflict(self, client, create_user):
        """Test updating a user with their own email succeeds."""
        user = create_user(username='testuser', email='test@example.com', age=30, role='admin')
        
        update_data = {
            'email': 'test@example.com',  # Same as current email
            'age': 35
        }
        
        response = client.patch(f'/api/users/{user["id"]}', json=update_data)
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['id'] == user['id']
        assert data['username'] == 'testuser'
        assert data['email'] == 'test@example.com'
        assert data['age'] == 35
        assert data['role'] == 'admin'
    
    def test_update_user_persisted_in_database(self, client, create_user):
        """Test that updated user data is persisted in the database."""
        user = create_user(username='testuser', email='test@example.com', age=30, role='admin')
        
        update_data = {
            'username': 'updateduser',
            'age': 35
        }
        
        # Update the user
        response = client.patch(f'/api/users/{user["id"]}', json=update_data)
        assert response.status_code == 200
        
        # Verify the update is persisted by fetching the user again
        get_response = client.get(f'/api/users/{user["id"]}')
        assert get_response.status_code == 200
        
        data = get_response.get_json()
        assert data['id'] == user['id']
        assert data['username'] == 'updateduser'
        assert data['email'] == 'test@example.com'
        assert data['age'] == 35
        assert data['role'] == 'admin'
    
    def test_update_user_visible_in_all_users_list(self, client, create_user):
        """Test that updated user is visible in get all users response."""
        user = create_user(username='testuser', email='test@example.com', age=30, role='admin')
        
        update_data = {
            'username': 'updateduser',
            'role': 'user'
        }
        
        # Update the user
        response = client.patch(f'/api/users/{user["id"]}', json=update_data)
        assert response.status_code == 200
        
        # Verify the update is visible in all users list
        get_all_response = client.get('/api/users')
        assert get_all_response.status_code == 200
        
        data = get_all_response.get_json()
        assert len(data['users']) == 1
        
        updated_user = data['users'][0]
        assert updated_user['id'] == user['id']
        assert updated_user['username'] == 'updateduser'
        assert updated_user['email'] == 'test@example.com'
        assert updated_user['age'] == 30
        assert updated_user['role'] == 'user'