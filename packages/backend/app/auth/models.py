from pydantic import BaseModel


class UserContext(BaseModel):
    """User context extracted from JWT token."""

    clerk_user_id: str
    email_verified: bool = False

    # Database user ID (set after user lookup/creation)
    user_id: str | None = None


class AuthError(Exception):
    """Authentication-related errors."""

    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
