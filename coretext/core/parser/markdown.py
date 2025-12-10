import re
from pathlib import Path
from typing import List, Tuple

from markdown_it import MarkdownIt
from markdown_it.token import Token

from coretext.core.parser.path_utils import normalize_path_to_project_root
from coretext.core.graph.models import BaseNode, FileNode, HeaderNode, ParsingErrorNode, BaseEdge

class MarkdownParser:
    """
    Parses BMAD Markdown files using an AST-based method.

    Attributes:
        md (MarkdownIt): An instance of the markdown-it parser.
    """

    def __init__(self):
        """
        Initializes the MarkdownParser with CommonMark compliance.
        """
        self.md = MarkdownIt("commonmark")

    def _process_link_token(self, link_token: Token, current_file_path: Path, file_node: FileNode, nodes: List[BaseNode], edges: List[BaseEdge], content_lines: List[str], link_index: int):
        """Helper function to process link_open tokens and create REFERENCES edges or ParsingErrorNodes."""
        href = None
        if link_token.attrs:
            href = link_token.attrs.get("href")
        
        if href:
            try:
                # Normalize the link target path
                normalized_link_path = normalize_path_to_project_root(current_file_path, href)
                
                # VALIDATION: Check if target exists
                # We need to resolve the full path to check existence
                # normalize_path_to_project_root doesn't return the full absolute path, so we re-resolve
                project_root = None
                for parent in current_file_path.parents:
                    if (parent / "pyproject.toml").exists() or (parent / ".git").is_dir():
                        project_root = parent
                        break
                
                full_target_path = project_root / normalized_link_path if project_root else Path(normalized_link_path)

                if not full_target_path.exists():
                     # Treat as broken link -> Parsing Error
                    line_number = link_token.map[0] + 1 if link_token.map else 0
                    raw_snippet = content_lines[link_token.map[0]] if link_token.map and link_token.map[0] < len(content_lines) else ""
                    error_node = ParsingErrorNode(
                        id=f"{file_node.id}#link-error-line-{line_number}-{link_index}",
                        file_path=file_node.file_path,
                        line_number=line_number,
                        error_message=f"Broken link: Target '{href}' does not exist.",
                        raw_content_snippet=raw_snippet
                    )
                    nodes.append(error_node)
                    return

                # Create a REFERENCES edge
                # Ensure unique ID by appending index
                edge_id = f"{file_node.id}-REFERENCES-{normalized_link_path}-{link_index}"
                
                edges.append(BaseEdge(
                    id=edge_id,
                    edge_type="REFERENCES",
                    source=file_node.id,
                    target=str(normalized_link_path)
                ))
            except ValueError as e:
                # Handle cases where link target cannot be normalized (e.g., external links, invalid paths)
                line_number = link_token.map[0] + 1 if link_token.map else 0
                raw_snippet = content_lines[link_token.map[0]] if link_token.map and link_token.map[0] < len(content_lines) else ""
                error_node = ParsingErrorNode(
                    id=f"{file_node.id}#link-error-line-{line_number}-{link_index}",
                    file_path=file_node.file_path,
                    line_number=line_number,
                    error_message=f"Malformed or unresolvable link target: {href}. Error: {e}",
                    raw_content_snippet=raw_snippet
                )
                nodes.append(error_node)

    def parse(self, file_path: Path) -> Tuple[List[BaseNode], List[BaseEdge]]:
        """
        Parses a Markdown file and converts its content into a list of BaseNodes and BaseEdges.

        Args:
            file_path (Path): The path to the Markdown file.

        Returns:
            Tuple[List[BaseNode], List[BaseEdge]]: A tuple containing lists of graph nodes and edges.
        """
        if not file_path.is_file():
            raise FileNotFoundError(f"Markdown file not found: {file_path}")

        normalized_file_path = normalize_path_to_project_root(file_path, str(file_path))

        content = file_path.read_text()
        tokens = self.md.parse(content)

        nodes: List[BaseNode] = []
        edges: List[BaseEdge] = []

        # 1. Create a FileNode for the markdown file itself
        file_node = FileNode(id=str(normalized_file_path), file_path=normalized_file_path, content=content)
        nodes.append(file_node)

        header_stack = [] # To manage PARENT_OF relationships
        
        # Split content into lines for error snippet
        content_lines = content.splitlines()

        link_counter = 0

        # Iterate through the top-level tokens
        for i, token in enumerate(tokens):
            if token.type == "heading_open":
                level = int(token.tag[1]) # e.g., "h1" -> 1
                
                header_content_token_index = i + 1
                header_content = ""
                if header_content_token_index < len(tokens) and tokens[header_content_token_index].type == "inline":
                    header_content = tokens[header_content_token_index].content

                # --- ERROR DETECTION: Empty Header Content ---
                if not header_content.strip():
                    line_number = token.map[0] + 1 if token.map else 0
                    raw_snippet = content_lines[token.map[0]] if token.map and token.map[0] < len(content_lines) else ""
                    error_node = ParsingErrorNode(
                        id=f"{normalized_file_path}#parsing-error-line-{line_number}",
                        file_path=normalized_file_path,
                        line_number=line_number,
                        error_message="Header has no content.",
                        raw_content_snippet=raw_snippet
                    )
                    nodes.append(error_node)
                    continue
                # --- END ERROR DETECTION ---
                
                # Generate a robust slug for the header ID
                slug = re.sub(r'[^a-z0-9]+', '-', header_content.lower()) # Replace non-alphanumeric with dashes
                slug = slug.strip('-') # Remove leading/trailing dashes
                
                header_id = f"{normalized_file_path}#{slug}"

                new_header_node = HeaderNode(
                    id=header_id,
                    file_path=normalized_file_path,
                    level=level,
                    content=header_content
                )
                nodes.append(new_header_node)

                # Define CONTAINS relationship: File -> Header
                edges.append(BaseEdge(
                    id=f"{file_node.id}-CONTAINS-{new_header_node.id}",
                    edge_type="CONTAINS",
                    source=file_node.id,
                    target=new_header_node.id
                ))

                # Define PARENT_OF relationship: Header -> Sub-Header
                while header_stack and header_stack[-1].level >= level:
                    header_stack.pop()
                if header_stack:
                    parent_header = header_stack[-1]
                    edges.append(BaseEdge(
                        id=f"{parent_header.id}-PARENT_OF-{new_header_node.id}",
                        edge_type="PARENT_OF",
                        source=parent_header.id,
                        target=new_header_node.id
                    ))
                header_stack.append(new_header_node)

            elif token.type == "inline": # Process inline tokens to find nested links and implicit references
                # Process children of inline token
                if token.children:
                    for child_token in token.children:
                        if child_token.type == "link_open":
                            link_counter += 1
                            self._process_link_token(child_token, file_path, file_node, nodes, edges, content_lines, link_counter)
                        elif child_token.type == "text" or child_token.type == "code_inline":
                            # Apply implicit link detection only to plain text or inline code
                            if child_token.content:
                                implicit_link_pattern = r"[\w\-/]+\.(md|yaml)"
                                for match in re.finditer(implicit_link_pattern, child_token.content):
                                    implicit_path = match.group(0)
                                    try:
                                        resolved_implicit_file = (file_path.parent / implicit_path).resolve()
                                        if resolved_implicit_file.is_file():
                                            normalized_implicit_path = normalize_path_to_project_root(file_path, str(resolved_implicit_file))
                                            link_counter += 1
                                            edges.append(BaseEdge(
                                                id=f"{file_node.id}-REFERENCES-{normalized_implicit_path}-{link_counter}",
                                                edge_type="REFERENCES",
                                                source=file_node.id,
                                                target=str(normalized_implicit_path)
                                            ))
                                    except ValueError:
                                        pass # Ignore errors for implicit links that don't resolve to project files
                
                # Also check the top-level inline token content for implicit links,
                # but only if it doesn't have children (meaning it's pure text)
                elif token.content:
                    implicit_link_pattern = r"[\w\-/]+\.(md|yaml)"
                    for match in re.finditer(implicit_link_pattern, token.content):
                        implicit_path = match.group(0)
                        try:
                            resolved_implicit_file = (file_path.parent / implicit_path).resolve()
                            if resolved_implicit_file.is_file():
                                normalized_implicit_path = normalize_path_to_project_root(file_path, str(resolved_implicit_file))
                                link_counter += 1
                                edges.append(BaseEdge(
                                    id=f"{file_node.id}-REFERENCES-{normalized_implicit_path}-{link_counter}",
                                    edge_type="REFERENCES",
                                    source=file_node.id,
                                    target=str(normalized_implicit_path)
                                ))
                        except ValueError:
                            pass # Ignore errors for implicit links that don't resolve to project files

            # TODO: Handle content associated with headers and other node types

        return nodes, edges