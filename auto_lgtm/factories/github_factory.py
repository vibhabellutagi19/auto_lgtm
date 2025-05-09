from auto_lgtm.services.github_service import GitHubService
from auto_lgtm.common.github_client import GitHubApiClient

class GitHubServiceFactory:
    @staticmethod
    def create(token: str, owner: str) -> GitHubService:
        api_client = GitHubApiClient(token, owner)
        return GitHubService(api_client)