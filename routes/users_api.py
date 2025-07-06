from flask import jsonify, request
from flask_restx import Resource
from pydantic import ValidationError
from services.user_service import UserService
from schemas.user_schemas import UserSchema, UserResponseSchema, UserCreateSchema, UserUpdateSchema
from schemas.error_schemas import ErrorResponseBuilder, ErrorCode
from rate_limiting import limiter
from flask import current_app
import functools

def conditional_rate_limit(limit_string):
    """Apply rate limiting only if not in testing mode."""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Skip rate limiting in test mode
            if current_app.config.get('TESTING') or not current_app.config.get('RATELIMIT_ENABLED', True):
                return f(*args, **kwargs)
            # Apply rate limiting decorator
            rate_limited_func = limiter.limit(limit_string)(f)
            return rate_limited_func(*args, **kwargs)
        return decorated_function
    return decorator
from api_docs import (
    users_ns, user_model, user_create_model, user_update_model, 
    user_response_model, error_model
)

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

@users_ns.route('/')
class UserList(Resource):
    @users_ns.doc('get_all_users')
    @users_ns.marshal_with(user_response_model)
    def get(self):
        """Get all users from the database."""
        users = UserService.get_all_users()
        usersResponse = UserResponseSchema(users=[UserSchema.model_validate(user) for user in users])
        return usersResponse.model_dump()

    @users_ns.doc('create_user')
    @users_ns.expect(user_create_model)
    @users_ns.marshal_with(user_model, code=201)
    @users_ns.response(400, 'Invalid input', error_model)
    @users_ns.response(409, 'User already exists', error_model)
    @conditional_rate_limit("2 per minute")
    def post(self):
        """Create a new user."""
        try:
            validatedUserRequest, err, status = _parse_json_body(UserCreateSchema)
            if err:
                return err.model_dump(), status
            
            # Create user
            user, error_response = UserService.create_user(
                validatedUserRequest.username,
                validatedUserRequest.email,
                validatedUserRequest.age,
                validatedUserRequest.role
            )
            
            # Handle service errors
            if error_response:
                return error_response.model_dump(), _error_status(error_response)
            
            # Return created user
            userResponse = UserSchema.model_validate(user)
            return userResponse.model_dump(), 201
            
        except Exception as e:
            error_response = ErrorResponseBuilder.internal_server_error(
                "An unexpected error occurred while processing the request"
            )
            return error_response.model_dump(), 500

@users_ns.route('/role/<string:role>')
class UsersByRole(Resource):
    @users_ns.doc('get_users_by_role')
    @users_ns.marshal_with(user_response_model)
    @users_ns.param('role', 'The role to filter users by')
    def get(self, role):
        """Get all users with a specific role."""
        users = UserService.get_users_by_role(role=role)
        usersResponse = UserResponseSchema(users=[UserSchema.model_validate(user) for user in users])
        return usersResponse.model_dump()

@users_ns.route('/<int:id>')
@users_ns.param('id', 'The user identifier')
class User(Resource):
    @users_ns.doc('get_user')
    @users_ns.marshal_with(user_model)
    @users_ns.response(404, 'User not found', error_model)
    def get(self, id):
        """Get a specific user by ID."""
        user = UserService.get_user(id=id)
        if not user:
            error_response = ErrorResponseBuilder.not_found("User", id)
            return error_response.model_dump(), 404
        
        userResponse = UserSchema.model_validate(user)
        return userResponse.model_dump()

    @users_ns.doc('delete_user')
    @users_ns.response(204, 'User deleted successfully')
    @users_ns.response(404, 'User not found', error_model)
    @conditional_rate_limit("3 per minute")
    def delete(self, id):
        """Delete a specific user by ID."""
        success, error_response = UserService.delete_user(id=id)
        if not success:
            status_code = 404 if error_response.code == "RESOURCE_NOT_FOUND" else 500
            return error_response.model_dump(), status_code
        
        return '', 204

    @users_ns.doc('update_user')
    @users_ns.expect(user_update_model)
    @users_ns.marshal_with(user_model)
    @users_ns.response(400, 'Invalid input', error_model)
    @users_ns.response(404, 'User not found', error_model)
    @users_ns.response(409, 'User already exists', error_model)
    @limiter.limit("5 per minute")
    def patch(self, id):
        """Update an existing user."""
        try:
            validatedUserRequest, err, status = _parse_json_body(UserUpdateSchema)
            if err:
                return err.model_dump(), status
            
            # Filter out None values to only update provided fields
            update_data = {k: v for k, v in validatedUserRequest.model_dump().items() if v is not None}
            
            # If no fields to update, return validation error
            if not update_data:
                error_response = ErrorResponseBuilder.invalid_json("At least one field must be provided for update")
                return error_response.model_dump(), 400
            
            # Update user
            user, error_response = UserService.update_user(id, update_data)
            
            # Handle service errors
            if error_response:
                return error_response.model_dump(), _error_status(error_response)
            
            # Return updated user
            userResponse = UserSchema.model_validate(user)
            return userResponse.model_dump(), 200
            
        except Exception as e:
            error_response = ErrorResponseBuilder.internal_server_error(
                "An unexpected error occurred while processing the request"
            )
            return error_response.model_dump(), 500 