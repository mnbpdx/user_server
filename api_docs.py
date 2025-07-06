from flask_restx import Api, Resource, fields
from werkzeug.exceptions import NotFound, InternalServerError

# Create API instance
api = Api(
    title='User Server API',
    version='1.0',
    description='A simple user management API with Flask',
    doc='/docs/',
    prefix='/api'
)

# User model for documentation
user_model = api.model('User', {
    'id': fields.Integer(readonly=True, description='User ID'),
    'username': fields.String(required=True, description='Username'),
    'email': fields.String(required=True, description='Email address'),
    'age': fields.Integer(required=True, description='Age'),
    'role': fields.String(required=True, description='User role'),
})

# User creation model (without ID)
user_create_model = api.model('UserCreate', {
    'username': fields.String(required=True, description='Username'),
    'email': fields.String(required=True, description='Email address'),
    'age': fields.Integer(required=True, description='Age'),
    'role': fields.String(required=True, description='User role'),
})

# User update model (all fields optional)
user_update_model = api.model('UserUpdate', {
    'username': fields.String(description='Username'),
    'email': fields.String(description='Email address'),
    'age': fields.Integer(description='Age'),
    'role': fields.String(description='User role'),
})

# User response model
user_response_model = api.model('UserResponse', {
    'users': fields.List(fields.Nested(user_model), description='List of users')
})

# Error model
error_model = api.model('Error', {
    'error': fields.String(description='Error message'),
    'code': fields.String(description='Error code'),
    'details': fields.Raw(description='Additional error details')
})

# Users namespace
users_ns = api.namespace('users', description='User operations')

# Register error handlers
@api.errorhandler(NotFound)
def handle_not_found(error):
    return {'error': 'Resource not found'}, 404

@api.errorhandler(InternalServerError)
def handle_internal_error(error):
    return {'error': 'Internal server error'}, 500

# Import the API routes to register them
from routes.users_api import * 