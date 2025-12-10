from git import Repo
from pathlib import Path
from typing import List

def get_staged_files(repo_path: Path) -> List[str]:
    """Returns a list of staged Markdown file paths (relative to repo root)."""
    try:
        repo = Repo(repo_path)
        # diff-filter=ACMR: Added, Copied, Modified, Renamed
        files = repo.git.diff("--cached", "--name-only", "--diff-filter=ACMR").splitlines()
        return [f for f in files if f.endswith(".md")]
    except Exception:
        return []

def get_last_commit_files(repo_path: Path) -> List[str]:
    """Returns list of Markdown files changed in the last commit (HEAD)."""
    try:
        repo = Repo(repo_path)
        try:
            files = repo.git.diff("HEAD~1", "HEAD", "--name-only", "--diff-filter=ACMR").splitlines()
        except Exception:
            # Fallback for initial commit
            files = repo.git.show("--name-only", "--format=", "HEAD").splitlines()
            
        return [f for f in files if f.endswith(".md")]
    except Exception:
        return []

def get_staged_content(repo_path: Path, file_path: str) -> str:
    """Reads content of a file from the git index (staged)."""
    repo = Repo(repo_path)
    # file_path is relative to repo root
    return repo.git.show(f":{file_path}")

def get_head_content(repo_path: Path, file_path: str) -> str:
    """Reads content of a file from HEAD commit."""
    repo = Repo(repo_path)
    return repo.git.show(f"HEAD:{file_path}")

def get_current_commit_hash(repo_path: Path) -> str | None:
    """Retrieves the current HEAD commit hash of the repository."""
    try:
        repo = Repo(repo_path)
        return repo.head.commit.hexsha
    except Exception:
        return None

