"""
Core Graph Models

This module defines the Pydantic models used to represent nodes and edges within the
CoreText knowledge graph. These models serve as the internal representation of graph
entities and are used for validation before persistence.
"""

from datetime import datetime
from typing import Any, List, Literal # Added Literal
from pathlib import Path
from pydantic import BaseModel, Field

class BaseNode(BaseModel):
    """
    Base model for all graph nodes.
    
    Attributes:
        id (str): Unique ID for the node, typically a file path or header path.
        node_type (str): The type of the node (e.g., 'file', 'header').
        content: str = Field(default="", description="The main content associated with the node.")
        metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata for the node.")
        commit_hash: str | None = Field(default=None, description="Git commit hash associated with this graph entity.")
        created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of node creation.")
        updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of last node update.")
    """
    id: str = Field(description="Unique ID for the node, typically a file path or header path.")
    node_type: str = Field(description="The type of the node (e.g., 'file', 'header').")
    content: str = Field(default="", description="The main content associated with the node.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata for the node.")
    commit_hash: str | None = Field(default=None, description="Git commit hash associated with this graph entity.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of node creation.")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of last node update.")


class FileNode(BaseNode):
    """
    Represents a Markdown file node in the graph.
    The ID for a FileNode should be its project-root relative path.
    """
    node_type: Literal["file"] = Field("file", description="The type of the node, fixed to 'file'.")
    path: Path = Field(description="The project-root relative path to the file.")
    title: str = Field(default="", description="The title extracted from the file's content.")
    summary: str = Field(default="", description="A summary extracted from the file's content.")


class HeaderNode(BaseNode):
    """
    Represents a Markdown header node in the graph.
    The ID for a HeaderNode should be a combination of its file path and header slug.
    """
    node_type: Literal["header"] = Field("header", description="The type of the node, fixed to 'header'.")
    path: Path = Field(description="The project-root relative path to the file containing this header.")
    level: int = Field(ge=1, le=6, description="The header level (e.g., 1 for H1, 2 for H2).")
    title: str = Field(default="", description="The title of the header.")


class ParsingErrorNode(BaseNode):
    """
    Represents a parsing error encountered while processing a Markdown file.
    """
    node_type: Literal["parsing_error"] = Field("parsing_error", description="The type of the node, fixed to 'parsing_error'.")
    file_path: Path = Field(description="The project-root relative path to the file where the error occurred.")
    line_number: int = Field(description="The line number where the parsing error was detected.")
    error_message: str = Field(description="A descriptive message of the parsing error.")
    raw_content_snippet: str = Field(description="A snippet of the malformed content that caused the error.")


class BaseEdge(BaseModel):
    """
    Base model for all graph edges.
    
    Attributes:
        id (str): Unique ID for the edge.
        edge_type (str): The type of the edge (e.g., 'contains', 'parent_of').
        source (str): The ID of the source node.
        target (str): The ID of the target node.
        metadata (dict[str, Any]): Arbitrary metadata for the edge.
        created_at (datetime): Timestamp of edge creation.
        updated_at (datetime): Timestamp of last edge update.
    """
    id: str = Field(description="Unique ID for the edge.")
    edge_type: str = Field(description="The type of the edge (e.g., 'contains', 'parent_of').")
    source: str = Field(description="The ID of the source node.")
    target: str = Field(description="The ID of the target node.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata for the edge.")
    commit_hash: str | None = Field(default=None, description="Git commit hash associated with this graph entity.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of edge creation.")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of last edge update.")


class SyncReport(BaseModel):
    """
    Report summarizing the outcome of a graph synchronization operation.
    """
    success: bool = Field(description="True if the synchronization operation was successful, False otherwise.")
    message: str = Field(description="A human-readable message detailing the outcome or any errors.")
    nodes_created: int = Field(default=0, description="Number of nodes created.")
    edges_created: int = Field(default=0, description="Number of edges created.")
    parsing_errors: List[ParsingErrorNode] = Field(default_factory=list, description="List of parsing errors encountered.")
