from services.github_service import GitHubService
from common.github_client import GitHubApiClient

class GitHubServiceFactory:
    @staticmethod
    def create(token: str) -> GitHubService:
        api_client = GitHubApiClient(token)
        return GitHubService(api_client)