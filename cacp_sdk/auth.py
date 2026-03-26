"""
CACP SDK Auth API

Authentication and token management operations.
"""

from typing import TYPE_CHECKING, Any, Dict, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from cacp_sdk.client import CacpClient


class User(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    role: Optional[str] = None


class Organization(BaseModel):
    id: str
    name: str
    plan_type: Optional[str] = None


class AuthRegisterResponse(BaseModel):
    token: str
    user: User
    organization: Organization


class AuthLoginResponse(BaseModel):
    token: str
    user: User
    organization_id: str


class AuthTokenResponse(BaseModel):
    token: str
    user: Optional[User] = None
    agent_id: Optional[str] = None
    organization_id: str
    token_type: Optional[str] = None


class AuthRefreshResponse(BaseModel):
    token: str
    token_type: str
    user: Optional[User] = None
    agent_id: Optional[str] = None
    organization_id: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    user_name: str = Field(..., alias="user_name")
    organization_name: str = Field(..., alias="organization_name")

    class Config:
        populate_by_name = True


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenRequest(BaseModel):
    api_key: str = Field(..., alias="api_key")

    class Config:
        populate_by_name = True


class AuthAPI:
    """
    API for authentication operations.

    Provides methods for:
    - User registration with organization creation
    - Login (email/password) to get JWT token
    - API key authentication to get JWT token
    - Token refresh
    """

    def __init__(self, client: "CacpClient") -> None:
        """Initialize the auth API."""
        self._client = client

    async def register(
        self,
        email: str,
        password: str,
        user_name: str,
        organization_name: str,
    ) -> AuthRegisterResponse:
        """
        Register a new user and create an organization.

        Args:
            email: User email address
            password: User password
            user_name: User's display name
            organization_name: Name for the new organization

        Returns:
            AuthRegisterResponse with token, user, and organization

        Raises:
            ValidationError: If required fields are missing or invalid
            CacpError: If registration fails

        Example:
            ```python
            result = await client.auth.register(
                email="user@example.com",
                password="secure-password",
                user_name="John Doe",
                organization_name="Acme Corp"
            )
            print(f"Token: {result.token}")
            print(f"User: {result.user.name}")
            ```
        """
        request = RegisterRequest(
            email=email,
            password=password,
            user_name=user_name,
            organization_name=organization_name,
        )

        response = await self._client.post(
            "/v1/auth/register",
            json_data=request.model_dump(by_alias=True),
        )

        return AuthRegisterResponse(**response)

    async def login(
        self,
        email: str,
        password: str,
    ) -> AuthLoginResponse:
        """
        Login with email and password.

        Args:
            email: User email address
            password: User password

        Returns:
            AuthLoginResponse with token and user info

        Raises:
            AuthenticationError: If credentials are invalid (code 5001)

        Example:
            ```python
            result = await client.auth.login(
                email="user@example.com",
                password="secure-password"
            )
            print(f"Token: {result.token}")
            ```
        """
        request = LoginRequest(email=email, password=password)

        response = await self._client.post(
            "/v1/auth/login",
            json_data=request.model_dump(),
        )

        return AuthLoginResponse(**response)

    async def get_token(self, api_key: str) -> AuthTokenResponse:
        """
        Exchange an API key for a JWT token.

        This endpoint authenticates using an API key and returns a JWT token
        that can be used for subsequent requests.

        Args:
            api_key: The API key (starts with "cacp_")

        Returns:
            AuthTokenResponse with token and owner info

        Raises:
            AuthenticationError: If API key is invalid (code 5002) or expired (code 5003)

        Example:
            ```python
            result = await client.auth.get_token(api_key="cacp_xxx...")
            print(f"Token: {result.token}")
            ```
        """
        request = TokenRequest(api_key=api_key)

        response = await self._client.post(
            "/v1/auth/token",
            json_data=request.model_dump(by_alias=True),
        )

        return AuthTokenResponse(**response)

    async def refresh_token(self) -> AuthRefreshResponse:
        """
        Refresh the current JWT token.

        The current JWT token must be provided in the Authorization header.
        Returns a new token with extended expiration.

        Returns:
            AuthRefreshResponse with new token

        Raises:
            AuthenticationError: If token is invalid or expired (codes 5005, 5006)

        Example:
            ```python
            # Assuming client is initialized with a JWT token
            result = await client.auth.refresh_token()
            print(f"New token: {result.token}")
            ```
        """
        response = await self._client.post("/v1/auth/refresh")
        return AuthRefreshResponse(**response)