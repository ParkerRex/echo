"""
Unit tests for the UserService.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from apps.core.lib.auth.supabase_auth import AuthenticatedUser
from apps.core.models.user_model import User
from apps.core.operations.user_repository import UserRepository
from apps.core.services.user_service import UserService


@pytest.fixture
def mock_user_repository():
    """Create a mock UserRepository."""
    return MagicMock(spec=UserRepository)


@pytest.fixture
def user_service(mock_user_repository):
    """Create a UserService instance with mock dependencies."""
    return UserService(mock_user_repository)


@pytest.fixture
def mock_db():
    """Mock SQLAlchemy Session."""
    return MagicMock(spec=Session)


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "is_active": True,
    }


@pytest.fixture
def sample_user(sample_user_data):
    """Create a sample User model instance."""
    user = MagicMock(spec=User)
    for key, value in sample_user_data.items():
        setattr(user, key, value)
    user.hashed_password = "hashed_password"  # Add hashed_password
    return user


@pytest.fixture
def auth_user():
    """Create a sample AuthenticatedUser."""
    return AuthenticatedUser(
        id="auth123",
        email="test@example.com",
        aud="authenticated",
    )


class TestUserService:
    """Test cases for the UserService class."""

    def test_get_user_profile_found(
        self, user_service, mock_user_repository, sample_user
    ):
        """Test getting a user profile when the user exists."""
        # Set up mock return
        mock_user_repository.get_user.return_value = sample_user

        # Call the service method
        user_profile = user_service.get_user_profile(1)

        # Verify results
        assert user_profile["id"] == sample_user.id
        assert user_profile["username"] == sample_user.username
        assert user_profile["email"] == sample_user.email
        assert user_profile["full_name"] == sample_user.full_name
        assert user_profile["is_active"] == sample_user.is_active
        assert "hashed_password" not in user_profile  # Sensitive info excluded

        # Verify repository call
        mock_user_repository.get_user.assert_called_once_with(1)

    def test_get_user_profile_not_found(self, user_service, mock_user_repository):
        """Test getting a user profile when the user doesn't exist."""
        # Set up mock return
        mock_user_repository.get_user.return_value = None

        # Call the service method and expect exception
        with pytest.raises(HTTPException) as excinfo:
            user_service.get_user_profile(999)

        # Verify exception
        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == "User not found"

        # Verify repository call
        mock_user_repository.get_user.assert_called_once_with(999)

    def test_get_or_create_user_profile_existing(
        self, user_service, mock_user_repository, mock_db, sample_user, auth_user
    ):
        """Test getting an existing user profile."""
        # Set up mock return
        mock_user_repository.get_user_by_email.return_value = sample_user

        # Call the service method
        result = user_service.get_or_create_user_profile(mock_db, auth_user)

        # Verify results
        assert result is sample_user

        # Verify repository calls
        mock_user_repository.get_user_by_email.assert_called_once_with(auth_user.email)
        mock_user_repository.create_user.assert_not_called()

    def test_get_or_create_user_profile_new(
        self, user_service, mock_user_repository, mock_db, sample_user, auth_user
    ):
        """Test creating a new user profile."""
        # Set up mock returns
        mock_user_repository.get_user_by_email.return_value = None
        mock_user_repository.create_user.return_value = sample_user

        # Call the service method
        result = user_service.get_or_create_user_profile(mock_db, auth_user)

        # Verify results
        assert result is sample_user

        # Verify repository calls
        mock_user_repository.get_user_by_email.assert_called_once_with(auth_user.email)
        mock_user_repository.create_user.assert_called_once()

        # Verify the created user data
        created_user_data = mock_user_repository.create_user.call_args[0][0]
        assert created_user_data["username"] == "test"  # from test@example.com
        assert created_user_data["email"] == auth_user.email
        assert created_user_data["is_active"] is True
        assert created_user_data["hashed_password"] == ""  # Not used for Supabase auth

    def test_get_or_create_user_profile_no_email(
        self, user_service, mock_user_repository, mock_db
    ):
        """Test handling when auth_user has no email."""
        # Create auth user without email
        auth_user_no_email = AuthenticatedUser(
            id="auth123",
            email=None,
            aud="authenticated",
        )

        # Call the service method and expect exception
        with pytest.raises(HTTPException) as excinfo:
            user_service.get_or_create_user_profile(mock_db, auth_user_no_email)

        # Verify exception
        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "Authenticated user missing email"

        # Verify repository not called
        mock_user_repository.get_user_by_email.assert_not_called()

    def test_get_or_create_user_profile_with_fallback_username(
        self, user_service, mock_user_repository, mock_db, sample_user
    ):
        """Test creating a user with fallback username when email has no @ symbol."""
        # Create auth user with unusual email (no @)
        auth_user_unusual_email = AuthenticatedUser(
            id="auth123",
            email="invalid-email",
            aud="authenticated",
        )

        # Set up mock returns
        mock_user_repository.get_user_by_email.return_value = None
        mock_user_repository.create_user.return_value = sample_user

        # Call the service method
        result = user_service.get_or_create_user_profile(
            mock_db, auth_user_unusual_email
        )

        # Verify results
        assert result is sample_user

        # Verify repository calls
        mock_user_repository.get_user_by_email.assert_called_once_with("invalid-email")
        mock_user_repository.create_user.assert_called_once()

        # Verify the created user data uses fallback username
        created_user_data = mock_user_repository.create_user.call_args[0][0]
        assert created_user_data["username"] == f"user_{auth_user_unusual_email.id}"
        assert created_user_data["email"] == "invalid-email"

    def test_create_user_success(
        self, user_service, mock_user_repository, sample_user, sample_user_data
    ):
        """Test creating a new user successfully."""
        # Set up mock returns for validation checks
        mock_user_repository.get_user_by_email.return_value = None
        mock_user_repository.get_user_by_username.return_value = None
        mock_user_repository.create_user.return_value = sample_user

        # Remove id as it's not part of input data
        user_input = sample_user_data.copy()
        del user_input["id"]
        user_input["hashed_password"] = "hashed_password"  # Add required field

        # Call the service method
        result = user_service.create_user(user_input)

        # Verify results
        assert result["id"] == sample_user.id
        assert result["username"] == sample_user.username
        assert result["email"] == sample_user.email
        assert result["full_name"] == sample_user.full_name
        assert result["is_active"] == sample_user.is_active
        assert "hashed_password" not in result  # Sensitive info excluded

        # Verify repository calls
        mock_user_repository.get_user_by_email.assert_called_once_with(
            sample_user_data["email"]
        )
        mock_user_repository.get_user_by_username.assert_called_once_with(
            sample_user_data["username"]
        )
        mock_user_repository.create_user.assert_called_once_with(user_input)

    def test_create_user_email_exists(
        self, user_service, mock_user_repository, sample_user, sample_user_data
    ):
        """Test creating a user with an email that already exists."""
        # Set up mock returns
        mock_user_repository.get_user_by_email.return_value = sample_user

        # Remove id as it's not part of input data
        user_input = sample_user_data.copy()
        del user_input["id"]

        # Call the service method and expect exception
        with pytest.raises(HTTPException) as excinfo:
            user_service.create_user(user_input)

        # Verify exception
        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "Email already registered"

        # Verify repository calls
        mock_user_repository.get_user_by_email.assert_called_once_with(
            sample_user_data["email"]
        )
        mock_user_repository.get_user_by_username.assert_not_called()
        mock_user_repository.create_user.assert_not_called()

    def test_create_user_username_exists(
        self, user_service, mock_user_repository, sample_user, sample_user_data
    ):
        """Test creating a user with a username that already exists."""
        # Set up mock returns
        mock_user_repository.get_user_by_email.return_value = None
        mock_user_repository.get_user_by_username.return_value = sample_user

        # Remove id as it's not part of input data
        user_input = sample_user_data.copy()
        del user_input["id"]

        # Call the service method and expect exception
        with pytest.raises(HTTPException) as excinfo:
            user_service.create_user(user_input)

        # Verify exception
        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "Username already taken"

        # Verify repository calls
        mock_user_repository.get_user_by_email.assert_called_once_with(
            sample_user_data["email"]
        )
        mock_user_repository.get_user_by_username.assert_called_once_with(
            sample_user_data["username"]
        )
        mock_user_repository.create_user.assert_not_called()

    def test_create_user_missing_email(self, user_service, mock_user_repository):
        """Test creating a user without an email."""
        # Create input data without email
        user_input = {
            "username": "testuser",
            "full_name": "Test User",
            "hashed_password": "hashed_password",
        }

        # Call the service method and expect exception
        with pytest.raises(HTTPException) as excinfo:
            user_service.create_user(user_input)

        # Verify exception
        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "Email is required"

        # Verify repository not called
        mock_user_repository.get_user_by_email.assert_not_called()

    def test_create_user_missing_username(self, user_service, mock_user_repository):
        """Test creating a user without a username."""
        # Create input data without username
        user_input = {
            "email": "test@example.com",
            "full_name": "Test User",
            "hashed_password": "hashed_password",
        }

        # Call the service method and expect exception
        with pytest.raises(HTTPException) as excinfo:
            user_service.create_user(user_input)

        # Verify exception
        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "Username is required"

        # Verify repository calls
        mock_user_repository.get_user_by_email.assert_called_once_with(
            "test@example.com"
        )
        mock_user_repository.get_user_by_username.assert_not_called()
        mock_user_repository.create_user.assert_not_called()
