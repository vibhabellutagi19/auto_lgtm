import requests
import os
class GitHubApiClient:
    def __init__(self, token: str):
        self.base_url = "https://api.github.com"
        self.owner = os.getenv("GITHUB_OWNER")
        self.headers: dict[str, str] = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def get(self, endpoint: str, params=None):
        response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data=None):
        response = requests.post(f"{self.base_url}{endpoint}", headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()