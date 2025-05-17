"""
Unit tests for Supabase authentication utilities.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from jose import jwt

from apps.core.core.config import Settings
from apps.core.lib.auth.supabase_auth import (
    AuthenticatedUser,
    get_current_user,
    oauth2_scheme,
)


@pytest.fixture
def mock_settings():
    """Create a mock settings object with JWT configuration."""
    settings = Settings()
    settings.SUPABASE_JWT_SECRET = "test_secret_key"
    settings.ALGORITHM = "HS256"
    return settings


@pytest.fixture
def valid_token_payload():
    """Create a valid token payload."""
    return {
        "sub": "user-id-123",
        "email": "test@example.com",
        "aud": "authenticated",
        "exp": datetime.utcnow() + timedelta(minutes=15),
    }


@pytest.fixture
def valid_jwt(valid_token_payload, mock_settings):
    """Create a valid JWT token."""
    with patch("apps.core.lib.auth.supabase_auth.settings", mock_settings):
        return jwt.encode(
            valid_token_payload,
            mock_settings.SUPABASE_JWT_SECRET,
            algorithm=mock_settings.ALGORITHM,
        )


class TestAuthenticatedUser:
    """Test cases for the AuthenticatedUser model."""

    def test_authenticated_user_model(self):
        """Test creating an AuthenticatedUser instance."""
        user = AuthenticatedUser(
            id="user-id-123", email="test@example.com", aud="authenticated"
        )

        assert user.id == "user-id-123"
        assert user.email == "test@example.com"
        assert user.aud == "authenticated"

    def test_authenticated_user_optional_fields(self):
        """Test creating an AuthenticatedUser with only required fields."""
        user = AuthenticatedUser(id="user-id-456")

        assert user.id == "user-id-456"
        assert user.email is None
        assert user.aud is None


class TestGetCurrentUser:
    """Test cases for the get_current_user function."""

    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(
        self, valid_jwt, mock_settings, valid_token_payload
    ):
        """Test getting the current user with a valid token."""
        with patch("apps.core.lib.auth.supabase_auth.settings", mock_settings):
            user = await get_current_user(valid_jwt)

            assert user.id == valid_token_payload["sub"]
            assert user.email == valid_token_payload["email"]
            assert user.aud == valid_token_payload["aud"]

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, mock_settings):
        """Test getting the current user with an invalid token."""
        with patch("apps.core.lib.auth.supabase_auth.settings", mock_settings):
            with pytest.raises(HTTPException) as excinfo:
                await get_current_user("invalid_token")

            assert excinfo.value.status_code == 401
            assert "Could not validate Supabase credentials" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_missing_sub(self, mock_settings):
        """Test getting the current user with a token missing the 'sub' claim."""
        # Create a token without the 'sub' claim
        payload = {
            "email": "test@example.com",
            "aud": "authenticated",
            "exp": datetime.utcnow() + timedelta(minutes=15),
        }
        token = jwt.encode(
            payload,
            mock_settings.SUPABASE_JWT_SECRET,
            algorithm=mock_settings.ALGORITHM,
        )

        with patch("apps.core.lib.auth.supabase_auth.settings", mock_settings):
            with pytest.raises(HTTPException) as excinfo:
                await get_current_user(token)

            assert excinfo.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_expired_token(self, mock_settings):
        """Test getting the current user with an expired token."""
        # Create an expired token
        payload = {
            "sub": "user-id-123",
            "email": "test@example.com",
            "aud": "authenticated",
            "exp": datetime.utcnow() - timedelta(minutes=15),  # Expired 15 minutes ago
        }
        token = jwt.encode(
            payload,
            mock_settings.SUPABASE_JWT_SECRET,
            algorithm=mock_settings.ALGORITHM,
        )

        with patch("apps.core.lib.auth.supabase_auth.settings", mock_settings):
            with pytest.raises(HTTPException) as excinfo:
                await get_current_user(token)

            assert excinfo.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_wrong_audience(self, mock_settings):
        """Test getting the current user with a token having the wrong audience."""
        # Create a token with a wrong audience
        payload = {
            "sub": "user-id-123",
            "email": "test@example.com",
            "aud": "wrong-audience",
            "exp": datetime.utcnow() + timedelta(minutes=15),
        }
        token = jwt.encode(
            payload,
            mock_settings.SUPABASE_JWT_SECRET,
            algorithm=mock_settings.ALGORITHM,
        )

        with patch("apps.core.lib.auth.supabase_auth.settings", mock_settings):
            with pytest.raises(HTTPException) as excinfo:
                await get_current_user(token)

            assert excinfo.value.status_code == 401

    @pytest.mark.asyncio
    async def test_oauth2_scheme_dependency(self, valid_jwt):
        """Test that the oauth2_scheme dependency is used correctly."""
        # Mock the OAuth2PasswordBearer to return our valid JWT
        mock_oauth2 = AsyncMock(return_value=valid_jwt)

        # Test the get_current_user function with the mocked dependency
        with patch("apps.core.lib.auth.supabase_auth.oauth2_scheme", mock_oauth2):
            # This will pass our valid JWT to get_current_user
            user = await get_current_user()

            # We expect oauth2_scheme to be called
            mock_oauth2.assert_called_once()
