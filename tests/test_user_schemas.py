import pytest
from pydantic import ValidationError
from schemas.user_schemas import UserSchema, UserCreateSchema, UserResponseSchema
from schemas.error_schemas import ErrorResponse, ErrorCode, FieldError, ErrorResponseBuilder


class TestUserCreateSchema:
    """Test the UserCreateSchema validation."""
    
    def test_valid_user_create_schema(self):
        """Test valid user creation data passes validation."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'age': 25,
            'role': 'admin'
        }
        
        schema = UserCreateSchema(**data)
        
        assert schema.username == 'testuser'
        assert schema.email == 'test@example.com'
        assert schema.age == 25
        assert schema.role == 'admin'
    
    def test_username_minimum_length(self):
        """Test username minimum length validation."""
        data = {
            'username': 'abc',  # exactly 3 characters
            'email': 'test@example.com',
            'age': 25,
            'role': 'admin'
        }
        
        schema = UserCreateSchema(**data)
        assert schema.username == 'abc'
    
    def test_username_maximum_length(self):
        """Test username maximum length validation."""
        data = {
            'username': 'a' * 50,  # exactly 50 characters
            'email': 'test@example.com',
            'age': 25,
            'role': 'admin'
        }
        
        schema = UserCreateSchema(**data)
        assert schema.username == 'a' * 50
    
    def test_username_too_short(self):
        """Test username too short validation error."""
        data = {
            'username': 'ab',  # only 2 characters
            'email': 'test@example.com',
            'age': 25,
            'role': 'admin'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreateSchema(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['type'] == 'string_too_short'
        assert errors[0]['loc'] == ('username',)
        assert 'at least 3 characters' in errors[0]['msg']
    
    def test_username_too_long(self):
        """Test username too long validation error."""
        data = {
            'username': 'a' * 51,  # 51 characters
            'email': 'test@example.com',
            'age': 25,
            'role': 'admin'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreateSchema(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['type'] == 'string_too_long'
        assert errors[0]['loc'] == ('username',)
        assert 'at most 50 characters' in errors[0]['msg']
    
    def test_email_maximum_length(self):
        """Test email maximum length validation."""
        # Create a valid email with exactly 100 characters
        local_part = 'a' * 84  # 84 characters
        domain_part = '@example.com'  # 12 characters
        long_email = local_part + domain_part  # 96 characters total
        
        data = {
            'username': 'testuser',
            'email': long_email,
            'age': 25,
            'role': 'admin'
        }
        
        schema = UserCreateSchema(**data)
        assert schema.email == long_email
    
    def test_email_too_long(self):
        """Test email too long validation error."""
        # Create an email with more than 100 characters
        long_email = 'a' * 101  # 101 characters
        
        data = {
            'username': 'testuser',
            'email': long_email,
            'age': 25,
            'role': 'admin'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreateSchema(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['type'] == 'string_too_long'
        assert errors[0]['loc'] == ('email',)
        assert 'at most 100 characters' in errors[0]['msg']
    
    def test_role_maximum_length(self):
        """Test role maximum length validation."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'age': 25,
            'role': 'a' * 20  # exactly 20 characters
        }
        
        schema = UserCreateSchema(**data)
        assert schema.role == 'a' * 20
    
    def test_role_too_long(self):
        """Test role too long validation error."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'age': 25,
            'role': 'a' * 21  # 21 characters
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreateSchema(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['type'] == 'string_too_long'
        assert errors[0]['loc'] == ('role',)
        assert 'at most 20 characters' in errors[0]['msg']
    
    def test_age_valid_integer(self):
        """Test age accepts valid integer values."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'age': 25,
            'role': 'admin'
        }
        
        schema = UserCreateSchema(**data)
        assert schema.age == 25
    
    def test_age_invalid_type(self):
        """Test age validation with invalid type."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'age': 'twenty-five',  # string instead of int
            'role': 'admin'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreateSchema(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['type'] == 'int_parsing'
        assert errors[0]['loc'] == ('age',)
    
    def test_missing_required_fields(self):
        """Test validation error when required fields are missing."""
        data = {
            'username': 'testuser',
            # missing email, age, role
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreateSchema(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 3
        error_fields = [error['loc'][0] for error in errors]
        assert 'email' in error_fields
        assert 'age' in error_fields
        assert 'role' in error_fields
    
    def test_empty_string_fields(self):
        """Test validation with empty string fields."""
        data = {
            'username': '',
            'email': '',
            'age': 25,
            'role': ''
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreateSchema(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1  # Only username has a minimum length constraint
        assert errors[0]['loc'] == ('username',)
        assert errors[0]['type'] == 'string_too_short'


class TestUserSchema:
    """Test the UserSchema validation."""
    
    def test_valid_user_schema(self):
        """Test valid user schema with all fields."""
        data = {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'age': 25,
            'role': 'admin'
        }
        
        schema = UserSchema(**data)
        
        assert schema.id == 1
        assert schema.username == 'testuser'
        assert schema.email == 'test@example.com'
        assert schema.age == 25
        assert schema.role == 'admin'
    
    def test_user_schema_missing_id(self):
        """Test user schema validation when ID is missing."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'age': 25,
            'role': 'admin'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserSchema(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['loc'] == ('id',)
        assert errors[0]['type'] == 'missing'
    
    def test_user_schema_invalid_id_type(self):
        """Test user schema validation with invalid ID type."""
        data = {
            'id': 'not_an_integer',
            'username': 'testuser',
            'email': 'test@example.com',
            'age': 25,
            'role': 'admin'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserSchema(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['loc'] == ('id',)
        assert errors[0]['type'] == 'int_parsing'
    
    def test_user_schema_from_attributes(self):
        """Test that UserSchema can be created from an object with attributes."""
        # Create a mock object with the required attributes
        class MockUser:
            def __init__(self):
                self.id = 1
                self.username = 'testuser'
                self.email = 'test@example.com'
                self.age = 25
                self.role = 'admin'
        
        mock_user = MockUser()
        schema = UserSchema.model_validate(mock_user)
        
        assert schema.id == 1
        assert schema.username == 'testuser'
        assert schema.email == 'test@example.com'
        assert schema.age == 25
        assert schema.role == 'admin'


class TestUserResponseSchema:
    """Test the UserResponseSchema validation."""
    
    def test_valid_user_response_schema(self):
        """Test valid user response schema with multiple users."""
        user_data = [
            {
                'id': 1,
                'username': 'user1',
                'email': 'user1@example.com',
                'age': 25,
                'role': 'admin'
            },
            {
                'id': 2,
                'username': 'user2',
                'email': 'user2@example.com',
                'age': 30,
                'role': 'user'
            }
        ]
        
        users = [UserSchema(**user) for user in user_data]
        response_schema = UserResponseSchema(users=users)
        
        assert len(response_schema.users) == 2
        assert response_schema.users[0].username == 'user1'
        assert response_schema.users[1].username == 'user2'
    
    def test_empty_user_response_schema(self):
        """Test user response schema with empty user list."""
        response_schema = UserResponseSchema(users=[])
        
        assert response_schema.users == []
    
    def test_user_response_schema_missing_users(self):
        """Test user response schema when users field is missing."""
        with pytest.raises(ValidationError) as exc_info:
            UserResponseSchema()
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['loc'] == ('users',)
        assert errors[0]['type'] == 'missing'
    
    def test_user_response_schema_invalid_user_data(self):
        """Test user response schema with invalid user data."""
        invalid_user_data = [
            {
                'id': 1,
                'username': 'user1',
                'email': 'user1@example.com',
                'age': 25,
                'role': 'admin'
            },
            {
                # Missing required fields
                'id': 2,
                'username': 'user2'
            }
        ]
        
        with pytest.raises(ValidationError) as exc_info:
            users = [UserSchema(**user) for user in invalid_user_data]
        
        # The error occurs when creating the second UserSchema, not the UserResponseSchema
        errors = exc_info.value.errors()
        assert len(errors) == 3  # Missing email, age, role
        error_fields = [error['loc'][0] for error in errors]
        assert 'email' in error_fields
        assert 'age' in error_fields
        assert 'role' in error_fields


class TestErrorResponseBuilder:
    """Test the ErrorResponseBuilder helper methods."""
    
    def test_validation_error(self):
        """Test creating a validation error response."""
        field_error = FieldError(
            field='username',
            message='Username is required',
            code=ErrorCode.MISSING_REQUIRED_FIELD
        )
        
        error_response = ErrorResponseBuilder.validation_error(
            "Validation failed",
            [field_error]
        )
        
        assert error_response.error == "Validation Error"
        assert error_response.code == ErrorCode.VALIDATION_ERROR
        assert error_response.message == "Validation failed"
        assert len(error_response.details) == 1
        assert error_response.details[0].field == 'username'
        assert error_response.details[0].code == ErrorCode.MISSING_REQUIRED_FIELD
    
    def test_not_found_error(self):
        """Test creating a not found error response."""
        error_response = ErrorResponseBuilder.not_found("User", 123)
        
        assert error_response.error == "Resource Not Found"
        assert error_response.code == ErrorCode.RESOURCE_NOT_FOUND
        assert error_response.message == "User not found with id: 123"
    
    def test_not_found_error_without_id(self):
        """Test creating a not found error response without ID."""
        error_response = ErrorResponseBuilder.not_found("User")
        
        assert error_response.error == "Resource Not Found"
        assert error_response.code == ErrorCode.RESOURCE_NOT_FOUND
        assert error_response.message == "User not found"
    
    def test_already_exists_error(self):
        """Test creating an already exists error response."""
        error_response = ErrorResponseBuilder.already_exists("User", "username", "testuser")
        
        assert error_response.error == "Resource Already Exists"
        assert error_response.code == ErrorCode.RESOURCE_ALREADY_EXISTS
        assert error_response.message == "User already exists with username: testuser"
    
    def test_database_error(self):
        """Test creating a database error response."""
        error_response = ErrorResponseBuilder.database_error("Connection failed")
        
        assert error_response.error == "Database Error"
        assert error_response.code == ErrorCode.DATABASE_ERROR
        assert error_response.message == "Connection failed"
    
    def test_database_error_default_message(self):
        """Test creating a database error response with default message."""
        error_response = ErrorResponseBuilder.database_error()
        
        assert error_response.error == "Database Error"
        assert error_response.code == ErrorCode.DATABASE_ERROR
        assert error_response.message == "Database operation failed"
    
    def test_constraint_violation_error(self):
        """Test creating a constraint violation error response."""
        error_response = ErrorResponseBuilder.constraint_violation("unique_username", "Username must be unique")
        
        assert error_response.error == "Constraint Violation"
        assert error_response.code == ErrorCode.CONSTRAINT_VIOLATION
        assert error_response.message == "Username must be unique"
    
    def test_constraint_violation_error_default_message(self):
        """Test creating a constraint violation error response with default message."""
        error_response = ErrorResponseBuilder.constraint_violation("unique_username")
        
        assert error_response.error == "Constraint Violation"
        assert error_response.code == ErrorCode.CONSTRAINT_VIOLATION
        assert error_response.message == "Database constraint violation: unique_username"
    
    def test_invalid_json_error(self):
        """Test creating an invalid JSON error response."""
        error_response = ErrorResponseBuilder.invalid_json("JSON parsing failed")
        
        assert error_response.error == "Invalid JSON"
        assert error_response.code == ErrorCode.INVALID_JSON
        assert error_response.message == "JSON parsing failed"
    
    def test_invalid_json_error_default_message(self):
        """Test creating an invalid JSON error response with default message."""
        error_response = ErrorResponseBuilder.invalid_json()
        
        assert error_response.error == "Invalid JSON"
        assert error_response.code == ErrorCode.INVALID_JSON
        assert error_response.message == "Invalid JSON in request body"
    
    def test_internal_server_error(self):
        """Test creating an internal server error response."""
        error_response = ErrorResponseBuilder.internal_server_error("Unexpected error occurred")
        
        assert error_response.error == "Internal Server Error"
        assert error_response.code == ErrorCode.INTERNAL_SERVER_ERROR
        assert error_response.message == "Unexpected error occurred"
    
    def test_internal_server_error_default_message(self):
        """Test creating an internal server error response with default message."""
        error_response = ErrorResponseBuilder.internal_server_error()
        
        assert error_response.error == "Internal Server Error"
        assert error_response.code == ErrorCode.INTERNAL_SERVER_ERROR
        assert error_response.message == "An internal server error occurred"
    
    def test_pydantic_validation_error(self):
        """Test converting Pydantic validation error to standardized error response."""
        # Create a validation error by trying to create an invalid UserCreateSchema
        try:
            UserCreateSchema(username="ab", email="", age="invalid", role="")
        except ValidationError as e:
            error_response = ErrorResponseBuilder.pydantic_validation_error(e)
            
            assert error_response.error == "Validation Error"
            assert error_response.code == ErrorCode.VALIDATION_ERROR
            assert error_response.message == "Request validation failed"
            assert len(error_response.details) >= 2  # At least username and age errors
            
            # Check that field errors are properly mapped
            field_names = [detail.field for detail in error_response.details]
            assert 'username' in field_names
            assert 'age' in field_names
            
            # Check that error codes are properly mapped
            error_codes = [detail.code for detail in error_response.details]
            assert ErrorCode.VALUE_TOO_SHORT in error_codes
            assert ErrorCode.INVALID_DATA_TYPE in error_codes


class TestFieldError:
    """Test the FieldError schema."""
    
    def test_valid_field_error(self):
        """Test creating a valid field error."""
        field_error = FieldError(
            field='username',
            message='Username is required',
            code=ErrorCode.MISSING_REQUIRED_FIELD,
            value='test_value'
        )
        
        assert field_error.field == 'username'
        assert field_error.message == 'Username is required'
        assert field_error.code == ErrorCode.MISSING_REQUIRED_FIELD
        assert field_error.value == 'test_value'
    
    def test_field_error_without_value(self):
        """Test creating a field error without value."""
        field_error = FieldError(
            field='username',
            message='Username is required',
            code=ErrorCode.MISSING_REQUIRED_FIELD
        )
        
        assert field_error.field == 'username'
        assert field_error.message == 'Username is required'
        assert field_error.code == ErrorCode.MISSING_REQUIRED_FIELD
        assert field_error.value is None


class TestErrorResponse:
    """Test the ErrorResponse schema."""
    
    def test_valid_error_response(self):
        """Test creating a valid error response."""
        field_error = FieldError(
            field='username',
            message='Username is required',
            code=ErrorCode.MISSING_REQUIRED_FIELD
        )
        
        error_response = ErrorResponse(
            error="Validation Error",
            code=ErrorCode.VALIDATION_ERROR,
            message="Request validation failed",
            details=[field_error],
            request_id="test-request-id"
        )
        
        assert error_response.error == "Validation Error"
        assert error_response.code == ErrorCode.VALIDATION_ERROR
        assert error_response.message == "Request validation failed"
        assert len(error_response.details) == 1
        assert error_response.details[0].field == 'username'
        assert error_response.request_id == "test-request-id"
    
    def test_error_response_without_optional_fields(self):
        """Test creating an error response without optional fields."""
        error_response = ErrorResponse(
            error="Not Found",
            code=ErrorCode.RESOURCE_NOT_FOUND,
            message="Resource not found"
        )
        
        assert error_response.error == "Not Found"
        assert error_response.code == ErrorCode.RESOURCE_NOT_FOUND
        assert error_response.message == "Resource not found"
        assert error_response.details is None
        assert error_response.request_id is None 