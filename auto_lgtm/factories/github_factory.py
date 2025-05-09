from auto_lgtm.services.github_service import GitHubService
from auto_lgtm.common.github_client import GitHubApiClient
from loguru import logger

class GitHubServiceFactory:
    @staticmethod
    def create(token: str, owner: str) -> GitHubService:
        logger.info(f"Creating GitHubService for owner: {owner}, token present: {token}")
        api_client = GitHubApiClient(token, owner)
        return GitHubService(api_client)