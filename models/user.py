from . import db
from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column, Mapped
from schemas.user_schemas import UserSchema

class User(db.Model):
    """User model representing a user in the system.
    
    Attributes:
        id: Primary key, auto-incremented integer.
        username: User's username, up to 50 characters.
        email: User's email address, up to 100 characters.
        age: User's age as an integer.
        role: User's role in the system, up to 20 characters.
    """
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=True)
    
    def to_dict(self):
        """Convert the User instance to a dictionary.
        
        Returns:
            dict: A dictionary representation of the user with all attributes except password_hash.
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'age': self.age,
            'role': self.role
        }
    
    def to_user_schema(id, username, email, age, role):
        """Convert user data to a UserSchema instance.
        
        Args:
            id: User ID.
            username: User's username.
            email: User's email address.
            age: User's age.
            role: User's role.
            
        Returns:
            UserSchema: A validated UserSchema instance.
        """
        return UserSchema(
            id=id,
            username=username,
            email=email,
            age=age,
            role=role
        )
    
    def __repr__(self):
        """String representation of the User instance.
        
        Returns:
            str: A string representation showing all user attributes.
        """
        return f'<id: {self.id}, username: {self.username}, email: {self.email}, age: {self.age}, role: {self.role}>'
