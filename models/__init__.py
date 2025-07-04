from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base class for SQLAlchemy models.
    
    This class serves as the declarative base for all database models
    in the application, providing common functionality and configuration.
    """
    pass

db = SQLAlchemy(model_class=Base)
