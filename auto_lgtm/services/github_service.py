import requests
from typing import Any, List, Dict, Literal
from auto_lgtm.models.review_models import ChangeType
from auto_lgtm.common.github_client import GitHubApiClient
from requests.exceptions import RequestException
from loguru import logger

class GitHubService:
    def __init__(self, api_client: GitHubApiClient):
        self.api_client: GitHubApiClient = api_client

    def fetch_pull_requests(self, repo: str, state: str = "open"):
        endpoint = f"/repos/{self.api_client.owner}/{repo}/pulls"
        return self.api_client.get(endpoint, params={"state": state})

    def fetch_pr_diff(self, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        endpoint = f"/repos/{self.api_client.owner}/{repo}/pulls/{pr_number}"
        try:
            with self.api_client.with_headers({"Accept": "application/vnd.github.v3.diff"}):
                diff_content = self.api_client.get(endpoint, return_text=True)
                return self.parse_diff(diff_content)
        except RequestException as e:
            if hasattr(e.response, 'status_code'):
                if e.response.status_code == 404:
                    raise GitHubServiceError(f"PR not found. Please check if repository '{repo}' and PR number {pr_number} are correct.")
                elif e.response.status_code == 403:
                    raise GitHubServiceError(f"Access forbidden. Please check if your token has sufficient permissions and the repository exists.")
            raise GitHubServiceError(f"Failed to fetch PR diff: {str(e)}")

    def parse_diff(self, diff_content: str) -> List[Dict[str, Any]]:
        """Parse the diff content and return a structured format with line numbers.
        
        Args:
            diff_content: The raw diff content from GitHub
            
        Returns:
            List of dictionaries containing structured diff information
        """
        structured_diff = []
        current_file = None
        current_chunk = None
        current_line_number = 0
        
        for line in diff_content.split('\n'):
            if line.startswith('diff --git'):
                if current_file is not None:
                    structured_diff.append(current_file)
                current_file = {
                    'file': line.split(' ')[2][2:],
                    'chunks': []
                }
                current_chunk = None
                current_line_number = 0
            elif line.startswith('@@'):
                if current_chunk is not None and current_file is not None:
                    current_file['chunks'].append(current_chunk)
                numbers = line.split(' ')[1:3]
                old_start = int(numbers[0].split(',')[0][1:])
                new_start = int(numbers[1].split(',')[0][1:])
                current_chunk = {
                    'old_start': old_start,
                    'new_start': new_start,
                    'changes': []
                }
                current_line_number = new_start
            elif line.startswith('+') or line.startswith('-'):
                if current_chunk is not None:
                    change_type = 'ADDITION' if line.startswith('+') else 'DELETION'
                    current_chunk['changes'].append({
                        'type': change_type,
                        'line': current_line_number if change_type == 'ADDITION' else current_line_number - 1,
                        'content': line[1:]  # Remove the + or - prefix
                    })
                    if change_type == 'ADDITION':
                        current_line_number += 1
            elif line.startswith(' '):
                # Unchanged line
                current_line_number += 1
        
        # Add the last file and chunk if they exist
        if current_chunk is not None and current_file is not None:
            current_file['chunks'].append(current_chunk)
        if current_file is not None:
            structured_diff.append(current_file)
            
        return structured_diff

    def post_review_comment(self, repo: str, pr_number: int, body: str, line_number: int, path: str, 
                          change_type: str, pr_details: dict = None):
        endpoint: str = f"/repos/{self.api_client.owner}/{repo}/pulls/{pr_number}/comments"
        
        try:
            if pr_details is None:
                pr_details = self.fetch_pr_context(repo, pr_number)
            commit_id = pr_details["head"]["sha"]
            
            clean_path: str = path.replace('b/', '') if path.startswith('b/') else path
            
            side: Literal['RIGHT'] | Literal['LEFT'] = "RIGHT" if change_type == ChangeType.ADDITION else "LEFT"
            
            lines: List[str] = body.split('\n')
            end_line: int = line_number + len(lines) - 1
            
            data: Dict[str, Any] = {
                "body": body,
                "commit_id": commit_id,
                "path": clean_path,
                "side": side,
            }
            
            if len(lines) > 1:
                data["start_line"] = line_number
                data["start_side"] = side
                data["line"] = end_line
                data["end_side"] = side
            else:
                data["line"] = line_number
            logger.debug(f"Posting review comment: {data}")
            with self.api_client.with_headers({"Accept": "application/vnd.github+json"}):
                response = self.api_client.post(endpoint, data=data)
            return response
        except RequestException as e:
            if hasattr(e.response, 'status_code'):
                if e.response.status_code == 404:
                    raise GitHubServiceError(f"PR not found. Please check if repository '{repo}' and PR number {pr_number} are correct.")
                elif e.response.status_code == 403:
                    raise GitHubServiceError(
                        f"Access forbidden. Please check:\n"
                        f"1. Your token has 'pull_request' write permissions\n"
                        f"2. The repository '{repo}' exists and is accessible\n"
                        f"3. The PR number {pr_number} is correct\n"
                        f"4. Your token is valid and not expired"
                    )
                elif e.response.status_code == 422:
                    error_msg = e.response.json().get("message", "Validation failed")
                    errors = e.response.json().get("errors", [])
                    error_details = "\n".join([f"- {err.get('field')}: {err.get('code')}" for err in errors])
                    raise GitHubServiceError(f"{error_msg}\n{error_details}")
            raise GitHubServiceError(f"Failed to post review comment: {str(e)}")

    def fetch_pr_context(self, repo: str, pr_number: int):
        endpoint = f"/repos/{self.api_client.owner}/{repo}/pulls/{pr_number}"
        try:
            response = self.api_client.get(endpoint)
            return response
        except RequestException as e:
            if hasattr(e.response, 'status_code'):
                if e.response.status_code == 404:
                    raise GitHubServiceError(f"PR not found. Please check if repository '{repo}' and PR number {pr_number} are correct.")
                elif e.response.status_code == 403:
                    raise GitHubServiceError(f"Access forbidden. Please check if your token has sufficient permissions and the repository exists.")
            raise GitHubServiceError(f"Failed to fetch PR context: {str(e)}")


class GitHubServiceError(Exception):
    """Custom exception for GitHub service errors"""
    pass
