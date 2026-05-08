"""Authentication routes."""
from fastapi import APIRouter, HTTPException, status, Header
from typing import Optional
import logging
from datetime import datetime

from app.models.user import LoginRequest, TokenResponse
from app.auth.jwt_handler import create_access_token, verify_token
from app.auth.password import verify_password
from app.database.connection import get_database

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


def get_admin_users_collection():
    """Get the admin_users collection."""
    db = get_database()
    return db["admin_users"]


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """
    Authenticate user and return JWT token.
    
    - **username**: Admin username
    - **password**: Admin password
    
    Returns JWT token valid for 1 hour.
    """
    try:
        collection = get_admin_users_collection()
        
        # Find user by username
        user = collection.find_one({"username": credentials.username, "is_active": True})
        
        if not user:
            logger.warning(f"Login attempt for non-existent user: {credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Verify password
        if not verify_password(credentials.password, user["password_hash"]):
            logger.warning(f"Invalid password for user: {credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Update last login
        collection.update_one(
            {"username": credentials.username},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        # Create access token
        access_token = create_access_token(data={"sub": credentials.username})
        
        logger.info(f"User logged in successfully: {credentials.username}")
        
        return TokenResponse(
            access_token=access_token,
            username=credentials.username
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.get("/verify")
async def verify(authorization: Optional[str] = Header(None)):
    """
    Verify JWT token and return user info.
    
    - **Authorization**: Bearer token in header
    
    Returns user information if token is valid.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid authentication scheme")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    # Verify token
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return {
        "username": payload["username"],
        "authenticated": True
    }


@router.post("/logout")
async def logout():
    """
    Logout endpoint (client-side token deletion).
    
    Returns success message.
    """
    return {"message": "Logged out successfully"}
