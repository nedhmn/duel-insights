import json
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError

from app.config import settings


class JWTHandler:
    """Handles JWT token verification using Clerk JWKS."""

    def __init__(self) -> None:
        self._jwks_cache: dict[str, Any] | None = None
        self._jwks_cache_expires: datetime | None = None
        self._cache_duration_seconds = 3600  # 1 hour

    async def get_jwks(self) -> dict[str, Any]:
        """Fetch JWKS from Clerk, with caching."""
        now = datetime.now(timezone.utc)

        # Return cached JWKS if still valid
        if (
            self._jwks_cache
            and self._jwks_cache_expires
            and now < self._jwks_cache_expires
        ):
            return self._jwks_cache

        # Fetch fresh JWKS
        if not settings.CLERK_JWKS_URL:
            raise ValueError("CLERK_JWKS_URL is not configured")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(settings.CLERK_JWKS_URL, timeout=10.0)
                response.raise_for_status()
                jwks_data = response.json()

                # Cache the JWKS
                self._jwks_cache = jwks_data
                self._jwks_cache_expires = now + timedelta(
                    seconds=self._cache_duration_seconds
                )

                return jwks_data  # type: ignore[no-any-return]

            except httpx.HTTPError as e:
                raise ValueError(f"Failed to fetch JWKS: {e}") from e
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JWKS response: {e}") from e

    async def verify_token(self, token: str) -> dict[str, Any]:
        """Verify JWT token and return claims."""
        if not token:
            raise ValueError("Token is required")

        try:
            # Get JWKS for signature verification
            jwks = await self.get_jwks()

            # Decode token header to get key ID
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")

            if not kid:
                raise ValueError("Token missing key ID (kid)")

            # Find the appropriate key
            key = None
            for jwk in jwks.get("keys", []):
                if jwk.get("kid") == kid:
                    key = jwk
                    break

            if not key:
                raise ValueError(f"Key with ID {kid} not found in JWKS")

            # Verify and decode the token
            claims = jwt.decode(
                token,
                key,
                algorithms=["RS256"],  # Clerk uses RS256
                issuer=settings.CLERK_JWT_ISSUER,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iss": True,
                    "require_exp": True,
                    "require_iss": True,
                },
            )

            return claims

        except ExpiredSignatureError as e:
            raise ValueError("Token has expired") from e
        except JWTClaimsError as e:
            raise ValueError(f"Token claims invalid: {e}") from e
        except JWTError as e:
            raise ValueError(f"Token verification failed: {e}") from e
        except Exception as e:
            raise ValueError(f"Unexpected error during token verification: {e}") from e

    def extract_user_info(self, claims: dict[str, Any]) -> dict[str, Any]:
        """Extract user information from JWT claims."""
        return {
            "clerk_user_id": claims.get("sub"),  # Subject is the Clerk user ID
            "email_verified": claims.get("email_verified", False),
        }


# Global JWT handler instance
jwt_handler = JWTHandler()
