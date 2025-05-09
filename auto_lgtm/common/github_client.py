import requests
from loguru import logger
from contextlib import contextmanager
from typing import Dict, Optional

class GitHubApiClient:
    def __init__(self, token: str, owner: str):
        self.base_url = "https://api.github.com"
        self.owner = owner
        self.headers: dict[str, str] = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        logger.info(f"GitHubApiClient initialized for owner: {owner}, token present: {bool(token)}, token length: {len(token) if token else 0}")

    @contextmanager
    def with_headers(self, headers: Dict[str, str]):
        """
        Context manager to temporarily modify headers for a specific request.
        
        Args:
            headers: Dictionary of headers to merge with existing headers
        """
        original_headers = self.headers.copy()
        try:
            self.headers.update(headers)
            yield
        finally:
            self.headers = original_headers
            logger.debug("Restored original headers")

    def get(self, endpoint: str, return_text: bool = False):
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"Making GET request to: {url}")
        response = requests.get(url, headers=self.headers)
        logger.info(f"GET {url} status: {response.status_code}")
        if response.status_code != 200:
            logger.error(f"Error response: {response.text}")
        response.raise_for_status()
        if return_text:
            return response.text
        return response.json()

    def post(self, endpoint: str, data=None):
        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, headers=self.headers, json=data)
        logger.info(f"POST {url} status: {response.status_code}")
        if response.status_code != 200:
            logger.error(f"Error response: {response.text}")
        response.raise_for_status()
        return response.json()