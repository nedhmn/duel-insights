from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt_handler import jwt_handler
from app.auth.models import AuthError, UserContext
from app.db.database import get_db_session
from app.db.models import User

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


async def get_user_context(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> UserContext:
    """Extract user context from JWT token."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Verify JWT token
        claims = await jwt_handler.verify_token(credentials.credentials)

        # Extract user information
        user_info = jwt_handler.extract_user_info(claims)

        # Create user context
        user_context = UserContext(**user_info)

        if not user_context.clerk_user_id:
            raise AuthError("Invalid token: missing user ID")

        return user_context

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except AuthError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error",
        ) from e


async def get_current_user(
    user_context: UserContext = Depends(get_user_context),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """Get or create the current user from the database."""
    try:
        # Try to find existing user
        result = await db.execute(
            select(User).where(User.clerk_user_id == user_context.clerk_user_id)
        )
        user = result.scalar_one_or_none()

        if user:
            # Update user context with database user ID
            user_context.user_id = str(user.id)
            return user

        # Create new user if doesn't exist
        new_user = User(clerk_user_id=user_context.clerk_user_id)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        # Update user context with new user ID
        user_context.user_id = str(new_user.id)

        return new_user

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User lookup failed",
        ) from e


async def get_optional_user_context(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> UserContext | None:
    """Extract user context from JWT token, returning None if not authenticated."""
    if not credentials or not credentials.credentials:
        return None

    try:
        return await get_user_context(credentials)
    except HTTPException:
        return None
