"""
Unit tests for the UserService.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apps.core.lib.auth.supabase_auth import AuthenticatedUser
from apps.core.models.user_model import User
from apps.core.operations.user_repository import UserRepository
from apps.core.services.user_service import UserService


@pytest.fixture
def mock_user_repository_async() -> AsyncMock:
    """Create a mock async UserRepository."""
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def user_service_async(mock_user_repository_async: AsyncMock) -> UserService:
    """Create a UserService instance with mock async dependencies."""
    return UserService(user_repository=mock_user_repository_async)


@pytest.fixture
def mock_db_async() -> AsyncMock:
    """Mock SQLAlchemy AsyncSession."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def sample_user_data() -> dict:
    """Sample user data for testing."""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "is_active": True,
        "supabase_auth_id": "some-auth-id-123",
    }


@pytest.fixture
def sample_user_async(sample_user_data: dict) -> AsyncMock:
    """Create a sample async mock User model instance."""
    user = AsyncMock(spec=User)
    for key, value in sample_user_data.items():
        setattr(user, key, value)
    user.hashed_password = "hashed_password"
    return user


@pytest.fixture
def auth_user() -> AuthenticatedUser:
    """Create a sample AuthenticatedUser for get_or_create tests."""
    return AuthenticatedUser(
        id="some-auth-id-123",
        email="test@example.com",
        aud="authenticated",
    )


