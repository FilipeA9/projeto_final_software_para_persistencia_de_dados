"""
Pydantic schemas for authentication requests and responses.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator


class UserRegisterRequest(BaseModel):
    """Schema for user registration request."""
    login: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    
    @validator("login")
    def validate_login(cls, v):
        """Validate login contains only allowed characters."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Login must contain only letters, numbers, hyphens, and underscores")
        return v.lower()
    
    @validator("password")
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v


class UserLoginRequest(BaseModel):
    """Schema for user login request."""
    login: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    """Schema for user data in responses."""
    id: int
    login: str
    email: str
    role: str
    created_at: str


class AuthResponse(BaseModel):
    """Schema for authentication response (login/register)."""
    user: UserResponse
    access_token: str
    token_type: str = "bearer"


class LogoutResponse(BaseModel):
    """Schema for logout response."""
    message: str
    success: bool
