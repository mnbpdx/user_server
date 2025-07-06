import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.exc import IntegrityError, DatabaseError
from services.user_service import UserService
from models.user import User
from schemas.error_schemas import ErrorResponse, ErrorCode


class TestUserServiceCreateUser:
    """Test the UserService.create_user method."""
    
    @patch('services.user_service.db')
    def test_create_user_success(self, mock_db):
        """Test successful user creation."""
        # Arrange
        mock_db.session.query.return_value.filter.return_value.first.return_value = None
        mock_user = Mock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.age = 25
        mock_user.role = "admin"
        
        # Mock the User constructor to return our mock user
        with patch('services.user_service.User', return_value=mock_user):
            # Act
            user, error = UserService.create_user("testuser", "test@example.com", 25, "admin")
            
            # Assert
            assert user == mock_user
            assert error is None
            mock_db.session.add.assert_called_once_with(mock_user)
            mock_db.session.commit.assert_called_once()
    
    @patch('services.user_service.db')
    def test_create_user_username_already_exists(self, mock_db):
        """Test user creation when username already exists through database constraint."""
        # Arrange
        mock_user = Mock()
        
        # Mock IntegrityError with username in message
        integrity_error = IntegrityError("statement", "params", "orig")
        integrity_error.orig = Mock()
        integrity_error.orig.__str__ = Mock(return_value="UNIQUE constraint failed: users.username")
        
        mock_db.session.commit.side_effect = integrity_error
        
        with patch('services.user_service.User', return_value=mock_user):
            # Act
            user, error = UserService.create_user("testuser", "test@example.com", 25, "admin")
            
            # Assert
            assert user is None
            assert error is not None
            assert error.code == ErrorCode.CONSTRAINT_VIOLATION
            assert "Username" in error.message and "testuser" in error.message
            mock_db.session.rollback.assert_called_once()
    
    @patch('services.user_service.db')
    def test_create_user_email_already_exists(self, mock_db):
        """Test user creation when email already exists through database constraint."""
        # Arrange
        mock_user = Mock()
        
        # Mock IntegrityError with email in message
        integrity_error = IntegrityError("statement", "params", "orig")
        integrity_error.orig = Mock()
        integrity_error.orig.__str__ = Mock(return_value="UNIQUE constraint failed: users.email")
        
        mock_db.session.commit.side_effect = integrity_error
        
        with patch('services.user_service.User', return_value=mock_user):
            # Act
            user, error = UserService.create_user("testuser", "test@example.com", 25, "admin")
            
            # Assert
            assert user is None
            assert error is not None
            assert error.code == ErrorCode.CONSTRAINT_VIOLATION
            assert "test@example.com" in error.message
            mock_db.session.rollback.assert_called_once()
    
    @patch('services.user_service.db')
    def test_create_user_integrity_error_username(self, mock_db):
        """Test user creation with integrity error on username."""
        # Arrange
        mock_db.session.query.return_value.filter.return_value.first.return_value = None
        mock_user = Mock()
        
        # Mock IntegrityError with username in message
        integrity_error = IntegrityError("statement", "params", "orig")
        integrity_error.orig = Mock()
        integrity_error.orig.__str__ = Mock(return_value="UNIQUE constraint failed: users.username")
        
        mock_db.session.commit.side_effect = integrity_error
        
        with patch('services.user_service.User', return_value=mock_user):
            # Act
            user, error = UserService.create_user("testuser", "test@example.com", 25, "admin")
            
            # Assert
            assert user is None
            assert error is not None
            assert error.code == ErrorCode.CONSTRAINT_VIOLATION
            assert "testuser" in error.message
            mock_db.session.rollback.assert_called_once()
    
    @patch('services.user_service.db')
    def test_create_user_integrity_error_email(self, mock_db):
        """Test user creation with integrity error on email."""
        # Arrange
        mock_db.session.query.return_value.filter.return_value.first.return_value = None
        mock_user = Mock()
        
        # Mock IntegrityError with email in message
        integrity_error = IntegrityError("statement", "params", "orig")
        integrity_error.orig = Mock()
        integrity_error.orig.__str__ = Mock(return_value="UNIQUE constraint failed: users.email")
        
        mock_db.session.commit.side_effect = integrity_error
        
        with patch('services.user_service.User', return_value=mock_user):
            # Act
            user, error = UserService.create_user("testuser", "test@example.com", 25, "admin")
            
            # Assert
            assert user is None
            assert error is not None
            assert error.code == ErrorCode.CONSTRAINT_VIOLATION
            assert "Email" in error.message and "test@example.com" in error.message
            mock_db.session.rollback.assert_called_once()
    
    @patch('services.user_service.db')
    def test_create_user_integrity_error_unknown(self, mock_db):
        """Test user creation with unknown integrity error."""
        # Arrange
        mock_db.session.query.return_value.filter.return_value.first.return_value = None
        mock_user = Mock()
        
        # Mock IntegrityError with unknown constraint
        integrity_error = IntegrityError("statement", "params", "orig")
        integrity_error.orig = Mock()
        integrity_error.orig.__str__ = Mock(return_value="UNIQUE constraint failed: users.unknown")
        
        mock_db.session.commit.side_effect = integrity_error
        
        with patch('services.user_service.User', return_value=mock_user):
            # Act
            user, error = UserService.create_user("testuser", "test@example.com", 25, "admin")
            
            # Assert
            assert user is None
            assert error is not None
            assert error.code == ErrorCode.CONSTRAINT_VIOLATION
            assert "A database constraint was violated" in error.message
            mock_db.session.rollback.assert_called_once()
    
    @patch('services.user_service.db')
    def test_create_user_database_error(self, mock_db):
        """Test user creation with database error."""
        # Arrange
        mock_db.session.query.return_value.filter.return_value.first.return_value = None
        mock_user = Mock()
        
        mock_db.session.commit.side_effect = DatabaseError("statement", "params", "orig")
        
        with patch('services.user_service.User', return_value=mock_user):
            # Act
            user, error = UserService.create_user("testuser", "test@example.com", 25, "admin")
            
            # Assert
            assert user is None
            assert error is not None
            assert error.code == ErrorCode.DATABASE_ERROR
            mock_db.session.rollback.assert_called_once()
    
    @patch('services.user_service.db')
    def test_create_user_unexpected_error(self, mock_db):
        """Test user creation with unexpected error."""
        # Arrange
        mock_db.session.query.return_value.filter.return_value.first.return_value = None
        mock_user = Mock()
        
        mock_db.session.commit.side_effect = Exception("Unexpected error")
        
        with patch('services.user_service.User', return_value=mock_user):
            # Act
            user, error = UserService.create_user("testuser", "test@example.com", 25, "admin")
            
            # Assert
            assert user is None
            assert error is not None
            assert error.code == ErrorCode.INTERNAL_SERVER_ERROR
            mock_db.session.rollback.assert_called_once()


