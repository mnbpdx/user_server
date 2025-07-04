from models import db
from models.user import User
from sqlalchemy.exc import IntegrityError, DatabaseError
from schemas.error_schemas import ErrorResponse, ErrorResponseBuilder
from typing import Tuple, Optional

class UserService:
    """Service class for user-related operations.
    
    This class provides static methods for CRUD operations on User entities,
    handling database interactions and structured error management.
    """
    @staticmethod
    def create_user(
        username: str,
        email: str,
        age: int,
        role: str
    ) -> Tuple[Optional[User], Optional[ErrorResponse]]:
        """Create a new user in the database.
        
        Args:
            username (str): The username for the new user.
            email (str): The email address for the new user.
            age (int): The age of the user.
            role (str): The role of the user in the system.
            
        Returns:
            tuple: A tuple containing (User, None) on success or (None, ErrorResponse) on failure.
        """
        try:
            # Check if user with same username already exists
            existing_user = db.session.query(User).filter(User.username == username).first()
            if existing_user:
                return None, ErrorResponseBuilder.already_exists("User", "username", username)
            
            # Check if user with same email already exists
            existing_user = db.session.query(User).filter(User.email == email).first()
            if existing_user:
                return None, ErrorResponseBuilder.already_exists("User", "email", email)
            
            user = User(
                username=username,
                email=email,
                age=age,
                role=role,
            )
            db.session.add(user)
            db.session.commit()
            return user, None
            
        except IntegrityError as e:
            db.session.rollback()
            # Handle specific database constraints
            error_msg = str(e.orig)
            if "username" in error_msg.lower():
                return None, ErrorResponseBuilder.constraint_violation(
                    "unique_username", 
                    f"Username '{username}' is already taken"
                )
            elif "email" in error_msg.lower():
                return None, ErrorResponseBuilder.constraint_violation(
                    "unique_email", 
                    f"Email '{email}' is already registered"
                )
            else:
                return None, ErrorResponseBuilder.constraint_violation(
                    "unknown_constraint", 
                    "A database constraint was violated"
                )
                
        except DatabaseError as e:
            db.session.rollback()
            return None, ErrorResponseBuilder.database_error(
                "Failed to create user due to database error"
            )
            
        except Exception as e:
            db.session.rollback()
            return None, ErrorResponseBuilder.internal_server_error(
                "An unexpected error occurred while creating the user"
            )
        
    @staticmethod
    def get_user(id: int) -> Optional[User]:
        """Get a user by their ID.
        
        Args:
            id (int): The ID of the user to retrieve.
            
        Returns:
            User or None: The User object if found, None otherwise.
        """
        try:
            return db.session.get(User, id)
        except DatabaseError:
            # For read operations, we don't need to return error responses
            # as the route handler will check for None and return appropriate error
            return None
    
    @staticmethod
    def get_all_users() -> list[User]:
        """Get all users from the database.
        
        Returns:
            list[User]: A list of all User objects in the database.
        """
        try:
            return db.session.query(User).all()
        except DatabaseError:
            # Return empty list if database error occurs
            return []
        
    @staticmethod
    def get_users_by_role(role: str) -> list[User]:
        """Get all users with a specific role.
        
        Args:
            role (str): The role to filter users by.
            
        Returns:
            list[User]: A list of User objects with the specified role.
        """
        try:
            return db.session.query(User).filter(User.role == role).all()
        except DatabaseError:
            # Return empty list if database error occurs
            return []

    @staticmethod
    def delete_user(id: int) -> Tuple[bool, Optional[ErrorResponse]]:
        """Delete a user by their ID.
        
        Args:
            id (int): The ID of the user to delete.
            
        Returns:
            tuple: A tuple containing (True, None) on success or (False, ErrorResponse) on failure.
        """
        try:
            user = db.session.get(User, id)
            if not user:
                return False, ErrorResponseBuilder.not_found("User", id)
            
            db.session.delete(user)
            db.session.commit()
            return True, None
            
        except DatabaseError as e:
            db.session.rollback()
            return False, ErrorResponseBuilder.database_error(
                "Failed to delete user due to database error"
            )
            
        except Exception as e:
            db.session.rollback()
            return False, ErrorResponseBuilder.internal_server_error(
                "An unexpected error occurred while deleting the user"
            )
