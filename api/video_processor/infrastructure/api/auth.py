"""Authentication and authorization for the API."""

import os
import time
from typing import Any, Callable, Dict, List, Optional

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from pydantic import BaseModel

# Security scheme for Swagger UI
security_scheme = HTTPBearer(
    scheme_name="Bearer Authentication",
    description="Enter JWT token",
    auto_error=False,
)


class TokenPayload(BaseModel):
    """JWT token payload."""

    sub: str  # Subject (user ID)
    iat: int  # Issued at
    exp: int  # Expiration time
    role: str  # User role
    scopes: List[str]  # Authorized scopes


class AuthConfig:
    """Authentication configuration."""

    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: str = "HS256",
        token_expire_minutes: int = 60 * 24,  # 24 hours
        api_key_header_name: str = "X-API-Key",
    ):
        """Initialize authentication configuration.

        Args:
            secret_key: JWT secret key (defaults to environment variable)
            algorithm: JWT algorithm
            token_expire_minutes: Token expiration time in minutes
            api_key_header_name: Name of the header for API key
        """
        self.secret_key = secret_key or os.environ.get("JWT_SECRET_KEY", "")
        if not self.secret_key:
            raise ValueError("JWT_SECRET_KEY not set")

        self.algorithm = algorithm
        self.token_expire_minutes = token_expire_minutes
        self.api_key_header_name = api_key_header_name

        # API keys (in production, these should be stored in a database or secret manager)
        self._api_keys = {}


class Auth:
    """Authentication and authorization handler."""

    def __init__(self, config: AuthConfig):
        """Initialize authentication handler.

        Args:
            config: Authentication configuration
        """
        self.config = config

    def create_access_token(
        self, user_id: str, role: str = "user", scopes: Optional[List[str]] = None
    ) -> str:
        """Create a new JWT access token.

        Args:
            user_id: User ID
            role: User role (default: "user")
            scopes: Authorized scopes

        Returns:
            JWT token string
        """
        if scopes is None:
            scopes = []

        expiration = int(time.time() + self.config.token_expire_minutes * 60)

        payload = {
            "sub": user_id,
            "iat": int(time.time()),
            "exp": expiration,
            "role": role,
            "scopes": scopes,
        }

        return jwt.encode(
            payload, self.config.secret_key, algorithm=self.config.algorithm
        )

    def verify_token(self, token: str) -> TokenPayload:
        """Verify JWT token and return payload.

        Args:
            token: JWT token string

        Returns:
            Token payload

        Raises:
            HTTPException: If token is invalid
        """
        try:
            payload = jwt.decode(
                token, self.config.secret_key, algorithms=[self.config.algorithm]
            )

            return TokenPayload(**payload)

        except jwt.ExpiredSignatureError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e

        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e

    def register_api_key(self, api_key: str, user_id: str, role: str = "api") -> None:
        """Register a new API key.

        Args:
            api_key: API key
            user_id: User ID
            role: User role (default: "api")
        """
        self.config._api_keys[api_key] = {
            "user_id": user_id,
            "role": role,
        }

    def verify_api_key(self, api_key: str) -> Dict[str, str]:
        """Verify API key and return user info.

        Args:
            api_key: API key

        Returns:
            User info (user_id and role)

        Raises:
            HTTPException: If API key is invalid
        """
        if api_key not in self.config._api_keys:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )

        return self.config._api_keys[api_key]


# Create auth handler with default configuration
auth_config = AuthConfig()
auth = Auth(auth_config)


def get_auth_from_request(request: Request) -> Dict[str, Any]:
    """Get authentication info from request.

    Attempts to get authentication from:
    1. Bearer token in Authorization header
    2. API key in X-API-Key header

    Args:
        request: FastAPI request

    Returns:
        Authentication info

    Raises:
        HTTPException: If authentication is invalid or missing
    """
    # Try to get Bearer token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        payload = auth.verify_token(token)
        return {
            "user_id": payload.sub,
            "role": payload.role,
            "scopes": payload.scopes,
            "auth_method": "jwt",
        }

    # Try to get API key
    api_key = request.headers.get(auth_config.api_key_header_name)
    if api_key:
        user_info = auth.verify_api_key(api_key)
        return {
            "user_id": user_info["user_id"],
            "role": user_info["role"],
            "scopes": [],
            "auth_method": "api_key",
        }

    # No authentication provided
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    request: Request = None,
) -> Dict[str, Any]:
    """
    Dependency for getting the current user from a Supabase JWT token.

    Args:
        credentials: HTTP Bearer credentials
        request: FastAPI request (for API key)

    Returns:
        User info

    Raises:
        HTTPException: If authentication is invalid or missing
    """
    if not credentials:
        # If no Bearer token, try API key
        if request:
            return get_auth_from_request(request)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )

    token = credentials.credentials

    # Supabase project reference (from env)
    supabase_project_id = os.environ.get("SUPABASE_PROJECT_ID")
    supabase_jwks_url = os.environ.get(
        "SUPABASE_JWKS_URL",
        (
            f"https://{supabase_project_id}.supabase.co/auth/v1/keys"
            if supabase_project_id
            else None
        ),
    )
    if not supabase_jwks_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Supabase JWKs URL not configured. "
                "Set SUPABASE_PROJECT_ID or SUPABASE_JWKS_URL."
            ),
        )

    try:
        jwk_client = PyJWKClient(supabase_jwks_url)
        signing_key = jwk_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=None,  # Optionally set audience if required
            options={"verify_aud": False},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Supabase JWT: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    # Return a user dict with at least id and email if present
    user_id = payload.get("sub")
    email = payload.get("email")
    role = payload.get("role", "authenticated")
    return {
        "id": user_id,
        "email": email,
        "role": role,
        "provider": payload.get("provider"),
        "raw_claims": payload,
    }


def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Dependency for getting the current active user.

    Args:
        current_user: Current user info

    Returns:
        User info

    Raises:
        HTTPException: If user is inactive
    """
    # In a real application, check if user is active in database
    return current_user


def require_role(allowed_roles: List[str]) -> Callable:
    """Dependency factory for role-based access control.

    Args:
        allowed_roles: List of allowed roles

    Returns:
        Dependency function
    """

    def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_active_user),
    ) -> Dict[str, Any]:
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {current_user['role']} not authorized",
            )
        return current_user

    return role_checker


def require_scope(required_scope: str) -> Callable:
    """Dependency factory for scope-based access control.

    Args:
        required_scope: Required scope

    Returns:
        Dependency function
    """

    def scope_checker(
        current_user: Dict[str, Any] = Depends(get_current_active_user),
    ) -> Dict[str, Any]:
        if "scopes" not in current_user or required_scope not in current_user["scopes"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Scope {required_scope} required",
            )
        return current_user

    return scope_checker


# Pre-defined roles for common use cases
require_admin = require_role(["admin"])
require_user = require_role(["user", "admin"])
require_api = require_role(["api", "admin"])
