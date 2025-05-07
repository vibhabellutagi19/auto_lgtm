from enum import Enum
from typing import List, Dict, Any
from pydantic import BaseModel

class ChangeType(str, Enum):
    ADDITION = "addition"
    DELETION = "deletion"
    MODIFICATION = "modification"

class SeverityLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

class ReviewComment(BaseModel):
    file: str
    line_number: int
    line_content: str
    change_type: ChangeType
    severity: SeverityLevel
    comment: str

class ReviewResponse(BaseModel):
    comments: List[ReviewComment]

class ReviewContext(BaseModel):
    """Context data needed for posting review comments"""
    repo: str
    pr_number: int
    pr_details: dict
    diff_content: List[Dict[str, Any]]