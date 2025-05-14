from fastapi import APIRouter, Depends, HTTPException, status

from api.video_processor.infrastructure.api.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/me")
async def read_users_me(current_user=Depends(get_current_user)):
    """
    Returns the authenticated user's details as provided by Supabase.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    return current_user
