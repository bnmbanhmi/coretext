from pydantic import BaseModel
from typing import List, Optional

class LintIssue(BaseModel):
    file_path: str
    line_number: int
    error_type: str
    message: str
    raw_content_snippet: Optional[str] = None

class LintReport(BaseModel):
    issues: List[LintIssue] = []
    
    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0
        
    def add_issue(self, issue: LintIssue):
        self.issues.append(issue)
