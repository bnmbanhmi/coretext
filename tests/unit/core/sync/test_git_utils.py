import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from coretext.core.sync.git_utils import get_staged_files, get_last_commit_files

@patch("coretext.core.sync.git_utils.Repo")
def test_get_staged_files(mock_repo_cls):
    mock_repo = mock_repo_cls.return_value
    mock_repo.git.diff.return_value = "doc1.md\nsrc/code.py\ndoc2.md"
    
    files = get_staged_files(Path("."))
    
    assert "doc1.md" in files
    assert "doc2.md" in files
    assert "src/code.py" not in files # Should filter .md
    mock_repo.git.diff.assert_called_with("--cached", "--name-only", "--diff-filter=ACMR")

@patch("coretext.core.sync.git_utils.Repo")
def test_get_last_commit_files(mock_repo_cls):
    mock_repo = mock_repo_cls.return_value
    mock_repo.git.diff.return_value = "doc1.md"
    
    files = get_last_commit_files(Path("."))
    
    assert "doc1.md" in files
    mock_repo.git.diff.assert_called_with("HEAD~1", "HEAD", "--name-only", "--diff-filter=ACMR")

@patch("coretext.core.sync.git_utils.Repo")
def test_get_last_commit_files_initial_commit(mock_repo_cls):
    mock_repo = mock_repo_cls.return_value
    # Simulate git diff failing (e.g., no HEAD~1)
    mock_repo.git.diff.side_effect = Exception("fatal: ambiguous argument 'HEAD~1'")
    mock_repo.git.show.return_value = "readme.md"
    
    files = get_last_commit_files(Path("."))
    
    assert "readme.md" in files
    mock_repo.git.show.assert_called_with("--name-only", "--format=", "HEAD")
