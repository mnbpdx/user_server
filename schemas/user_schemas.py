from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class UserCreateSchema(BaseModel):
    """Schema for creating a new user.
    
    This schema validates the input data when creating a new user.
    The ID is auto-generated and not included in this schema.
    
    Attributes:
        username (str): The username for the new user. Must be 3-50 characters.
        email (str): The email address for the new user. Must be up to 100 characters.
        age (int): The age of the user.
        role (str): The role of the user in the system. Must be up to 20 characters.
    """
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(max_length=100)
    age: int
    role: str = Field(max_length=20)

class UserUpdateSchema(BaseModel):
    """Schema for updating an existing user.
    
    This schema validates the input data when updating a user.
    All fields are optional to support partial updates.
    
    Attributes:
        username (Optional[str]): The username for the user. Must be 3-50 characters if provided.
        email (Optional[str]): The email address for the user. Must be up to 100 characters if provided.
        age (Optional[int]): The age of the user if provided.
        role (Optional[str]): The role of the user in the system. Must be up to 20 characters if provided.
    """
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    age: Optional[int] = None
    role: Optional[str] = Field(None, max_length=20)

class UserSchema(BaseModel):
    """Schema for user data representation.
    
    This schema represents a complete user with all attributes,
    including the auto-generated ID. Used for API responses.
    
    Attributes:
        id (int): The unique identifier for the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        age (int): The age of the user.
        role (str): The role of the user in the system.
    """
    id: int
    username: str
    email: str
    age: int
    role: str
    
    model_config = ConfigDict(from_attributes=True)  # Allows conversion from SQLAlchemy models

class UserResponseSchema(BaseModel):
    """Schema for API responses containing multiple users.
    
    This schema wraps a list of users in a structured response format.
    
    Attributes:
        users (list[UserSchema]): A list of user objects.
    """
    users: list[UserSchema]
