from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from services.user_service import UserService
from schemas.user_schemas import UserSchema, UserResponseSchema, UserCreateSchema
from schemas.error_schemas import ErrorResponseBuilder

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

@users_bp.route('', methods=['GET'])
def get_all_users():
    """Get all users from the database.
    
    Returns:
        Response: JSON response containing all users wrapped in UserResponseSchema.
    """
    users = UserService.get_all_users()
    usersResponse = UserResponseSchema(users=[UserSchema.model_validate(user) for user in users])
    return jsonify(usersResponse.model_dump())

@users_bp.route('/role/<role>', methods=['GET'])
def get_users_by_role(role):
    """Get all users with a specific role.
    
    Args:
        role (str): The role to filter users by.
        
    Returns:
        Response: JSON response containing users with the specified role.
    """
    users = UserService.get_users_by_role(role=role)
    usersResponse = UserResponseSchema(users=[UserSchema.model_validate(user) for user in users])
    return jsonify(usersResponse.model_dump())

@users_bp.route('/<int:id>', methods=['GET'])
def get_user(id):
    """Get a specific user by ID.
    
    Args:
        id (int): The ID of the user to retrieve.
        
    Returns:
        Response: JSON response containing the user data or error message.
        
    Status Codes:
        200: User found and returned successfully.
        404: User not found.
    """
    user = UserService.get_user(id=id)
    if not user:
        error_response = ErrorResponseBuilder.not_found("User", id)
        return jsonify(error_response.model_dump()), 404
    
    userResponse = UserSchema.model_validate(user)
    return jsonify(userResponse.model_dump())

@users_bp.route('/<int:id>', methods=['DELETE'])
def delete_user(id):
    """Delete a specific user by ID.
    
    Args:
        id (int): The ID of the user to delete.
        
    Returns:
        Response: Empty response with appropriate status code.
        
    Status Codes:
        204: User deleted successfully.
        404: User not found.
        500: Internal server error.
    """
    success, error_response = UserService.delete_user(id=id)
    if not success:
        status_code = 404 if error_response.code == "RESOURCE_NOT_FOUND" else 500
        return jsonify(error_response.model_dump()), status_code
    
    return '', 204

@users_bp.route('', methods=['POST'])
def create_user():
    """Create a new user.
    
    Expects JSON body with username, email, age, and role fields.
    The user ID is auto-generated.
    
    Returns:
        Response: JSON response containing the created user data or error message.
        
    Status Codes:
        201: User created successfully.
        400: Invalid request data or validation error.
        409: User with same username or email already exists.
        500: Internal server error during user creation.
    """
    try:
        # Check if request has JSON content
        if not request.is_json:
            error_response = ErrorResponseBuilder.invalid_json("Request must have JSON content type")
            return jsonify(error_response.model_dump()), 400
            
        # Get JSON data - handle potential exceptions
        try:
            json_data = request.get_json()
        except Exception:
            error_response = ErrorResponseBuilder.invalid_json("Request body must be valid JSON")
            return jsonify(error_response.model_dump()), 400
            
        if json_data is None:
            error_response = ErrorResponseBuilder.invalid_json("Request body must be valid JSON")
            return jsonify(error_response.model_dump()), 400
        
        # Validate request data
        validatedUserRequest = UserCreateSchema(**json_data)
        
        # Create user
        user, error_response = UserService.create_user(
            validatedUserRequest.username,
            validatedUserRequest.email,
            validatedUserRequest.age,
            validatedUserRequest.role
        )
        
        # Handle service errors
        if error_response:
            if error_response.code == "RESOURCE_ALREADY_EXISTS":
                return jsonify(error_response.model_dump()), 409
            elif error_response.code == "CONSTRAINT_VIOLATION":
                return jsonify(error_response.model_dump()), 409
            elif error_response.code == "DATABASE_ERROR":
                return jsonify(error_response.model_dump()), 500
            else:
                return jsonify(error_response.model_dump()), 500
        
        # Return created user
        userResponse = UserSchema.model_validate(user)
        return jsonify(userResponse.model_dump()), 201
        
    except ValidationError as e:
        error_response = ErrorResponseBuilder.pydantic_validation_error(e)
        return jsonify(error_response.model_dump()), 400
        
    except Exception as e:
        error_response = ErrorResponseBuilder.internal_server_error(
            "An unexpected error occurred while processing the request"
        )
        return jsonify(error_response.model_dump()), 500
