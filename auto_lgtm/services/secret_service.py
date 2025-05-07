from google.cloud import secretmanager
from loguru import logger

class SecretService:
    def __init__(self, project_id: str):
        self.client = secretmanager.SecretManagerServiceClient()
        self.project_id = project_id
        self.project_path = f"projects/{project_id}"

    def get_secret(self, secret_id: str) -> str:
        """
        Get a secret from Secret Manager.
        
        Args:
            secret_id: The ID of the secret to retrieve
            
        Returns:
            The secret value as a string
        """
        try:
            name = f"{self.project_path}/secrets/{secret_id}/versions/latest"
            response = self.client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            logger.error(f"Error accessing secret {secret_id}: {str(e)}")
            raise 