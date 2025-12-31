from pathlib import Path
from typing import List
from coretext.core.parser.markdown import MarkdownParser
from coretext.core.graph.models import ParsingErrorNode, BaseNode
from coretext.core.lint.models import LintReport, LintIssue

class LintManager:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.parser = MarkdownParser(project_root)

    async def lint_files(self, files: List[Path]) -> LintReport:
        report = LintReport()
        
        for file_path in files:
            # We assume files are passed as Paths
            if not file_path.exists():
                continue
                
            # Parse the file
            # parser.parse returns (nodes, edges)
            # It catches its own errors and returns ParsingErrorNode
            try:
                nodes, _ = self.parser.parse(file_path)
                
                for node in nodes:
                    if isinstance(node, ParsingErrorNode):
                        # Determine error type based on node ID or message content
                        error_type = "Parsing Error"
                        if "Dangling Reference" in node.error_message:
                            error_type = "Broken Link"
                        
                        report.add_issue(LintIssue(
                            file_path=str(node.file_path),
                            line_number=node.line_number,
                            error_type=error_type,
                            message=node.error_message,
                            raw_content_snippet=node.raw_content_snippet
                        ))
            except Exception as e:
                # Fallback for unexpected crashes
                try:
                    rel_path = str(file_path.relative_to(self.project_root))
                except ValueError:
                    rel_path = str(file_path)
                    
                report.add_issue(LintIssue(
                    file_path=rel_path,
                    line_number=0,
                    error_type="Unexpected Error",
                    message=str(e)
                ))
                
        return report
