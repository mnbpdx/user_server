from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from services.user_service import UserService
from schemas.user_schemas import UserSchema, UserResponseSchema, UserCreateSchema

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
        return jsonify({'error': 'User not found'}), 404
    
    userResponse = UserSchema.model_validate(user)
    return jsonify(userResponse.model_dump())

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
        500: Internal server error during user creation.
    """
    try:
        validatedUserRequest = UserCreateSchema(**request.get_json())
        
        user, error = UserService.create_user(
            validatedUserRequest.username,
            validatedUserRequest.email,
            validatedUserRequest.age,
            validatedUserRequest.role
        )
        
        if error:
            return jsonify({'error': error}), 500
        
        userResponse = UserSchema.model_validate(user)
        return jsonify(userResponse.model_dump()), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Request Pydantic validation failed', 'details': e.errors()}), 400
    except Exception as e:
        return jsonify({'error': 'general error'}), 400
