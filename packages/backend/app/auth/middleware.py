import logging
from typing import Callable, Awaitable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.auth.dependencies import get_optional_user_context
from app.auth.models import UserContext


logger = logging.getLogger(__name__)


class AuthContextMiddleware(BaseHTTPMiddleware):
    """Middleware to optionally extract user context and add it to request state."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process request and add user context to request state if available."""

        # Initialize user context as None
        request.state.user_context = None
        request.state.is_authenticated = False

        # Try to extract user context (non-blocking)
        try:
            # Get authorization header
            authorization = request.headers.get("authorization")

            if authorization and authorization.startswith("Bearer "):
                # Extract user context without raising exceptions
                from fastapi.security import HTTPAuthorizationCredentials

                credentials = HTTPAuthorizationCredentials(
                    scheme="Bearer", credentials=authorization.split(" ", 1)[1]
                )

                user_context = await get_optional_user_context(credentials)

                if user_context:
                    request.state.user_context = user_context
                    request.state.is_authenticated = True
                    logger.debug(f"User authenticated: {user_context.clerk_user_id}")
                else:
                    logger.debug("Invalid or expired token in request")
            else:
                logger.debug("No authorization header in request")

        except Exception as e:
            # Log error but don't block request
            logger.warning(f"Error extracting user context: {e}")

        # Process the request
        response = await call_next(request)

        return response


def get_request_user_context(request: Request) -> Optional[UserContext]:
    """Helper function to get user context from request state."""
    return getattr(request.state, "user_context", None)


def is_request_authenticated(request: Request) -> bool:
    """Helper function to check if request is authenticated."""
    return getattr(request.state, "is_authenticated", False)
