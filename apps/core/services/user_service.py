from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from lib.auth.supabase_auth import AuthenticatedUser
from operations.user_repository import UserRepository, get_user_repository
from sqlalchemy.orm import Session

from apps.core.models.user_model import User


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        user = self.user_repository.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Business logic: exclude sensitive information
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
        }

    def get_or_create_user_profile(
        self, db: Session, auth_user: AuthenticatedUser
    ) -> User:
        """
        Ensures a local user profile exists for the authenticated user.
        Looks up by email; creates a new user if not found.

        Args:
            db (Session): SQLAlchemy DB session.
            auth_user (AuthenticatedUser): Authenticated user from Supabase JWT.

        Returns:
            User: The user model instance.
        """
        if not auth_user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authenticated user missing email",
            )
        user = self.user_repository.get_user_by_email(auth_user.email)
        if user:
            return user

        # Generate a username from email prefix or fallback to user id string
        username = (
            auth_user.email.split("@")[0]
            if "@" in auth_user.email
            else f"user_{auth_user.id}"
        )
        user_data = {
            "username": username,
            "email": auth_user.email,
            "full_name": "",
            "hashed_password": "",  # Not used for Supabase-auth users
            "is_active": True,
        }
        user = self.user_repository.create_user(user_data)
        return user

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        # Check if username or email already exists
        email = user_data.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required",
            )
        if self.user_repository.get_user_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        username = user_data.get("username")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username is required",
            )
        if self.user_repository.get_user_by_username(username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

        # Create user
        user = self.user_repository.create_user(user_data)

        # Return user without sensitive information
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
        }


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(user_repository)
