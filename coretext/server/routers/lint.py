from fastapi import APIRouter, Depends
from typing import List, Optional
from pydantic import BaseModel
from pathlib import Path

from coretext.core.lint.manager import LintManager
from coretext.core.lint.models import LintReport

router = APIRouter()

class LintRequest(BaseModel):
    files: Optional[List[str]] = None

def get_project_root() -> Path:
    return Path.cwd()

def get_lint_manager(project_root: Path = Depends(get_project_root)) -> LintManager:
    return LintManager(project_root)

@router.post("/lint", response_model=LintReport)
async def lint_endpoint(
    request: LintRequest,
    manager: LintManager = Depends(get_lint_manager),
    project_root: Path = Depends(get_project_root)
):
    """
    Triggers a dry-run integrity check on Markdown files.
    """
    if request.files:
        # Resolve paths relative to project root
        files_to_lint = [project_root / f for f in request.files]
    else:
        # Find all .md files in project, excluding hidden directories
        all_md = list(project_root.glob("**/*.md"))
        files_to_lint = [
            f for f in all_md
            if not any(part.startswith('.') for part in f.relative_to(project_root).parts)
        ]

    return await manager.lint_files(files_to_lint)
