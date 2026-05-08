"""Authentication middleware for protecting routes."""
from fastapi import Request, HTTPException, status
from typing import Callable
from app.auth.jwt_handler import verify_token


async def verify_auth_token(request: Request, call_next: Callable):
    """
    Middleware to verify JWT tokens for protected routes.
    """
    # Skip authentication for OPTIONS requests (CORS preflight)
    if request.method == "OPTIONS":
        response = await call_next(request)
        return response
    
    # Skip authentication for these paths
    public_paths = ["/", "/health", "/docs", "/redoc", "/openapi.json"]
    
    # Allow public paths and all auth routes
    if request.url.path in public_paths or request.url.path.startswith("/api/auth"):
        response = await call_next(request)
        return response
    
    # Check for authorization header (case-insensitive)
    authorization = request.headers.get("authorization") or request.headers.get("Authorization")
    
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    # Extract and verify token
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid authentication scheme")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Add user info to request state
    request.state.user = payload
    
    response = await call_next(request)
    return response
