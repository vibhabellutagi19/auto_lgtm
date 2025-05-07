from typing import List, Dict, Any
from enum import Enum
import json

from prompts.pr_review_prompt import PR_REVIEW_PROMPT
from models.review_models import ReviewResponse, ReviewComment, ChangeType, SeverityLevel

from .llm_service import LLMService

class DiffParser:
    """
    Responsible for parsing code diffs and extracting useful information.
    """
    def parse(self, structured_diff: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
        return changes

    def create_review_comment(self, file: str, line_number: int, line_content: str, 
                            change_type: ChangeType, severity: SeverityLevel, comment: str) -> ReviewComment:
        """
        Creates a ReviewComment instance with the provided parameters.
        """
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
        changes: List[Dict[str, Any]] = self.diff_parser.parse(structured_diff)
        return changes

    def generate_comments(self, changes: List[Dict[str, Any]]) -> ReviewResponse:
        pr_metadata = {
            "title": self.pr_details["title"],
            "body": self.pr_details["body"]
        }

        system_prompt: str = PR_REVIEW_PROMPT.format(
            changes=changes,
            pr_metadata=pr_metadata
        )
        self.llm_service.set_system_prompt(system_prompt)

        raw_comments: str = self.llm_service.generate_response()
        comments_list = json.loads(raw_comments)
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
        return ReviewResponse(comments=review_comments)