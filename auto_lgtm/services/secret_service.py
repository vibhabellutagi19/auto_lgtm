from google.cloud import secretmanager
from loguru import logger
import json
from typing import Dict, Any, Optional

class SecretService:
    def __init__(self, project_id: str):
        self.client = secretmanager.SecretManagerServiceClient()
        self.project_id = project_id
        self.project_path = f"projects/{project_id}"
        self._secrets_cache: Dict[str, Any] = {}

    def _get_secrets_from_sm(self, secret_id: str) -> Dict[str, Any]:
        """
        Get all secrets from Secret Manager.
        The secrets are stored in a single JSON file in Secret Manager.
        
        Returns:
            Dictionary containing all secrets
            
        Raises:
            ValueError: If secrets cannot be retrieved
        """
        if not self._secrets_cache.get(secret_id):
            try:
                name = f"{self.project_path}/secrets/{secret_id}/versions/latest"
                response = self.client.access_secret_version(name=name)
                secret_data = response.payload.data.decode("UTF-8")
                
                try:
                    self._secrets_cache[secret_id] = json.loads(secret_data)
                except json.JSONDecodeError:
                    self._secrets_cache[secret_id] = secret_data
                    
            except Exception as e:
                logger.error(f"Error accessing secrets: {str(e)}")
                raise ValueError(f"Failed to retrieve secrets: {str(e)}")
        return self._secrets_cache[secret_id]

    def get_secret(self, secret_id: str, key: str) -> str:
        """
        Get a specific secret from the secrets dictionary.
        If key is None, returns the entire secret value (for plain text secrets).
        
        Args:
            secret_id: The ID of the secret in Secret Manager
            key: The key of the secret to retrieve. If None, returns the entire secret value.
            
        Returns:
            The secret value as a string
            
        Raises:
            ValueError: If the secret cannot be retrieved
        """
        secrets = self._get_secrets_from_sm(secret_id)
        
        if key in secrets:
            return secrets[key]
        else:
            if key is not None and key not in secrets:
                raise ValueError(f"Secret key '{key}' not found in secrets. Available keys: {list(secrets.keys())}")
            return secrets[key]

    def get_secret_plain_text(self, secret_id: str) -> str:
        """
        Get a plain text secret from the secrets dictionary.
        """
        secrets = self._get_secrets_from_sm(secret_id)
        return secrets