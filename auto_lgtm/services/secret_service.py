from google.cloud import secretmanager
from loguru import logger
import json
from typing import Dict, Any

class SecretService:
    def __init__(self, project_id: str):
        self.client = secretmanager.SecretManagerServiceClient()
        self.project_id = project_id
        self.project_path = f"projects/{project_id}"
        self._secrets_cache: Dict[str, Any] = {}

    def get_secrets(self, secret_id: str) -> Dict[str, Any]:
        """
        Get all secrets from Secret Manager.
        The secrets are stored in a single JSON file in Secret Manager.
        
        Returns:
            Dictionary containing all secrets
            
        Raises:
            ValueError: If secrets cannot be retrieved
        """
        if not self._secrets_cache:
            try:
                name = f"{self.project_path}/secrets/{secret_id}/versions/latest"
                response = self.client.access_secret_version(request={"name": name})
                self._secrets_cache = json.loads(response.payload.data.decode("UTF-8"))
            except Exception as e:
                logger.error(f"Error accessing secrets: {str(e)}")
                raise ValueError(f"Failed to retrieve secrets: {str(e)}")
        return self._secrets_cache

    def get_secret(self, secret_id: str, key: str) -> str:
        """
        Get a specific secret from the secrets dictionary.
        
        Args:
            key: The key of the secret to retrieve
            
        Returns:
            The secret value as a string
            
        Raises:
            ValueError: If the secret cannot be retrieved
        """
        secrets = self.get_secrets(secret_id)
        if key not in secrets:
            raise ValueError(f"Secret key '{key}' not found in secrets")
        return secrets[key] 