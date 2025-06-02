from typing import Dict, List, Any
from auto_lgtm.services.llm_service import LLMService
from auto_lgtm.factories.github_app_factory import GitHubAppFactory
from auto_lgtm.services.github_service import GitHubService, GitHubServiceError
from auto_lgtm.services.review_service import ReviewService, DiffParser
from auto_lgtm.models.review_models import ReviewResponse, ReviewComment, ReviewContext
from auto_lgtm.services.secret_service import SecretService
import os
from loguru import logger

def review_pr(repo: str, pr_number: int, github_owner: str, project_id: str) -> None:
    """
    Main function to review a pull request.
    Triggers the LLM review, maps comments to diff positions, and posts a single review.
    """
    try:
        secret_service = SecretService(project_id)
        secret_id = os.getenv("SECRET_ID")
        installation_id = os.getenv("GITHUB_INSTALLATION_ID")
        
        if not installation_id:
            raise ValueError("GitHub App installation ID not found in environment variables")
            
        logger.info(f"Retrieving GitHub App credentials from Secret Manager (secret_id: {secret_id})")
        gemini_api_key: str = secret_service.get_secret(secret_id, "gemini_api_key")
        
        if not gemini_api_key:
            raise ValueError("Failed to retrieve Gemini API key from secrets")

        logger.info(f"Processing PR #{pr_number} in repository {repo}")
        github_app_factory = GitHubAppFactory(project_id, secret_id)
        github_client = github_app_factory.create_client(github_owner, installation_id)
        github_service = GitHubService(github_client)

        logger.info("Fetching PR diff and context...")
        structured_diff: List[Dict[str, Any]] = github_service.fetch_pr_diff(repo, pr_number)
        pr_details: str | Any = github_service.fetch_pr_context(repo, pr_number)

        user_query = "Analyze the following changes with right line number and provide feedback on the code."
        llm_service = LLMService(user_query=user_query, project_id=project_id, gemini_api_key=gemini_api_key)
        review_service = ReviewService(DiffParser(), llm_service, pr_details)

        logger.info("Analyzing diff and generating review comments...")
        changes: List[Dict[str, Any]] = review_service.analyze_diff(structured_diff)
        review_response: ReviewResponse = review_service.generate_comments(changes)
        logger.info(f"Generated {len(review_response.comments)} review comments")

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

        if review_comments:
            logger.info(f"Posting review with {len(review_comments)} comments to PR #{pr_number}")
            github_service.post_review(
                repo=repo,
                pr_number=pr_number,
                body="Automated review by Auto-LGTM.",
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
        logger.error(f"Error in review_pr: {str(e)}")
        raise