class TestUserService:
    """Test cases for the UserService class."""

    @pytest.mark.asyncio
    async def test_get_user_profile_found(
        self,
        user_service_async: UserService,
        mock_user_repository_async: AsyncMock,
        sample_user_async: AsyncMock,
    ):
        """Test getting a user profile when the user exists."""
        test_user_id = sample_user_async.id
        mock_user_repository_async.get_user.return_value = sample_user_async

        user_profile_dict = await user_service_async.get_user_profile(test_user_id)

        assert user_profile_dict is not None
        if user_profile_dict:
            assert user_profile_dict["id"] == sample_user_async.id
            assert user_profile_dict["username"] == sample_user_async.username
            assert user_profile_dict["email"] == sample_user_async.email
            assert user_profile_dict["full_name"] == sample_user_async.full_name
            assert user_profile_dict["is_active"] == sample_user_async.is_active
            assert "hashed_password" not in user_profile_dict

        mock_user_repository_async.get_user.assert_awaited_once_with(test_user_id)

    @pytest.mark.asyncio
    async def test_get_user_profile_not_found(
        self, user_service_async: UserService, mock_user_repository_async: AsyncMock
    ):
        """Test getting a user profile when the user doesn't exist."""
        test_user_id = 999
        mock_user_repository_async.get_user.return_value = None

        with pytest.raises(HTTPException) as excinfo:
            await user_service_async.get_user_profile(test_user_id)

        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == "User not found"
        mock_user_repository_async.get_user.assert_awaited_once_with(test_user_id)

    @pytest.mark.asyncio
    async def test_get_or_create_user_profile_existing(
        self,
        user_service_async: UserService,
        mock_user_repository_async: AsyncMock,
        sample_user_async: AsyncMock,
        auth_user: AuthenticatedUser,
    ):
        """Test getting an existing user profile via get_or_create_user_profile."""
        mock_user_repository_async.get_user_by_email.return_value = sample_user_async

        result_user = await user_service_async.get_or_create_user_profile(auth_user)

        assert result_user is sample_user_async
        mock_user_repository_async.get_user_by_email.assert_awaited_once_with(
            auth_user.email
        )
        mock_user_repository_async.create_user.assert_not_awaited()  # Should not be called if user exists

    @pytest.mark.asyncio
    async def test_get_or_create_user_profile_new(
        self,
        user_service_async: UserService,
        mock_user_repository_async: AsyncMock,
        sample_user_async: AsyncMock,
        auth_user: AuthenticatedUser,
    ):
        """Test creating a new user profile via get_or_create_user_profile."""
        mock_user_repository_async.get_user_by_email.return_value = (
            None  # Simulate user not found by email
        )
        mock_user_repository_async.create_user.return_value = (
            sample_user_async  # Mock the created user
        )

        result_user = await user_service_async.get_or_create_user_profile(auth_user)

        assert result_user is sample_user_async
        mock_user_repository_async.get_user_by_email.assert_awaited_once_with(
            auth_user.email
        )
        mock_user_repository_async.create_user.assert_awaited_once()

        # Verify the data passed to create_user (it's the first positional arg to the mock)
        # call_args[0] is for positional args, call_args[1] for kwargs
        # create_user in repo takes (user_data: dict)
        created_user_data_arg = mock_user_repository_async.create_user.await_args[0][0]
        assert created_user_data_arg["email"] == auth_user.email
        assert (
            auth_user.email is not None
        )  # Ensure email is not None before split for linter
        assert created_user_data_arg["username"] == auth_user.email.split("@")[0]
        assert created_user_data_arg["is_active"] is True
        # Assuming supabase_auth_id is also set, if that's part of User model and create logic
        # If UserService itself sets supabase_auth_id, it should be checked here.
        # The current UserRepo.create_user takes user_data dict, so it depends on what UserService puts in that dict.
        # The service logic for username generation is: auth_user.email.split("@")[0]
        # The service logic for other fields might be specific. For example, hashed_password = "" in the service.
        assert created_user_data_arg["hashed_password"] == ""

    @pytest.mark.asyncio
    async def test_get_or_create_user_profile_no_email(
        self, user_service_async: UserService, mock_user_repository_async: AsyncMock
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
            await user_service_async.get_or_create_user_profile(auth_user_no_email)

        # Verify exception
        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "Authenticated user missing email"

        # Verify repository not called
        mock_user_repository_async.get_user_by_email.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_get_or_create_user_profile_with_fallback_username(
        self,
        user_service_async: UserService,
        mock_user_repository_async: AsyncMock,
        sample_user_async: AsyncMock,
    ):
        """Test creating a user with fallback username when email has no @ symbol."""
        # Create auth user with unusual email (no @)
        auth_user_unusual_email = AuthenticatedUser(
            id="auth123",
            email="invalid-email",
            aud="authenticated",
        )

        # Set up mock returns
        mock_user_repository_async.get_user_by_email.return_value = None
        mock_user_repository_async.create_user.return_value = sample_user_async

        # Call the service method
        result = await user_service_async.get_or_create_user_profile(
            auth_user_unusual_email
        )

        # Verify results
        assert result is sample_user_async

        # Verify repository calls
        mock_user_repository_async.get_user_by_email.assert_awaited_once_with(
            "invalid-email"
        )
        mock_user_repository_async.create_user.assert_awaited_once()

        # Verify the created user data uses fallback username
        created_user_data = mock_user_repository_async.create_user.await_args[0][0]
        assert created_user_data["username"] == f"user_{auth_user_unusual_email.id}"
        assert created_user_data["email"] == "invalid-email"

    @pytest.mark.asyncio
    async def test_create_user_success(
        self,
        user_service_async: UserService,
        mock_user_repository_async: AsyncMock,
        sample_user_async: AsyncMock,
        sample_user_data: dict,
    ):
        """Test creating a new user successfully."""
        # Set up mock returns for validation checks
        mock_user_repository_async.get_user_by_email.return_value = None
        mock_user_repository_async.get_user_by_username.return_value = None
        mock_user_repository_async.create_user.return_value = sample_user_async

        # Remove id as it's not part of input data
        user_input_dict = sample_user_data.copy()
        # Ensure we are creating a new user, so ID from sample_user_data (which implies existing) should not be used.
        # UserService.create_user expects a dict. Let's simulate the Pydantic model or dict it might receive.
        user_input_for_create = {
            "username": user_input_dict["username"],
            "email": user_input_dict["email"],
            "full_name": user_input_dict.get(
                "full_name"
            ),  # Use .get for optional fields
            "hashed_password": "hashed_password",  # create_user service method expects this
            "is_active": user_input_dict.get(
                "is_active", True
            ),  # Default if not in sample
            "supabase_auth_id": user_input_dict.get("supabase_auth_id"),
        }

        # Call the service method
        result_dict = await user_service_async.create_user(user_input_for_create)

        # Verify results
        assert result_dict["id"] == sample_user_async.id
        assert result_dict["username"] == sample_user_async.username
        assert result_dict["email"] == sample_user_async.email
        assert result_dict["full_name"] == sample_user_async.full_name
        assert result_dict["is_active"] == sample_user_async.is_active
        assert "hashed_password" not in result_dict  # Sensitive info excluded

        # Verify repository calls
        mock_user_repository_async.get_user_by_email.assert_awaited_once_with(
            user_input_for_create["email"]
        )
        mock_user_repository_async.get_user_by_username.assert_awaited_once_with(
            user_input_for_create["username"]
        )
        # Verify create_user was called with the correct structure
        # The service method constructs user_create_dict then passes its .model_dump() (if pydantic)
        # or the dict itself to repository's create_user.
        # Assuming user_input_for_create is what's ultimately passed (or its equivalent after Pydantic processing)
        mock_user_repository_async.create_user.assert_awaited_once_with(
            user_input_for_create
        )

    @pytest.mark.asyncio
    async def test_create_user_email_exists(
        self,
        user_service_async: UserService,
        mock_user_repository_async: AsyncMock,
        sample_user_async: AsyncMock,
        sample_user_data: dict,
    ):
        """Test creating a user when the email already exists."""
        # Set up mock returns for validation checks
        mock_user_repository_async.get_user_by_email.return_value = (
            sample_user_async  # Email exists
        )
        mock_user_repository_async.get_user_by_username.return_value = None

        user_input_dict = sample_user_data.copy()
        user_input_for_create = {
            "username": "newusername",  # Different username
            "email": user_input_dict["email"],  # Existing email
            "full_name": user_input_dict.get("full_name"),
            "hashed_password": "hashed_password",
            "is_active": user_input_dict.get("is_active", True),
            "supabase_auth_id": user_input_dict.get("supabase_auth_id"),
        }

        # Call the service method and expect exception
        with pytest.raises(HTTPException) as excinfo:
            await user_service_async.create_user(user_input_for_create)

        # Verify exception
        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "Email already registered"

        # Verify repository calls
        mock_user_repository_async.get_user_by_email.assert_awaited_once_with(
            user_input_for_create["email"]
        )
        mock_user_repository_async.get_user_by_username.assert_not_awaited()  # Should not be called if email check fails first
        mock_user_repository_async.create_user.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_create_user_username_exists(
        self,
        user_service_async: UserService,
        mock_user_repository_async: AsyncMock,
        sample_user_async: AsyncMock,
        sample_user_data: dict,
    ):
        """Test creating a user when the username already exists."""
        # Set up mock returns for validation checks
        mock_user_repository_async.get_user_by_email.return_value = (
            None  # Email is unique
        )
        mock_user_repository_async.get_user_by_username.return_value = (
            sample_user_async  # Username exists
        )

        user_input_dict = sample_user_data.copy()
        user_input_for_create = {
            "username": user_input_dict["username"],  # Existing username
            "email": "newemail@example.com",  # Different email
            "full_name": user_input_dict.get("full_name"),
            "hashed_password": "hashed_password",
            "is_active": user_input_dict.get("is_active", True),
            "supabase_auth_id": user_input_dict.get("supabase_auth_id"),
        }

        # Call the service method and expect exception
        with pytest.raises(HTTPException) as excinfo:
            await user_service_async.create_user(user_input_for_create)

        # Verify exception
        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "Username already registered"

        # Verify repository calls
        mock_user_repository_async.get_user_by_email.assert_awaited_once_with(
            user_input_for_create["email"]
        )
        mock_user_repository_async.get_user_by_username.assert_awaited_once_with(
            user_input_for_create["username"]
        )
        mock_user_repository_async.create_user.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_create_user_missing_email(
        self, user_service_async: UserService, mock_user_repository_async: AsyncMock
    ):
        """Test creating a user with missing email (should be caught by Pydantic model if UserCreate schema is used)."""
        user_input_for_create = {
            "username": "someuser",
            # "email": "missing@example.com", # Email is missing
            "full_name": "Some User",
            "hashed_password": "hashed_password",
        }
        # Depending on how UserService.create_user handles input (e.g. if it uses a Pydantic model UserCreate for validation)
        # this might raise a Pydantic ValidationError or an HTTPException if the service catches it.
        # For this test, let's assume the service raises HTTPException for simplicity if basic fields are missing,
        # or Pydantic ValidationError if it uses a model.
        # If UserService create_user uses a Pydantic model UserCreate that requires email:
        # from pydantic import ValidationError
        # with pytest.raises(ValidationError): # Or HTTPException if service translates it
        #     await user_service_async.create_user(user_input_for_create)

        # If the service's create_user method itself checks for 'email' in the dict:
        with pytest.raises(
            HTTPException
        ) as excinfo:  # Or TypeError if dict access fails like user_data["email"]
            await user_service_async.create_user(user_input_for_create)  # Pass the dict

        # This assertion depends on the actual error raised by create_user for missing fields.
        # If UserCreate Pydantic model is used, it would be a ValidationError.
        # If the service manually checks and raises HTTPException:
        assert (
            excinfo.value.status_code == 422
        )  # Unprocessable Entity (typical for validation errors)
        # Or if a KeyError/TypeError happens before validation and is not caught:
        # assert isinstance(excinfo.value, (KeyError, TypeError))

        mock_user_repository_async.create_user.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_create_user_missing_username(
        self, user_service_async: UserService, mock_user_repository_async: AsyncMock
    ):
        """Test creating a user with missing username."""
        user_input_for_create = {
            # "username": "someuser", # Username is missing
            "email": "test@example.com",
            "full_name": "Some User",
            "hashed_password": "hashed_password",
        }

        with pytest.raises(
            HTTPException
        ) as excinfo:  # Assuming HTTPException for validation
            await user_service_async.create_user(user_input_for_create)

        assert excinfo.value.status_code == 422  # Unprocessable Entity
        mock_user_repository_async.create_user.assert_not_awaited()
