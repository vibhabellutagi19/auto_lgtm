from typing import Dict, List, Any
from services.llm_service import LLMService
from factories.github_factory import GitHubServiceFactory
from services.github_service import GitHubService, GitHubServiceError
from services.review_service import ReviewService, DiffParser
from models.review_models import ReviewResponse, ReviewComment, ReviewContext
from services.secret_service import SecretService
import os
from loguru import logger

def post_comments(github_service: GitHubService, review_response: ReviewResponse, context: ReviewContext):
    logger.info(f"Posting {len(review_response.comments)} comments to PR #{context.pr_number}")
    for comment in review_response.comments:
        github_service.post_review_comment(
            repo=context.repo,
            pr_number=context.pr_number,
            body=comment.comment,
            line_number=comment.line_number,
            path=comment.file,
            change_type=comment.change_type,
            pr_details=context.pr_details
        )
    logger.info("All comments posted successfully")

def review_pr(repo: str, pr_number: int, project_id: str) -> None:
    """
    Main function to review a pull request.
    This is the core function that can be called by both CLI and webhook.
    
    Args:
        repo: Repository name
        pr_number: Pull request number
        project_id: Google Cloud project ID
    """
    try:
        # Initialize secret service
        secret_service = SecretService(project_id)
        
        # Get secrets from Secret Manager
        token = secret_service.get_secret("github-token")
        if not token:
            raise ValueError("Failed to retrieve GitHub token from Secret Manager")

        logger.info(f"Processing PR #{pr_number} in repository {repo}")

        # Create GitHub service
        github_service: GitHubService = GitHubServiceFactory.create(token)
        
        # Fetch PR diff
        logger.info("Fetching PR diff...")
        structured_diff: List[Dict[str, Any]] = github_service.fetch_pr_diff(repo, pr_number)
            
        # Fetch PR context
        logger.info("Fetching PR context...")
        pr_details = github_service.fetch_pr_context(repo, pr_number)
        
        logger.info(f"PR title: {pr_details['title']}")

        # Create review context
        context = ReviewContext(
            repo=repo,
            pr_number=pr_number,
            pr_details=pr_details,
            diff_content=structured_diff
        )

        # Initialize services with project_id
        user_query = "Analyze the following changes with right line number and provide feedback on the code."
        logger.info("Initializing LLM service")
        llm_service = LLMService(user_query=user_query, project_id=project_id)
        diff_parser = DiffParser()
        review_service = ReviewService(diff_parser, llm_service, pr_details)
        
        # Analyze diff
        logger.info("Analyzing diff")
        changes: List[Dict[str, Any]] = review_service.analyze_diff(structured_diff)
            
        # Generate review comments
        logger.info("Generating review comments")
        review_response: ReviewResponse = review_service.generate_comments(changes)
        
        logger.info(f"Generated {len(review_response.comments)} review comments")

        # Post comments
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
