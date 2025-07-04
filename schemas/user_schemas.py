from pydantic import BaseModel, ConfigDict

class UserCreateSchema(BaseModel):
    """Schema for creating a new user.
    
    This schema validates the input data when creating a new user.
    The ID is auto-generated and not included in this schema.
    
    Attributes:
        username (str): The username for the new user.
        email (str): The email address for the new user.
        age (int): The age of the user.
        role (str): The role of the user in the system.
    """
    username: str
    email: str
    age: int
    role: str

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
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    email: str
    age: int
    role: str

class UserResponseSchema(BaseModel):
    """Schema for API responses containing multiple users.
    
    This schema wraps a list of users in a structured response format.
    
    Attributes:
        users (list[UserSchema]): A list of user objects.
    """
    users: list[UserSchema]
