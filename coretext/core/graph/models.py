"""
Core Graph Models

This module defines the Pydantic models used to represent nodes and edges within the
CoreText knowledge graph. These models serve as the internal representation of graph
entities and are used for validation before persistence.
"""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

class BaseNode(BaseModel):
    """
    Base model for all graph nodes.
    
    Attributes:
        id (str): Unique ID for the node, typically a file path or header path.
        node_type (str): The type of the node (e.g., 'file', 'header').
        content (str): The main content associated with the node.
        metadata (dict[str, Any]): Arbitrary metadata for the node.
        created_at (datetime): Timestamp of node creation.
        updated_at (datetime): Timestamp of last node update.
    """
    id: str = Field(description="Unique ID for the node, typically a file path or header path.")
    node_type: str = Field(description="The type of the node (e.g., 'file', 'header').")
    content: str = Field(default="", description="The main content associated with the node.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata for the node.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of node creation.")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of last node update.")

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
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of edge creation.")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of last edge update.")
