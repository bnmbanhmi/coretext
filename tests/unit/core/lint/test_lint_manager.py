import pytest
from pathlib import Path
from coretext.core.lint.manager import LintManager
from coretext.core.lint.models import LintReport, LintIssue

@pytest.mark.asyncio
async def test_lint_manager_check_markdown_syntax(tmp_path):
    # Setup
    # Create a dummy bad markdown file (Empty header triggers error in MarkdownParser)
    bad_file = tmp_path / "bad.md"
    bad_file.write_text("# ") 

    # Create a dummy good file
    good_file = tmp_path / "good.md"
    good_file.write_text("# Good Header\nContent")

    # Create a dummy broken link file
    broken_link_file = tmp_path / "broken.md"
    broken_link_file.write_text("[Broken](./missing.md)")
    
    manager = LintManager(project_root=tmp_path)
    
    # Execution
    report = await manager.lint_files([bad_file, good_file, broken_link_file])
    
    # Verification
    assert isinstance(report, LintReport)
    assert len(report.issues) == 2
    
    # Check for empty header error
    header_issues = [i for i in report.issues if "Header has no content" in i.message]
    assert len(header_issues) == 1
    # Check strict path equality or substring depending on implementation. 
    # Parser usually returns relative paths.
    assert str(bad_file.name) in header_issues[0].file_path
    
    # Check for broken link error
    link_issues = [i for i in report.issues if "Dangling Reference" in i.message]
    assert len(link_issues) == 1
    assert str(broken_link_file.name) in link_issues[0].file_path
