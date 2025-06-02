from auto_lgtm.common.github_app_auth import get_installation_access_token
from auto_lgtm.common.github_client import GitHubApiClient
from auto_lgtm.services.secret_service import SecretService
from loguru import logger

class GitHubAppFactory:
    def __init__(self, project_id: str, secret_id: str):
        self.secret_service = SecretService(project_id)
        self.secret_id = secret_id
        self.private_github_key = "github_app_private_key" # TODO: handle it in a better way

    def create_client(self, owner: str, installation_id: str) -> GitHubApiClient:
        """
        Create a GitHub API client using GitHub App authentication.
        
        Args:
            owner: The repository owner
            installation_id: The GitHub App installation ID
            
        Returns:
            GitHubApiClient configured with an installation access token
        """
        try:
            # Get the private key and app ID from Secret Manager
            private_key = self.secret_service.get_secret_plain_text(self.private_github_key)
            app_id = self.secret_service.get_secret(self.secret_id, "github_app_id")

            logger.info(f"app_id: {app_id}")
            
            # Generate installation access token
            installation_token = get_installation_access_token(app_id, private_key, installation_id)
            
            # Create and return the GitHub client
            return GitHubApiClient(token=installation_token, owner=owner)
            
        except Exception as e:
            logger.error(f"Failed to create GitHub App client: {str(e)}")
            raise 