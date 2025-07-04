# Fake SQL database of users
class User:
    """Legacy User class for fake database.
    
    This appears to be a legacy implementation that creates fake user data.
    The actual User model is defined in models/user.py using SQLAlchemy.
    
    Args:
        id (int): User ID.
        username (str): Username.
        email (str): Email address.
        age (int): User age.
        role (str): User role.
    """
    def __init__(self, id, username, email, age, role):
        self.id = id
        self.username = username
        self.email = email
        self.age = age
        self.role = role

users_db = [
    User(1, "john_doe", "john@example.com", 30, "admin"),
    User(2, "jane_smith", "jane@example.com", 25, "user"),
    User(3, "bob_jackson", "bob@example.com", 42, "user"),
    User(4, "alice_wonder", "alice@example.com", 28, "user"),
    User(5, "sam_wilson", "sam@example.com", 35, "moderator"),
    User(6, "emma_stone", "emma@example.com", 31, "moderator")
] 
