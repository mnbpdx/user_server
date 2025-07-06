import pytest
from pydantic import ValidationError
from models.user import User
from schemas.user_schemas import UserSchema


class TestUserModel:
    """Test the User model class."""
    
    def test_user_creation(self):
        """Test creating a User instance."""
        user = User(
            username='testuser',
            email='test@example.com',
            age=25,
            role='admin'
        )
        
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.age == 25
        assert user.role == 'admin'
        assert user.id is None  # ID is not set until saved to database
    
    def test_user_creation_with_id(self):
        """Test creating a User instance with ID."""
        user = User(
            id=1,
            username='testuser',
            email='test@example.com',
            age=25,
            role='admin'
        )
        
        assert user.id == 1
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.age == 25
        assert user.role == 'admin'
    
    def test_user_tablename(self):
        """Test that the User model has the correct table name."""
        assert User.__tablename__ == 'users'
    
    def test_user_to_dict(self):
        """Test the to_dict method."""
        user = User(
            id=1,
            username='testuser',
            email='test@example.com',
            age=25,
            role='admin'
        )
        
        user_dict = user.to_dict()
        
        assert isinstance(user_dict, dict)
        assert user_dict['id'] == 1
        assert user_dict['username'] == 'testuser'
        assert user_dict['email'] == 'test@example.com'
        assert user_dict['age'] == 25
        assert user_dict['role'] == 'admin'
        assert len(user_dict) == 5  # Ensure no extra fields
    
    def test_user_to_dict_with_none_id(self):
        """Test the to_dict method when ID is None."""
        user = User(
            username='testuser',
            email='test@example.com',
            age=25,
            role='admin'
        )
        
        user_dict = user.to_dict()
        
        assert user_dict['id'] is None
        assert user_dict['username'] == 'testuser'
        assert user_dict['email'] == 'test@example.com'
        assert user_dict['age'] == 25
        assert user_dict['role'] == 'admin'
    
    def test_user_to_user_schema(self):
        """Test the to_user_schema static method."""
        user_schema = User.to_user_schema(
            id=1,
            username='testuser',
            email='test@example.com',
            age=25,
            role='admin'
        )
        
        assert isinstance(user_schema, UserSchema)
        assert user_schema.id == 1
        assert user_schema.username == 'testuser'
        assert user_schema.email == 'test@example.com'
        assert user_schema.age == 25
        assert user_schema.role == 'admin'
    
    def test_user_to_user_schema_with_none_id(self):
        """Test the to_user_schema static method with None ID raises ValidationError."""
        with pytest.raises(ValidationError):
            User.to_user_schema(
                id=None,
                username='testuser',
                email='test@example.com',
                age=25,
                role='admin'
            )
    
    def test_user_repr(self):
        """Test the __repr__ method."""
        user = User(
            id=1,
            username='testuser',
            email='test@example.com',
            age=25,
            role='admin'
        )
        
        repr_str = repr(user)
        
        assert '<id: 1' in repr_str
        assert 'username: testuser' in repr_str
        assert 'email: test@example.com' in repr_str
        assert 'age: 25' in repr_str
        assert 'role: admin' in repr_str
    
    def test_user_repr_with_none_id(self):
        """Test the __repr__ method when ID is None."""
        user = User(
            username='testuser',
            email='test@example.com',
            age=25,
            role='admin'
        )
        
        repr_str = repr(user)
        
        assert '<id: None' in repr_str
        assert 'username: testuser' in repr_str
        assert 'email: test@example.com' in repr_str
        assert 'age: 25' in repr_str
        assert 'role: admin' in repr_str
    
    def test_user_repr_with_special_characters(self):
        """Test the __repr__ method with special characters in fields."""
        user = User(
            id=1,
            username='test_user@123',
            email='test+user@example.com',
            age=25,
            role='admin-user'
        )
        
        repr_str = repr(user)
        
        assert '<id: 1' in repr_str
        assert 'username: test_user@123' in repr_str
        assert 'email: test+user@example.com' in repr_str
        assert 'age: 25' in repr_str
        assert 'role: admin-user' in repr_str
    
    def test_user_equality(self):
        """Test User equality comparison."""
        user1 = User(
            id=1,
            username='testuser',
            email='test@example.com',
            age=25,
            role='admin'
        )
        
        user2 = User(
            id=1,
            username='testuser',
            email='test@example.com',
            age=25,
            role='admin'
        )
        
        # Note: Users with same data are not automatically equal unless explicitly implemented
        # This test documents the current behavior
        assert user1 != user2  # Different object instances
    
    def test_user_attributes_types(self):
        """Test that User attributes have correct types."""
        user = User(
            id=1,
            username='testuser',
            email='test@example.com',
            age=25,
            role='admin'
        )
        
        assert isinstance(user.id, int)
        assert isinstance(user.username, str)
        assert isinstance(user.email, str)
        assert isinstance(user.age, int)
        assert isinstance(user.role, str)
    
    def test_user_boundary_values(self):
        """Test User model with boundary values."""
        # Test with minimum valid values
        user_min = User(
            id=1,
            username='abc',  # 3 characters (minimum)
            email='a@b.c',   # short but valid email
            age=0,           # minimum age
            role='x'         # 1 character role
        )
        
        assert user_min.username == 'abc'
        assert user_min.email == 'a@b.c'
        assert user_min.age == 0
        assert user_min.role == 'x'
        
        # Test with maximum valid values
        user_max = User(
            id=999999,
            username='a' * 50,  # 50 characters (maximum)
            email='a' * 88 + '@example.com',  # 100 characters total
            age=150,            # large age
            role='a' * 20       # 20 characters (maximum)
        )
        
        assert len(user_max.username) == 50
        assert len(user_max.email) == 100
        assert user_max.age == 150
        assert len(user_max.role) == 20
    
    def test_user_dict_conversion_consistency(self):
        """Test that to_dict conversion is consistent."""
        original_data = {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'age': 25,
            'role': 'admin'
        }
        
        user = User(**original_data)
        converted_data = user.to_dict()
        
        assert converted_data == original_data
    
    def test_user_schema_conversion_consistency(self):
        """Test that to_user_schema conversion is consistent."""
        original_data = {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'age': 25,
            'role': 'admin'
        }
        
        user_schema = User.to_user_schema(**original_data)
        
        assert user_schema.id == original_data['id']
        assert user_schema.username == original_data['username']
        assert user_schema.email == original_data['email']
        assert user_schema.age == original_data['age']
        assert user_schema.role == original_data['role']
    
    def test_user_unicode_handling(self):
        """Test User model with Unicode characters."""
        user = User(
            id=1,
            username='用户名',  # Chinese characters
            email='тест@пример.com',  # Cyrillic characters
            age=25,
            role='管理员'  # Chinese characters
        )
        
        assert user.username == '用户名'
        assert user.email == 'тест@пример.com'
        assert user.role == '管理员'
        
        # Test to_dict with Unicode
        user_dict = user.to_dict()
        assert user_dict['username'] == '用户名'
        assert user_dict['email'] == 'тест@пример.com'
        assert user_dict['role'] == '管理员'
        
        # Test __repr__ with Unicode
        repr_str = repr(user)
        assert '用户名' in repr_str
        assert 'тест@пример.com' in repr_str
        assert '管理员' in repr_str
    
    def test_user_with_empty_strings(self):
        """Test User model with empty strings."""
        user = User(
            id=1,
            username='',
            email='',
            age=25,
            role=''
        )
        
        assert user.username == ''
        assert user.email == ''
        assert user.role == ''
        
        # Test to_dict with empty strings
        user_dict = user.to_dict()
        assert user_dict['username'] == ''
        assert user_dict['email'] == ''
        assert user_dict['role'] == ''
    
    def test_user_field_modification(self):
        """Test that User fields can be modified after creation."""
        user = User(
            id=1,
            username='olduser',
            email='old@example.com',
            age=25,
            role='user'
        )
        
        # Modify fields
        user.username = 'newuser'
        user.email = 'new@example.com'
        user.age = 30
        user.role = 'admin'
        
        assert user.username == 'newuser'
        assert user.email == 'new@example.com'
        assert user.age == 30
        assert user.role == 'admin'
        
        # Verify changes are reflected in to_dict
        user_dict = user.to_dict()
        assert user_dict['username'] == 'newuser'
        assert user_dict['email'] == 'new@example.com'
        assert user_dict['age'] == 30
        assert user_dict['role'] == 'admin' 