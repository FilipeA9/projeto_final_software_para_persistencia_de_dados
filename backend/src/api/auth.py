"""
Auth API endpoints - User registration and authentication.

Implements POST endpoints for register, login, logout, and user info.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.postgres import get_db
from src.services.auth_service import AuthService
from src.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    AuthResponse,
    LogoutResponse,
    UserResponse,
)
from src.dependencies.auth import get_current_user
from src.models.usuario import Usuario

router = APIRouter()
security = HTTPBearer()


@router.post("/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account.
    
    **Request Body:**
    - `login`: Username (3-50 chars, alphanumeric + hyphens/underscores)
    - `email`: Valid email address
    - `password`: Password (minimum 6 characters)
    
    **Returns:**
    - User information
    - Access token (JWT) valid for 24 hours
    - Token type (bearer)
    
    **Errors:**
    - 400: Login or email already exists
    - 422: Validation error (invalid format)
    
    **Password Security:**
    - Passwords are hashed using bcrypt
    - Plain text passwords are never stored
    
    **Session:**
    - Session is automatically created in Redis
    - Token must be included in subsequent requests
    """
    auth_service = AuthService(db)
    
    try:
        result = await auth_service.register_user(
            login=user_data.login,
            email=user_data.email,
            password=user_data.password,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/auth/login", response_model=AuthResponse)
async def login(
    credentials: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Login with username/email and password.
    
    **Request Body:**
    - `login`: Username or email address
    - `password`: User password
    
    **Returns:**
    - User information
    - Access token (JWT) valid for 24 hours
    - Token type (bearer)
    
    **Errors:**
    - 401: Invalid credentials
    
    **Token Usage:**
    - Include token in Authorization header: `Bearer <token>`
    - Token expires after 24 hours
    - Use `/auth/logout` to invalidate token before expiration
    
    **Session:**
    - Previous sessions are replaced with new one
    - Only one active session per user
    """
    auth_service = AuthService(db)
    
    try:
        result = await auth_service.login(
            login=credentials.login,
            password=credentials.password,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/auth/logout", response_model=LogoutResponse)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Logout current user and invalidate session.
    
    **Authentication Required:**
    - Must include valid Bearer token in Authorization header
    
    **Returns:**
    - Success message
    
    **Effects:**
    - Session removed from Redis
    - Token added to blacklist
    - Subsequent requests with this token will fail
    
    **Note:**
    - Token remains invalid until natural expiration (24 hours)
    - User must login again to get new token
    """
    auth_service = AuthService(db)
    token = credentials.credentials
    
    success = await auth_service.logout(current_user.id, token)
    
    return {
        "message": "Logged out successfully",
        "success": success,
    }


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Usuario = Depends(get_current_user),
):
    """
    Get current authenticated user information.
    
    **Authentication Required:**
    - Must include valid Bearer token in Authorization header
    
    **Returns:**
    - User ID, login, email, role
    - Account creation timestamp
    
    **Use Case:**
    - Verify token is still valid
    - Get user profile information
    - Check user role for authorization
    
    **Errors:**
    - 401: Token invalid, expired, or blacklisted
    """
    return {
        "id": current_user.id,
        "login": current_user.login,
        "email": current_user.email,
        "role": current_user.role.value,
        "created_at": current_user.created_at.isoformat(),
    }