class TestUserServiceGetUser:
    """Test the UserService.get_user method."""
    
    @patch('services.user_service.db')
    def test_get_user_success(self, mock_db):
        """Test successful user retrieval."""
        # Arrange
        mock_user = Mock()
        mock_user.id = 1
        mock_db.session.get.return_value = mock_user
        
        # Act
        user = UserService.get_user(1)
        
        # Assert
        assert user == mock_user
        mock_db.session.get.assert_called_once_with(User, 1)
    
    @patch('services.user_service.db')
    def test_get_user_not_found(self, mock_db):
        """Test user retrieval when user doesn't exist."""
        # Arrange
        mock_db.session.get.return_value = None
        
        # Act
        user = UserService.get_user(999)
        
        # Assert
        assert user is None
        mock_db.session.get.assert_called_once_with(User, 999)
    
    @patch('services.user_service.db')
    def test_get_user_database_error(self, mock_db):
        """Test user retrieval with database error."""
        # Arrange
        mock_db.session.get.side_effect = DatabaseError("statement", "params", "orig")
        
        # Act
        user = UserService.get_user(1)
        
        # Assert
        assert user is None
        mock_db.session.get.assert_called_once_with(User, 1)


class TestUserServiceGetAllUsers:
    """Test the UserService.get_all_users method."""
    
    @patch('services.user_service.db')
    def test_get_all_users_success(self, mock_db):
        """Test successful retrieval of all users."""
        # Arrange
        mock_users = [Mock(), Mock()]
        mock_db.session.query.return_value.all.return_value = mock_users
        
        # Act
        users = UserService.get_all_users()
        
        # Assert
        assert users == mock_users
        mock_db.session.query.assert_called_once_with(User)
    
    @patch('services.user_service.db')
    def test_get_all_users_empty(self, mock_db):
        """Test retrieval of all users when database is empty."""
        # Arrange
        mock_db.session.query.return_value.all.return_value = []
        
        # Act
        users = UserService.get_all_users()
        
        # Assert
        assert users == []
        mock_db.session.query.assert_called_once_with(User)
    
    @patch('services.user_service.db')
    def test_get_all_users_database_error(self, mock_db):
        """Test retrieval of all users with database error."""
        # Arrange
        mock_db.session.query.side_effect = DatabaseError("statement", "params", "orig")
        
        # Act
        users = UserService.get_all_users()
        
        # Assert
        assert users == []
        mock_db.session.query.assert_called_once_with(User)


