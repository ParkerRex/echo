"""
supabase_auth.py: Supabase authentication utilities for Echo backend.

- Provides AuthenticatedUser Pydantic model.
- Provides get_current_user FastAPI dependency for JWT validation.
- Designed for use in the infrastructure/lib layer.

Directory: apps/core/lib/auth/supabase_auth.py
Layer: Infrastructure/Lib
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from apps.core.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AuthenticatedUser(BaseModel):
    id: str
    email: Optional[str] = None
    aud: Optional[str] = None


async def get_current_user(token: str = Depends(oauth2_scheme)) -> AuthenticatedUser:
    """
    FastAPI dependency to extract and validate the current user from a Supabase JWT.

    Args:
        token (str): JWT token from the Authorization header.

    Returns:
        AuthenticatedUser: The authenticated user.

    Raises:
        HTTPException: If the token is invalid or missing required claims.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate Supabase credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=[settings.ALGORITHM],
            audience="authenticated",
        )
        user_id = payload.get("sub")
        email: Optional[str] = payload.get("email")
        aud: Optional[str] = payload.get("aud")
        if user_id is None:
            raise credentials_exception
        return AuthenticatedUser(id=str(user_id), email=email, aud=aud)
    except JWTError:
        raise credentials_exception
