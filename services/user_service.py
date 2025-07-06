from models import db
from models.user import User
from sqlalchemy.exc import IntegrityError, DatabaseError
from schemas.error_schemas import ErrorResponse, ErrorResponseBuilder
from typing import Tuple, Optional, Dict, Any
from functools import wraps
import inspect


def handle_database_errors(operation_name: str):
    """Decorator to handle common database errors in service methods.
    
    Args:
        operation_name (str): Name of the operation for error messages.
        
    Returns:
        Decorator function that handles database errors.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except IntegrityError as e:
                db.session.rollback()
                # Handle specific database constraints
                error_msg = str(e.orig)
                
                # Get function signature to extract username/email from args
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                if "username" in error_msg.lower():
                    username = bound_args.arguments.get('username') or (
                        bound_args.arguments.get('update_data', {}).get('username') if 'update_data' in bound_args.arguments else None
                    )
                    return None, ErrorResponseBuilder.already_exists("User", "username", username) if username else ErrorResponseBuilder.already_exists("User", "username", "unknown")
                elif "email" in error_msg.lower():
                    email = bound_args.arguments.get('email') or (
                        bound_args.arguments.get('update_data', {}).get('email') if 'update_data' in bound_args.arguments else None
                    )
                    return None, ErrorResponseBuilder.already_exists("User", "email", email) if email else ErrorResponseBuilder.already_exists("User", "email", "unknown")
                else:
                    return None, ErrorResponseBuilder.constraint_violation(
                        "unknown_constraint", 
                        "A database constraint was violated"
                    )
            except DatabaseError as e:
                db.session.rollback()
                return None, ErrorResponseBuilder.database_error(
                    f"Failed to {operation_name} due to database error"
                )
            except Exception as e:
                db.session.rollback()
                return None, ErrorResponseBuilder.internal_server_error(
                    f"An unexpected error occurred while {operation_name}"
                )
        return wrapper
    return decorator


class UserService:
    """Service class for user-related operations.
    
    This class provides static methods for CRUD operations on User entities,
    handling database interactions and structured error management.
    """
    
    @staticmethod
    @handle_database_errors("creating user")
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
        user = User(
            username=username,
            email=email,
            age=age,
            role=role,
        )
        db.session.add(user)
        db.session.commit()
        return user, None
    
    @staticmethod
    @handle_database_errors("updating user")
    def update_user(
        id: int,
        update_data: Dict[str, Any]
    ) -> Tuple[Optional[User], Optional[ErrorResponse]]:
        """Update an existing user in the database.
        
        Args:
            id (int): The ID of the user to update.
            update_data (Dict[str, Any]): Dictionary of fields to update.
            
        Returns:
            tuple: A tuple containing (User, None) on success or (None, ErrorResponse) on failure.
        """
        # Get the user to update
        user = db.session.get(User, id)
        if not user:
            return None, ErrorResponseBuilder.not_found("User", id)
        
        # Update the user's fields
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        db.session.commit()
        return user, None
        
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
