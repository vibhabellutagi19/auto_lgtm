import os
import sys
from typing import List, Dict, Any
from loguru import logger

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auto_lgtm.lgtm import post_comments
from auto_lgtm.services.github_service import GitHubService, GitHubServiceError
from auto_lgtm.factories.github_factory import GitHubServiceFactory
from auto_lgtm.services.llm_service import LLMService
from auto_lgtm.services.review_service import DiffParser, ReviewService
from auto_lgtm.models.review_models import ReviewResponse, ReviewContext

GITHUB_OWNER = "vibhabellutagi19"
REPO = "lgtm_test"
PR_NUMBER = 13
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "autolgtm") 
SECRET_ID = os.getenv("SECRET_ID", "lgtm-secrets")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN","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")


def review_pr() -> None:
    """
    Main function to review a pull request.
    This is the core function that can be called by both CLI and webhook.
    
    Args:
        repo: Repository name
        pr_number: Pull request number
        project_id: Google Cloud project ID
    """
    try:
        github_service: GitHubService = GitHubServiceFactory.create(GITHUB_TOKEN, GITHUB_OWNER)
        
        structured_diff: List[Dict[str, Any]] = github_service.fetch_pr_diff(REPO, PR_NUMBER)
            
        logger.info("Fetching PR context...")
        pr_details = github_service.fetch_pr_context(REPO, PR_NUMBER)

        context = ReviewContext(
            repo=REPO,
            pr_number=PR_NUMBER,
            pr_details=pr_details,
            diff_content=structured_diff
        )

        user_query = "Analyze the following changes with right line number and provide feedback on the code."
        logger.info("Initializing LLM service")
        llm_service = LLMService(user_query=user_query, project_id=PROJECT_ID)
        diff_parser = DiffParser()
        review_service = ReviewService(diff_parser, llm_service, pr_details)
        
        logger.info("Analyzing diff")
        changes: List[Dict[str, Any]] = review_service.analyze_diff(structured_diff)
            
        logger.info("Generating review comments")
        review_response: ReviewResponse = review_service.generate_comments(changes)
        
        logger.info(f"Generated {len(review_response.comments)} review comments")

        post_comments(github_service, review_response, context)
        
        logger.success("Auto LGTM process completed successfully!")

    except GitHubServiceError as e:
        logger.error(f"GitHub service error: {e}")
        raise
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error in review_pr: {str(e)}")
        raise

if __name__ == "__main__":
    review_pr()