from enum import Enum
from pathlib import Path
from typing import List, Callable, Optional
from pydantic import BaseModel

from coretext.core.parser.markdown import MarkdownParser
from coretext.core.graph.manager import GraphManager
from coretext.core.graph.models import ParsingErrorNode, BaseNode, BaseEdge

class SyncMode(str, Enum):
    DRY_RUN = "dry-run"
    WRITE = "write"

class SyncResult(BaseModel):
    success: bool
    processed_count: int = 0
    error_count: int = 0
    message: str = ""
    errors: List[str] = []

class SyncEngine:
    def __init__(self, parser: MarkdownParser, graph_manager: GraphManager):
        self.parser = parser
        self.graph_manager = graph_manager

    async def process_files(self, file_paths: List[str], mode: SyncMode, content_provider: Optional[Callable[[str], str]] = None, commit_hash: Optional[str] = None) -> SyncResult:
        processed_count = 0
        error_count = 0
        all_errors = []
        
        nodes_to_ingest: List[BaseNode] = []
        edges_to_ingest: List[BaseEdge] = []

        for file_path_str in file_paths:
            file_path = Path(file_path_str)
            try:
                # Parsing
                content = None
                if content_provider:
                    try:
                        content = content_provider(file_path_str)
                    except Exception as e:
                        error_count += 1
                        all_errors.append(f"File {file_path_str}: Failed to read content: {e}")
                        continue

                nodes, edges = self.parser.parse(file_path, content=content)
                processed_count += 1
                
                # Check for parsing errors immediately
                file_parsing_errors = [n for n in nodes if isinstance(n, ParsingErrorNode)]
                if file_parsing_errors:
                    error_count += len(file_parsing_errors)
                    for err in file_parsing_errors:
                         all_errors.append(f"File {file_path_str}: {err.error_message}")
                
                nodes_to_ingest.extend(nodes)
                edges_to_ingest.extend(edges)

            except Exception as e:
                error_count += 1
                all_errors.append(f"File {file_path_str}: Unexpected error: {str(e)}")

        # Propagate commit_hash to nodes and edges before ingestion
        if commit_hash:
            for node in nodes_to_ingest:
                node.commit_hash = commit_hash
            for edge in edges_to_ingest:
                edge.commit_hash = commit_hash

        if error_count > 0:
             return SyncResult(
                success=False,
                processed_count=processed_count,
                error_count=error_count,
                message=f"Sync failed with {error_count} errors.",
                errors=all_errors
            )

        if mode == SyncMode.WRITE:
            # Ingest to DB
            report = await self.graph_manager.ingest(nodes_to_ingest, edges_to_ingest)
            if not report.success:
                 # Extract errors from report if any
                 ingest_errors = []
                 if report.parsing_errors:
                     ingest_errors = [f"Ingestion error: {err.error_message}" for err in report.parsing_errors]
                 else:
                     ingest_errors.append(report.message)

                 return SyncResult(
                    success=False,
                    processed_count=processed_count,
                    error_count=len(report.parsing_errors) if report.parsing_errors else 1,
                    message=report.message,
                    errors=ingest_errors
                )

        return SyncResult(
            success=True,
            processed_count=processed_count,
            message="Sync completed successfully."
        )
