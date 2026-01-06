from fastapi import APIRouter, Depends
from typing import List, Optional
from pydantic import BaseModel
from pathlib import Path

from coretext.core.lint.manager import LintManager
from coretext.core.lint.models import LintReport

router = APIRouter()

class LintRequest(BaseModel):
    files: Optional[List[str]] = None
    project_root: Optional[str] = None

def get_project_root() -> Path:
    return Path.cwd()

def get_lint_manager(project_root: Path = Depends(get_project_root)) -> LintManager:
    return LintManager(project_root)

@router.post("/lint", response_model=LintReport)
async def lint_endpoint(
    request: LintRequest,
    project_root: Path = Depends(get_project_root)
):
    """
    Triggers a dry-run integrity check on Markdown files.
    """
    # Override project_root if provided in request
    if request.project_root:
        root_path = Path(request.project_root)
    else:
        root_path = project_root
        
    manager = LintManager(root_path)

    if request.files:
        # Resolve paths relative to project root and expand directories
        files_to_lint = []
        for f in request.files:
            p = root_path / f
            if p.is_dir():
                # Recursively find all .md files in the directory
                all_md = list(p.glob("**/*.md"))
                files_to_lint.extend([
                    m for m in all_md
                    if not any(part.startswith('.') for part in m.relative_to(root_path).parts)
                ])
            elif p.is_file():
                files_to_lint.append(p)
    else:
        # Find all .md files in project, excluding hidden directories
        all_md = list(root_path.glob("**/*.md"))
        files_to_lint = [
            f for f in all_md
            if not any(part.startswith('.') for part in f.relative_to(root_path).parts)
        ]

    return await manager.lint_files(files_to_lint)