class TestUserServiceGetUsersByRole:
    """Test the UserService.get_users_by_role method."""
    
    @patch('services.user_service.db')
    def test_get_users_by_role_success(self, mock_db):
        """Test successful retrieval of users by role."""
        # Arrange
        mock_users = [Mock(), Mock()]
        mock_db.session.query.return_value.filter.return_value.all.return_value = mock_users
        
        # Act
        users = UserService.get_users_by_role("admin")
        
        # Assert
        assert users == mock_users
        mock_db.session.query.assert_called_once_with(User)
        mock_db.session.query.return_value.filter.assert_called_once()
    
    @patch('services.user_service.db')
    def test_get_users_by_role_empty(self, mock_db):
        """Test retrieval of users by role when no users match."""
        # Arrange
        mock_db.session.query.return_value.filter.return_value.all.return_value = []
        
        # Act
        users = UserService.get_users_by_role("nonexistent")
        
        # Assert
        assert users == []
        mock_db.session.query.assert_called_once_with(User)
    
    @patch('services.user_service.db')
    def test_get_users_by_role_database_error(self, mock_db):
        """Test retrieval of users by role with database error."""
        # Arrange
        mock_db.session.query.side_effect = DatabaseError("statement", "params", "orig")
        
        # Act
        users = UserService.get_users_by_role("admin")
        
        # Assert
        assert users == []
        mock_db.session.query.assert_called_once_with(User)


class TestUserServiceDeleteUser:
    """Test the UserService.delete_user method."""
    
    @patch('services.user_service.db')
    def test_delete_user_success(self, mock_db):
        """Test successful user deletion."""
        # Arrange
        mock_user = Mock()
        mock_user.id = 1
        mock_db.session.get.return_value = mock_user
        
        # Act
        success, error = UserService.delete_user(1)
        
        # Assert
        assert success is True
        assert error is None
        mock_db.session.get.assert_called_once_with(User, 1)
        mock_db.session.delete.assert_called_once_with(mock_user)
        mock_db.session.commit.assert_called_once()
    
    @patch('services.user_service.db')
    def test_delete_user_not_found(self, mock_db):
        """Test user deletion when user doesn't exist."""
        # Arrange
        mock_db.session.get.return_value = None
        
        # Act
        success, error = UserService.delete_user(999)
        
        # Assert
        assert success is False
        assert error is not None
        assert error.code == ErrorCode.RESOURCE_NOT_FOUND
        assert "999" in error.message
        mock_db.session.get.assert_called_once_with(User, 999)
        mock_db.session.delete.assert_not_called()
        mock_db.session.commit.assert_not_called()
    
    @patch('services.user_service.db')
    def test_delete_user_database_error(self, mock_db):
        """Test user deletion with database error."""
        # Arrange
        mock_user = Mock()
        mock_user.id = 1
        mock_db.session.get.return_value = mock_user
        mock_db.session.commit.side_effect = DatabaseError("statement", "params", "orig")
        
        # Act
        success, error = UserService.delete_user(1)
        
        # Assert
        assert success is False
        assert error is not None
        assert error.code == ErrorCode.DATABASE_ERROR
        mock_db.session.rollback.assert_called_once()
    
    @patch('services.user_service.db')
    def test_delete_user_unexpected_error(self, mock_db):
        """Test user deletion with unexpected error."""
        # Arrange
        mock_user = Mock()
        mock_user.id = 1
        mock_db.session.get.return_value = mock_user
        mock_db.session.commit.side_effect = Exception("Unexpected error")
        
        # Act
        success, error = UserService.delete_user(1)
        
        # Assert
        assert success is False
        assert error is not None
        assert error.code == ErrorCode.INTERNAL_SERVER_ERROR
        mock_db.session.rollback.assert_called_once() 