"""
Admin User models for authentication.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AdminUserDB(BaseModel):
    """Admin user database model."""
    username: str
    password_hash: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert model to dictionary for MongoDB."""
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "last_login": self.last_login
        }


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    username: str
