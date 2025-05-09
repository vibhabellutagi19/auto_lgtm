import json
import os
from typing import List, Dict, Any

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auto_lgtm.services.llm_service import LLMService
from auto_lgtm.factories.github_factory import GitHubServiceFactory
from auto_lgtm.services.github_service import GitHubService, GitHubServiceError
from auto_lgtm.services.review_service import ReviewService, DiffParser
from auto_lgtm.models.review_models import ReviewResponse
from loguru import logger

def review_pr_local(
    repo: str,
    pr_number: int,
    github_owner: str,
    github_token: str,
    project_id: str,
    gemini_api_key: str
) -> None:
    """
    Local version of review_pr that does not use Secret Manager.
    Expects the GitHub token to be provided directly.
    """
    try:
        logger.info(f"Processing PR #{pr_number} in repository {repo}")
        github_service = GitHubServiceFactory.create(github_token, github_owner)

        logger.info("Fetching PR diff and context...")
        structured_diff = github_service.fetch_pr_diff(repo, pr_number)
        pr_details = github_service.fetch_pr_context(repo, pr_number)

        user_query = "Analyze the following changes with right line number and provide feedback on the code."
        llm_service = LLMService(user_query=user_query, project_id=project_id, gemini_api_key=gemini_api_key)
        review_service = ReviewService(DiffParser(), llm_service, pr_details)

        logger.info("Analyzing diff and generating review comments...")
        changes: List[Dict[str, Any]] = review_service.analyze_diff(structured_diff)
        review_response: ReviewResponse = review_service.generate_comments(changes)

        review_comments = []
        for comment in review_response.comments:
            position = github_service.get_diff_position(
                repo=repo,
                pr_number=pr_number,
                file_path=comment.file,
                line_number=comment.line_number
            )
            if position is not None:
                review_comments.append({
                    "path": comment.file,
                    "position": position,
                    "body": comment.comment
                })
            else:
                logger.warning(f"Could not map {comment.file}:{comment.line_number} to a diff position. Skipping comment.")

        # Post the review
        if review_comments:
            logger.info(f"Posting review with {len(review_comments)} comments to PR #{pr_number}")
            github_service.post_review(
                repo=repo,
                pr_number=pr_number,
                body="Automated review by Auto-LGTM (local).",
                comments=review_comments,
                event="COMMENT"
            )
            logger.info("Review posted successfully!")
        else:
            logger.info("No valid review comments to post.")

        logger.success("Auto LGTM process completed successfully!")

    except GitHubServiceError as e:
        logger.error(f"GitHub service error: {e}")
        raise
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error in review_pr_local: {str(e)}")
        raise

if __name__ == "__main__":
    REPO = "lgtm_test"
    PR_NUMBER = 14
    GITHUB_OWNER = "vibhabellutagi19"
    
    with open("auto_lgtm/secrets.json", "r") as f:
        secrets = json.load(f)
    GITHUB_TOKEN = secrets["github_token"]
    PROJECT_ID = secrets["project_id"]
    GEMINI_API_KEY = secrets["gemini_api_key"]

    if not GITHUB_TOKEN or not GEMINI_API_KEY:
        print("Please set the GITHUB_TOKEN and GEMINI_API_KEY environment variables.")
    else:
        review_pr_local(
            repo=REPO,
            pr_number=PR_NUMBER,
            github_owner=GITHUB_OWNER,
            github_token=GITHUB_TOKEN,
            project_id=PROJECT_ID,
            gemini_api_key=GEMINI_API_KEY
        )