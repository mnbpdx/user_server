from models import db
from models.user import User
from sqlalchemy.exc import IntegrityError

class UserService:
    """Service class for user-related operations.
    
    This class provides static methods for CRUD operations on User entities,
    handling database interactions and error management.
    """
    @staticmethod
    def create_user(
        username: str,
        email: str,
        age: int,
        role: str
    ):
        """Create a new user in the database.
        
        Args:
            username (str): The username for the new user.
            email (str): The email address for the new user.
            age (int): The age of the user.
            role (str): The role of the user in the system.
            
        Returns:
            tuple: A tuple containing (User, None) on success or (None, error_message) on failure.
        """
        try:
            user = User(
                username=username,
                email=email,
                age=age,
                role=role,
            )
            db.session.add(user)
            db.session.commit()
            return user, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
        
    @staticmethod
    def get_user(id):
        """Get a user by their ID.
        
        Args:
            id (int): The ID of the user to retrieve.
            
        Returns:
            User or None: The User object if found, None otherwise.
        """
        return db.session.get(User, id)
    
    @staticmethod
    def get_all_users():
        """Get all users from the database.
        
        Returns:
            list[User]: A list of all User objects in the database.
        """
        return db.session.query(User).all()
        
    @staticmethod
    def get_users_by_role(role):
        """Get all users with a specific role.
        
        Args:
            role (str): The role to filter users by.
            
        Returns:
            list[User]: A list of User objects with the specified role.
        """
        return db.session.query(User).filter(User.role == role).all()
