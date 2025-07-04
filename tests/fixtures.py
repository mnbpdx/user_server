import pytest
from models.user import User
from models import db


@pytest.fixture
def sample_user_data():
    """Provide sample user data for testing."""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'age': 25,
        'role': 'admin'
    }


@pytest.fixture
def sample_users_data():
    """Provide multiple sample users for testing."""
    return [
        {
            'username': 'alice',
            'email': 'alice@example.com',
            'age': 30,
            'role': 'admin'
        },
        {
            'username': 'bob',
            'email': 'bob@example.com',
            'age': 25,
            'role': 'user'
        },
        {
            'username': 'charlie',
            'email': 'charlie@example.com',
            'age': 35,
            'role': 'moderator'
        }
    ]


@pytest.fixture
def create_user(app):
    """Create a single user in the database for testing."""
    def _create_user(username='testuser', email='test@example.com', age=25, role='admin'):
        with app.app_context():
            user = User(username=username, email=email, age=age, role=role)
            db.session.add(user)
            db.session.commit()
            # Refresh the user to get the ID and avoid detached session issues
            db.session.refresh(user)
            # Return the user data as a dict to avoid session issues
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'age': user.age,
                'role': user.role
            }
    return _create_user


@pytest.fixture
def create_users(app):
    """Create multiple users in the database for testing."""
    def _create_users(users_data):
        with app.app_context():
            created_users = []
            for user_data in users_data:
                user = User(**user_data)
                db.session.add(user)
                created_users.append(user)
            db.session.commit()
            return created_users
    return _create_users