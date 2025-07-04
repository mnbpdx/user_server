from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum


class ErrorCode(str, Enum):
    """Standardized error codes for the API."""
    
    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_DATA_TYPE = "INVALID_DATA_TYPE"
    INVALID_FORMAT = "INVALID_FORMAT"
    VALUE_TOO_SHORT = "VALUE_TOO_SHORT"
    VALUE_TOO_LONG = "VALUE_TOO_LONG"
    VALUE_OUT_OF_RANGE = "VALUE_OUT_OF_RANGE"
    
    # Resource errors
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    
    # Database errors
    DATABASE_ERROR = "DATABASE_ERROR"
    CONSTRAINT_VIOLATION = "CONSTRAINT_VIOLATION"
    
    # Request errors
    INVALID_JSON = "INVALID_JSON"
    MISSING_CONTENT_TYPE = "MISSING_CONTENT_TYPE"
    
    # Internal errors
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"


class FieldError(BaseModel):
    """Schema for field-specific error details."""
    
    field: str
    message: str
    code: ErrorCode
    value: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Standardized error response schema."""
    
    error: str
    code: ErrorCode
    message: str
    details: Optional[List[FieldError]] = None
    request_id: Optional[str] = None


class ErrorResponseBuilder:
    """Builder class for creating standardized error responses."""
    
    @staticmethod
    def validation_error(message: str, field_errors: List[FieldError] = None) -> ErrorResponse:
        """Create a validation error response."""
        return ErrorResponse(
            error="Validation Error",
            code=ErrorCode.VALIDATION_ERROR,
            message=message,
            details=field_errors or []
        )
    
    @staticmethod
    def not_found(resource_type: str, resource_id: Any = None) -> ErrorResponse:
        """Create a not found error response."""
        message = f"{resource_type} not found"
        if resource_id is not None:
            message += f" with id: {resource_id}"
        
        return ErrorResponse(
            error="Resource Not Found",
            code=ErrorCode.RESOURCE_NOT_FOUND,
            message=message
        )
    
    @staticmethod
    def already_exists(resource_type: str, field: str, value: Any) -> ErrorResponse:
        """Create an already exists error response."""
        return ErrorResponse(
            error="Resource Already Exists",
            code=ErrorCode.RESOURCE_ALREADY_EXISTS,
            message=f"{resource_type} already exists with {field}: {value}"
        )
    
    @staticmethod
    def database_error(message: str = "Database operation failed") -> ErrorResponse:
        """Create a database error response."""
        return ErrorResponse(
            error="Database Error",
            code=ErrorCode.DATABASE_ERROR,
            message=message
        )
    
    @staticmethod
    def constraint_violation(constraint_name: str, message: str = None) -> ErrorResponse:
        """Create a constraint violation error response."""
        error_message = message or f"Database constraint violation: {constraint_name}"
        return ErrorResponse(
            error="Constraint Violation",
            code=ErrorCode.CONSTRAINT_VIOLATION,
            message=error_message
        )
    
    @staticmethod
    def invalid_json(message: str = "Invalid JSON in request body") -> ErrorResponse:
        """Create an invalid JSON error response."""
        return ErrorResponse(
            error="Invalid JSON",
            code=ErrorCode.INVALID_JSON,
            message=message
        )
    
    @staticmethod
    def internal_server_error(message: str = "An internal server error occurred") -> ErrorResponse:
        """Create an internal server error response."""
        return ErrorResponse(
            error="Internal Server Error",
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            message=message
        )
    
    @staticmethod
    def pydantic_validation_error(validation_error) -> ErrorResponse:
        """Convert Pydantic validation error to standardized error response."""
        field_errors = []
        
        for error in validation_error.errors():
            field_path = '.'.join(str(loc) for loc in error['loc'])
            error_type = error['type']
            error_msg = error['msg']
            input_value = error.get('input')
            
            # Map Pydantic error types to our error codes
            if error_type == 'missing':
                code = ErrorCode.MISSING_REQUIRED_FIELD
            elif error_type in ['string_too_short', 'too_short']:
                code = ErrorCode.VALUE_TOO_SHORT
            elif error_type in ['string_too_long', 'too_long']:
                code = ErrorCode.VALUE_TOO_LONG
            elif error_type in ['int_parsing', 'float_parsing', 'bool_parsing']:
                code = ErrorCode.INVALID_DATA_TYPE
            elif error_type == 'string_type':
                code = ErrorCode.INVALID_DATA_TYPE
            elif error_type == 'int_type':
                code = ErrorCode.INVALID_DATA_TYPE
            elif error_type == 'value_error':
                code = ErrorCode.INVALID_FORMAT
            else:
                code = ErrorCode.VALIDATION_ERROR
            
            field_errors.append(FieldError(
                field=field_path,
                message=error_msg,
                code=code,
                value=input_value
            ))
        
        return ErrorResponse(
            error="Validation Error",
            code=ErrorCode.VALIDATION_ERROR,
            message="Request validation failed",
            details=field_errors
        ) 