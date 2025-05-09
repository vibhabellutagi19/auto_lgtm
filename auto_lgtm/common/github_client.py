import requests
from loguru import logger

class GitHubApiClient:
    def __init__(self, token: str, owner: str):
        self.base_url = "https://api.github.com"
        self.owner = owner
        self.headers: dict[str, str] = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        logger.info(f"GitHubApiClient initialized for owner: {owner}, token present: {bool(token)}, token length: {len(token) if token else 0}")

    def get(self, endpoint: str, params=None):
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"GET {url} with params={params}")
        response = requests.get(url, headers=self.headers, params=params)
        logger.info(f"GET {url} status: {response.status_code}")
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data=None):
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"POST {url} with data={data}")
        response = requests.post(url, headers=self.headers, json=data)
        logger.info(f"POST {url} status: {response.status_code}")
        response.raise_for_status()
        return response.json()