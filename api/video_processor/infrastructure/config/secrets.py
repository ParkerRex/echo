"""Secure credential management using Google Cloud Secret Manager."""

import json
import os
from functools import lru_cache
from typing import Any, Dict, Optional

from google.cloud import secretmanager
from google.cloud.secretmanager_v1 import SecretManagerServiceClient

from video_processor.infrastructure.monitoring import structured_log


class SecretManagerClient:
    """Client for Google Cloud Secret Manager.

    This class provides methods for securely accessing and managing credentials
    stored in Google Cloud Secret Manager.
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        client: Optional[SecretManagerServiceClient] = None,
    ):
        """Initialize Secret Manager client.

        Args:
            project_id: Google Cloud project ID (defaults to GOOGLE_CLOUD_PROJECT env var)
            client: Secret Manager client instance (created if not provided)
        """
        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not self.project_id:
            raise ValueError(
                "Project ID must be provided or set as GOOGLE_CLOUD_PROJECT environment variable"
            )

        self.client = client or secretmanager.SecretManagerServiceClient()

        # Cache for secrets to avoid repeated API calls
        self._secret_cache: Dict[str, Dict[str, Any]] = {}

    def get_secret_version_path(self, secret_id: str, version: str = "latest") -> str:
        """Get the full path to a secret version.

        Args:
            secret_id: Secret ID
            version: Secret version (default: latest)

        Returns:
            Full path to the secret version
        """
        return f"projects/{self.project_id}/secrets/{secret_id}/versions/{version}"

    def get_secret(self, secret_id: str, version: str = "latest") -> str:
        """Get a secret value.

        Args:
            secret_id: Secret ID
            version: Secret version (default: latest)

        Returns:
            Secret value as a string

        Raises:
            Exception: If the secret cannot be accessed
        """
        # Check cache first
        cache_key = f"{secret_id}:{version}"
        if cache_key in self._secret_cache:
            return self._secret_cache[cache_key]["value"]

        try:
            # Build the resource name of the secret version
            name = self.get_secret_version_path(secret_id, version)

            # Access the secret version
            response = self.client.access_secret_version(request={"name": name})

            # Get the secret value
            payload = response.payload.data.decode("UTF-8")

            # Cache the secret
            self._secret_cache[cache_key] = {
                "value": payload,
                "version": response.name.split("/")[-1],
            }

            structured_log(
                "info",
                f"Retrieved secret {secret_id} (version: {version})",
                {"secret_id": secret_id},
            )

            return payload

        except Exception as e:
            structured_log(
                "error",
                f"Failed to retrieve secret {secret_id}: {str(e)}",
                {"secret_id": secret_id, "error": str(e)},
            )
            raise

    def get_json_secret(
        self, secret_id: str, version: str = "latest"
    ) -> Dict[str, Any]:
        """Get a JSON secret value.

        Args:
            secret_id: Secret ID
            version: Secret version (default: latest)

        Returns:
            Secret value as a parsed JSON object

        Raises:
            Exception: If the secret cannot be accessed or is not valid JSON
        """
        secret_value = self.get_secret(secret_id, version)
        try:
            return json.loads(secret_value)
        except json.JSONDecodeError as e:
            structured_log(
                "error",
                f"Failed to parse JSON secret {secret_id}: {str(e)}",
                {"secret_id": secret_id, "error": str(e)},
            )
            raise

    def create_secret(self, secret_id: str, secret_value: str) -> None:
        """Create a new secret.

        Args:
            secret_id: Secret ID
            secret_value: Secret value

        Raises:
            Exception: If the secret cannot be created
        """
        try:
            parent = f"projects/{self.project_id}"

            # Create the secret
            self.client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": secret_id,
                    "secret": {"replication": {"automatic": {}}},
                }
            )

            # Add the secret version
            self.client.add_secret_version(
                request={
                    "parent": f"{parent}/secrets/{secret_id}",
                    "payload": {"data": secret_value.encode("UTF-8")},
                }
            )

            structured_log(
                "info",
                f"Created secret {secret_id}",
                {"secret_id": secret_id},
            )

        except Exception as e:
            structured_log(
                "error",
                f"Failed to create secret {secret_id}: {str(e)}",
                {"secret_id": secret_id, "error": str(e)},
            )
            raise

    def update_secret(self, secret_id: str, secret_value: str) -> None:
        """Update an existing secret with a new version.

        Args:
            secret_id: Secret ID
            secret_value: New secret value

        Raises:
            Exception: If the secret cannot be updated
        """
        try:
            parent = f"projects/{self.project_id}/secrets/{secret_id}"

            # Add a new version
            response = self.client.add_secret_version(
                request={
                    "parent": parent,
                    "payload": {"data": secret_value.encode("UTF-8")},
                }
            )

            # Update cache
            version = response.name.split("/")[-1]
            cache_key = f"{secret_id}:latest"
            self._secret_cache[cache_key] = {
                "value": secret_value,
                "version": version,
            }

            structured_log(
                "info",
                f"Updated secret {secret_id} (version: {version})",
                {"secret_id": secret_id, "version": version},
            )

        except Exception as e:
            structured_log(
                "error",
                f"Failed to update secret {secret_id}: {str(e)}",
                {"secret_id": secret_id, "error": str(e)},
            )
            raise

    def delete_secret(self, secret_id: str) -> None:
        """Delete a secret.

        Args:
            secret_id: Secret ID

        Raises:
            Exception: If the secret cannot be deleted
        """
        try:
            name = f"projects/{self.project_id}/secrets/{secret_id}"

            # Delete the secret
            self.client.delete_secret(request={"name": name})

            # Clear cache
            for key in list(self._secret_cache.keys()):
                if key.startswith(f"{secret_id}:"):
                    del self._secret_cache[key]

            structured_log(
                "info",
                f"Deleted secret {secret_id}",
                {"secret_id": secret_id},
            )

        except Exception as e:
            structured_log(
                "error",
                f"Failed to delete secret {secret_id}: {str(e)}",
                {"secret_id": secret_id, "error": str(e)},
            )
            raise


# Create a singleton instance with caching
@lru_cache(maxsize=1)
def get_secret_manager_client(project_id: Optional[str] = None) -> SecretManagerClient:
    """Get a Secret Manager client instance.

    This function returns a singleton instance of the Secret Manager client,
    which is cached to avoid creating multiple instances.

    Args:
        project_id: Google Cloud project ID (defaults to GOOGLE_CLOUD_PROJECT env var)

    Returns:
        Secret Manager client instance
    """
    return SecretManagerClient(project_id)


def get_secret(secret_id: str, version: str = "latest") -> str:
    """Convenience function to get a secret value.

    Args:
        secret_id: Secret ID
        version: Secret version (default: latest)

    Returns:
        Secret value as a string
    """
    client = get_secret_manager_client()
    return client.get_secret(secret_id, version)


def get_json_secret(secret_id: str, version: str = "latest") -> Dict[str, Any]:
    """Convenience function to get a JSON secret value.

    Args:
        secret_id: Secret ID
        version: Secret version (default: latest)

    Returns:
        Secret value as a parsed JSON object
    """
    client = get_secret_manager_client()
    return client.get_json_secret(secret_id, version)


def get_or_env(secret_id: str, env_var: str, default: Optional[str] = None) -> str:
    """Get a secret or fallback to an environment variable.

    This is useful for development environments where Secret Manager may not be available.

    Args:
        secret_id: Secret ID
        env_var: Environment variable name
        default: Default value if both secret and env var are not available

    Returns:
        Secret value or environment variable value or default
    """
    try:
        return get_secret(secret_id)
    except Exception:
        value = os.environ.get(env_var)
        if value is not None:
            return value
        if default is not None:
            return default
        raise ValueError(
            f"Neither secret {secret_id} nor environment variable {env_var} is set"
        )
