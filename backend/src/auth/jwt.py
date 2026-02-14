"""
JWT token verification and decoding utilities.
"""

import os
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from fastapi import HTTPException, status

# Load secret from environment
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
if not BETTER_AUTH_SECRET:
    raise ValueError("BETTER_AUTH_SECRET environment variable is not set")

# JWT algorithm used by Better Auth
ALGORITHM = "HS256"


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and verify a JWT token.

    Args:
        token: The JWT token string to decode

    Returns:
        Dict containing the token payload

    Raises:
        HTTPException: If token is invalid, expired, or malformed
    """
    try:
        payload = jwt.decode(
            token,
            BETTER_AUTH_SECRET,
            algorithms=[ALGORITHM]
        )
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        # Handle invalid token, wrong signature, malformed token, etc.
        error_msg = str(e)
        if "Signature verification failed" in error_msg:
            detail = "Token signature verification failed"
        elif "Invalid" in error_msg:
            detail = "Invalid token"
        else:
            detail = "Could not validate credentials"

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_token(token: str) -> Optional[str]:
    """
    Verify a JWT token and extract the user ID.

    Args:
        token: The JWT token string to verify

    Returns:
        The user ID (sub claim) if token is valid, None otherwise

    Raises:
        HTTPException: If token is invalid or expired
    """
    payload = decode_token(token)

    # Extract user ID from 'sub' claim (standard JWT claim for subject/user ID)
    user_id: Optional[str] = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id
