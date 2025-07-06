from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from services.user_service import UserService
from schemas.user_schemas import UserSchema, UserResponseSchema, UserCreateSchema, UserUpdateSchema
from schemas.error_schemas import ErrorResponseBuilder, ErrorCode

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

# ---------------------------------------------------------------------------
# Helper utilities shared by multiple routes
# ---------------------------------------------------------------------------

def _parse_json_body(schema_cls):
    """Parse request JSON and validate against *schema_cls*.

    Returns a tuple *(validated_model, error_response, status_code)* where
    *validated_model* is the parsed Pydantic model instance on success.
    When the request is invalid, *validated_model* is ``None`` and the second
    and third tuple elements contain an ``ErrorResponse`` and HTTP status code
    respectively.  This keeps route handlers concise and consistent.
    """

    if not request.is_json:
        return None, ErrorResponseBuilder.invalid_json("Request must have JSON content type"), 400

    try:
        json_data = request.get_json()
    except Exception:
        return None, ErrorResponseBuilder.invalid_json("Request body must be valid JSON"), 400

    if json_data is None:
        return None, ErrorResponseBuilder.invalid_json("Request body must be valid JSON"), 400

    try:
        return schema_cls(**json_data), None, None
    except ValidationError as exc:
        return None, ErrorResponseBuilder.pydantic_validation_error(exc), 400

def _error_status(err):
    """Map our ErrorCode enum to an HTTP status code."""

    mapping = {
        ErrorCode.RESOURCE_NOT_FOUND: 404,
        ErrorCode.RESOURCE_ALREADY_EXISTS: 409,
        ErrorCode.CONSTRAINT_VIOLATION: 409,
        ErrorCode.DATABASE_ERROR: 500,
        ErrorCode.VALIDATION_ERROR: 400,
        ErrorCode.INVALID_JSON: 400,
    }
    return mapping.get(err.code, 500)

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
        validatedUserRequest, err, status = _parse_json_body(UserCreateSchema)
        if err:
            return jsonify(err.model_dump()), status
        
        # Create user
        user, error_response = UserService.create_user(
            validatedUserRequest.username,
            validatedUserRequest.email,
            validatedUserRequest.age,
            validatedUserRequest.role
        )
        
        # Handle service errors
        if error_response:
            return jsonify(error_response.model_dump()), _error_status(error_response)
        
        # Return created user
        userResponse = UserSchema.model_validate(user)
        return jsonify(userResponse.model_dump()), 201
        
    except Exception as e:
        error_response = ErrorResponseBuilder.internal_server_error(
            "An unexpected error occurred while processing the request"
        )
        return jsonify(error_response.model_dump()), 500

@users_bp.route('/<int:id>', methods=['PATCH'])
def update_user(id):
    """Update an existing user.
    
    Expects JSON body with optional fields: username, email, age, and/or role.
    Only provided fields will be updated (partial updates supported).
    
    Args:
        id (int): The ID of the user to update.
        
    Returns:
        Response: JSON response containing the updated user data or error message.
        
    Status Codes:
        200: User updated successfully.
        400: Invalid request data or validation error.
        404: User not found.
        409: User with same username or email already exists.
        500: Internal server error during user update.
    """
    try:
        validatedUserRequest, err, status = _parse_json_body(UserUpdateSchema)
        if err:
            return jsonify(err.model_dump()), status
        
        # Filter out None values to only update provided fields
        update_data = {k: v for k, v in validatedUserRequest.model_dump().items() if v is not None}
        
        # If no fields to update, return validation error
        if not update_data:
            error_response = ErrorResponseBuilder.invalid_json("At least one field must be provided for update")
            return jsonify(error_response.model_dump()), 400
        
        # Update user
        user, error_response = UserService.update_user(id, update_data)
        
        # Handle service errors
        if error_response:
            return jsonify(error_response.model_dump()), _error_status(error_response)
        
        # Return updated user
        userResponse = UserSchema.model_validate(user)
        return jsonify(userResponse.model_dump()), 200
        
    except Exception as e:
        error_response = ErrorResponseBuilder.internal_server_error(
            "An unexpected error occurred while processing the request"
        )
        return jsonify(error_response.model_dump()), 500
