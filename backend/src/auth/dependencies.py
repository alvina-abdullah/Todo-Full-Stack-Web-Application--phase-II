"""
FastAPI dependencies for authentication and authorization.
"""

import logging
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .jwt import verify_token

# Configure logger
logger = logging.getLogger(__name__)

# Security scheme for extracting Bearer tokens from Authorization header
security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> str:
    """
    FastAPI dependency to extract and verify the current authenticated user.

    This dependency:
    1. Extracts the JWT token from the Authorization header (Bearer scheme)
    2. Verifies the token signature and expiration
    3. Returns the authenticated user ID

    Args:
        credentials: HTTP Bearer credentials automatically extracted by FastAPI

    Returns:
        The authenticated user ID (string)

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired

    Usage:
        @app.get("/protected")
        async def protected_route(user_id: Annotated[str, Depends(get_current_user)]):
            # user_id is now available and verified
            return {"user_id": user_id}
    """
    token = credentials.credentials

    if not token:
        logger.warning("Authentication failed: Missing token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Verify token and extract user ID
        user_id = verify_token(token)
        logger.info(f"Authentication successful: user_id={user_id}")
        return user_id
    except HTTPException as e:
        logger.warning(f"Authentication failed: {e.detail}")
        raise
