import asyncio
from enum import Enum
from pathlib import Path
from typing import List, Callable, Optional, Tuple
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
    SYNC_ASYNC_THRESHOLD_FILES = 5

    def __init__(self, parser: MarkdownParser, graph_manager: GraphManager, project_root: Path):
        self.parser = parser
        self.graph_manager = graph_manager
        self.project_root = project_root

    @staticmethod
    def should_detach(file_count: int) -> bool:
        """Determines if the sync operation should be detached based on file count."""
        return file_count > SyncEngine.SYNC_ASYNC_THRESHOLD_FILES

    def _parse_single_file(self, file_path: Path, content: Optional[str]) -> Tuple[List[BaseNode], List[BaseEdge], List[str]]:
        """Parses a single file, handling potential exceptions and returning nodes, edges, and errors."""
        file_errors = []
        try:
            nodes, edges = self.parser.parse(file_path, content=content)
            
            # Check for parsing errors immediately
            file_parsing_errors = [n for n in nodes if isinstance(n, ParsingErrorNode)]
            if file_parsing_errors:
                for err in file_parsing_errors:
                     file_errors.append(f"File {file_path}: {err.error_message}")
            
            return nodes, edges, file_errors
        except Exception as e:
            file_errors.append(f"File {file_path}: Unexpected error during parsing: {str(e)}")
            return [], [], file_errors


    async def process_files(self, file_paths_str: List[str], mode: SyncMode, content_provider: Optional[Callable[[str], str]] = None, commit_hash: Optional[str] = None) -> SyncResult:
        processed_count = 0
        error_count = 0
        all_errors = []
        
        nodes_to_ingest: List[BaseNode] = []
        edges_to_ingest: List[BaseEdge] = []

        async def get_content_and_parse(file_path_str: str):
            file_path = Path(file_path_str)
            content = None
            if content_provider:
                try:
                    content = await asyncio.to_thread(content_provider, file_path_str)
                except Exception as e:
                    return file_path, [], [], [f"File {file_path_str}: Failed to read content: {e}"]

            # Run CPU-bound parsing in a separate thread
            nodes, edges, file_errors = await asyncio.to_thread(self._parse_single_file, file_path, content)
            return file_path, nodes, edges, file_errors

        tasks = [get_content_and_parse(fp) for fp in file_paths_str]
        results = await asyncio.gather(*tasks)

        for file_path, nodes, edges, file_errors in results:
            processed_count += 1
            if file_errors:
                error_count += len(file_errors)
                all_errors.extend(file_errors)
            
            nodes_to_ingest.extend(nodes)
            edges_to_ingest.extend(edges)

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
