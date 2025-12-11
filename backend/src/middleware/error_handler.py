"""
Error Handling Middleware - Centralized error handling for the application.

Provides consistent error responses and logging.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


async def http_error_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle HTTP exceptions with consistent format.
    
    Args:
        request: FastAPI request
        exc: HTTP exception
        
    Returns:
        JSON response with error details
    """
    logger.warning(
        f"HTTP {exc.status_code}: {exc.detail} - {request.method} {request.url}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "path": str(request.url),
            }
        },
    )


async def validation_error_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors with detailed field information.
    
    Args:
        request: FastAPI request
        exc: Validation error
        
    Returns:
        JSON response with validation errors
    """
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"],
        })
    
    logger.warning(
        f"Validation error on {request.method} {request.url}: {len(errors)} errors"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": 422,
                "message": "Validation error",
                "details": errors,
                "path": str(request.url),
            }
        },
    )


async def database_error_handler(request: Request, exc: SQLAlchemyError):
    """
    Handle database errors.
    
    Args:
        request: FastAPI request
        exc: SQLAlchemy error
        
    Returns:
        JSON response with generic error
    """
    logger.error(
        f"Database error on {request.method} {request.url}: {str(exc)}",
        exc_info=True,
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": 500,
                "message": "Database error occurred",
                "path": str(request.url),
            }
        },
    )


async def generic_error_handler(request: Request, exc: Exception):
    """
    Handle unexpected errors.
    
    Args:
        request: FastAPI request
        exc: Exception
        
    Returns:
        JSON response with generic error
    """
    logger.error(
        f"Unexpected error on {request.method} {request.url}: {str(exc)}",
        exc_info=True,
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": 500,
                "message": "An unexpected error occurred",
                "path": str(request.url),
            }
        },
    )


def setup_error_handlers(app):
    """
    Register error handlers with the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(SQLAlchemyError, database_error_handler)
    app.add_exception_handler(Exception, generic_error_handler)
