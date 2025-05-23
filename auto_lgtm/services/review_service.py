from typing import List, Dict, Any
from enum import Enum
import json
from loguru import logger

from auto_lgtm.prompts.pr_review_prompt import PR_REVIEW_PROMPT
from auto_lgtm.models.review_models import ReviewResponse, ReviewComment, ChangeType, SeverityLevel

from auto_lgtm.services.llm_service import LLMService

class DiffParser:
    """
    Responsible for parsing code diffs and extracting useful information.
    """
    def parse(self, structured_diff: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        logger.info(f"Parsing structured diff with {len(structured_diff)} files.")
        changes = []
        for file_diff in structured_diff:
            file_path = file_diff['file']
            for chunk in file_diff['chunks']:
                for change in chunk['changes']:
                    changes.append({
                        "file": file_path,
                        "line_number": change['line'],
                        "line_content": change['content'],
                        "change_type": ChangeType.ADDITION if change['type'] == 'ADDITION' else ChangeType.DELETION
                    })
        logger.info(f"Parsed {len(changes)} changes from diff.")
        return changes

    def create_review_comment(self, file: str, line_number: int, line_content: str, 
                            change_type: ChangeType, severity: SeverityLevel, comment: str) -> ReviewComment:
        """
        Creates a ReviewComment instance with the provided parameters.
        """
        logger.debug(f"Creating review comment for {file}:{line_number} [{change_type}] {severity}")
        return ReviewComment(
            file=file,
            line_number=line_number,
            line_content=line_content,
            change_type=change_type,
            severity=severity,
            comment=comment
        )

class ReviewService:
    """
    Analyzes code diffs and generates review comments using an LLM.
    """
    def __init__(self, diff_parser: DiffParser, llm_service: LLMService, pr_details: Dict[str, Any] = None):
        self.diff_parser = diff_parser
        self.llm_service = llm_service
        self.pr_details = pr_details

    def analyze_diff(self, structured_diff: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        logger.info("Analyzing diff...")
        changes: List[Dict[str, Any]] = self.diff_parser.parse(structured_diff)
        logger.info(f"Found {len(changes)} changes to analyze.")
        return changes

    def generate_comments(self, changes: List[Dict[str, Any]]) -> ReviewResponse:
        logger.info(f"Generating review comments for {len(changes)} changes.")
        pr_metadata = {
            "title": self.pr_details["title"],
            "body": self.pr_details["body"]
        }

        system_prompt: str = PR_REVIEW_PROMPT.format(
            changes=changes,
            pr_metadata=pr_metadata
        )
        self.llm_service.set_system_prompt(system_prompt)
        comments_list = self.llm_service.generate_response()
        review_comments = [
            ReviewComment(
                file=comment["file"],
                line_number=comment["line_number"],
                line_content=comment["line_content"],
                change_type=ChangeType(comment["change_type"]),
                severity=SeverityLevel(comment["severity"]),
                comment=comment["comment"]
            )
            for comment in comments_list
        ]
        logger.info(f"Generated {len(review_comments)} review comments.")
        return ReviewResponse(comments=review_comments)