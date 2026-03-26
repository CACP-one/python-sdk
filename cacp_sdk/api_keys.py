"""
CACP SDK API Keys API

API key management operations.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from cacp_sdk.client import CacpClient


class APIKey(BaseModel):
    id: str
    name: str
    scopes: List[str] = []
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class APIKeyCreated(BaseModel):
    id: str
    name: str
    key: str
    scopes: List[str] = []
    expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    owner_type: str
    owner_id: str
    warning: str = "Store this key securely. It will not be shown again."


class APIKeyListResponse(BaseModel):
    api_keys: List[APIKey]
    total: int


class CreateAPIKeyRequest(BaseModel):
    name: Optional[str] = None
    scopes: List[str] = Field(default_factory=lambda: ["read", "write"])
    expires_in_days: Optional[int] = None


class APIKeysAPI:
    """
    API for API key management operations.

    Provides methods for:
    - Creating new API keys
    - Listing API keys
    - Getting API key details
    - Deleting (revoking) API keys
    """

    def __init__(self, client: "CacpClient") -> None:
        """Initialize the API keys API."""
        self._client = client

    async def create(
        self,
        name: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        expires_in_days: Optional[int] = None,
    ) -> APIKeyCreated:
        """
        Create a new API key.

        The API key can be used for authenticating API requests.
        The key is only returned once - store it securely.

        Args:
            name: Optional name for the key (defaults to "API Key <date>")
            scopes: List of scopes (default: ["read", "write"])
            expires_in_days: Optional expiration in days

        Returns:
            APIKeyCreated with the key and metadata

        Raises:
            ValidationError: If request is invalid
            AuthenticationError: If not authenticated

        Example:
            ```python
            key = await client.api_keys.create(
                name="Production Key",
                scopes=["read", "write"],
                expires_in_days=90
            )
            print(f"Key: {key.key}")
            print(f"Warning: {key.warning}")
            ```
        """
        request_data: Dict[str, Any] = {}
        if name:
            request_data["name"] = name
        if scopes is not None:
            request_data["scopes"] = scopes
        if expires_in_days is not None:
            request_data["expires_in_days"] = expires_in_days

        response = await self._client.post(
            "/v1/api-keys",
            json_data=request_data if request_data else None,
        )

        return APIKeyCreated(**response)

    async def list(self) -> APIKeyListResponse:
        """
        List all API keys for the authenticated user/agent.

        Note: The actual key values are not returned in the list.

        Returns:
            APIKeyListResponse with list of keys and total count

        Raises:
            AuthenticationError: If not authenticated

        Example:
            ```python
            result = await client.api_keys.list()
            for key in result.api_keys:
                print(f"{key.name}: {key.scopes}")
            ```
        """
        response = await self._client.get("/v1/api-keys")
        return APIKeyListResponse(**response)

    async def get(self, key_id: str) -> APIKey:
        """
        Get details of a specific API key.

        Args:
            key_id: The API key ID

        Returns:
            APIKey with details

        Raises:
            NotFoundError: If the key doesn't exist (code 2001)
            AuthenticationError: If not authenticated

        Example:
            ```python
            key = await client.api_keys.get("key_123")
            print(f"Name: {key.name}")
            print(f"Last used: {key.last_used_at}")
            ```
        """
        response = await self._client.get(f"/v1/api-keys/{key_id}")
        return APIKey(**response)

    async def delete(self, key_id: str) -> None:
        """
        Delete (revoke) an API key.

        After deletion, the key can no longer be used for authentication.

        Args:
            key_id: The API key ID to delete

        Raises:
            NotFoundError: If the key doesn't exist (code 2001)
            AuthenticationError: If not authenticated

        Example:
            ```python
            await client.api_keys.delete("key_123")
            print("Key revoked")
            ```
        """
        await self._client.delete(f"/v1/api-keys/{key_id}")