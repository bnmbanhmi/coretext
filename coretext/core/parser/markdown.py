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

    def __init__(self, project_root: Path):
        """
        Initializes the MarkdownParser with CommonMark compliance.
        
        Args:
            project_root (Path): The root directory of the project.
        """
        self.md = MarkdownIt("commonmark")
        self.project_root = project_root
        self._file_anchors_cache = {}

    def _generate_slug(self, text: str) -> str:
        """Generates a robust slug for header IDs."""
        slug = re.sub(r'[^a-z0-9]+', '-', text.lower()) # Replace non-alphanumeric with dashes
        return slug.strip('-') # Remove leading/trailing dashes

    def _get_anchors_for_file(self, file_path: Path) -> set[str]:
        """Parses a file to extract all header anchors (slugs). Caches results."""
        if file_path in self._file_anchors_cache:
            return self._file_anchors_cache[file_path]

        anchors = set()
        if not file_path.exists():
            return anchors

        try:
            content = file_path.read_text()
            tokens = self.md.parse(content)
            
            for i, token in enumerate(tokens):
                if token.type == "heading_open":
                    header_content_token_index = i + 1
                    if header_content_token_index < len(tokens) and tokens[header_content_token_index].type == "inline":
                        header_content = tokens[header_content_token_index].content
                        slug = self._generate_slug(header_content)
                        anchors.add(slug)
        except Exception:
            # If we can't read/parse, assume no anchors (file error will be caught elsewhere)
            pass

        self._file_anchors_cache[file_path] = anchors
        return anchors

    def _process_link_token(self, link_token: Token, parent_token: Token, current_file_path: Path, file_node: FileNode, nodes: List[BaseNode], edges: List[BaseEdge], content_lines: List[str], link_index: int):
        """Helper function to process link_open tokens and create REFERENCES edges or ParsingErrorNodes."""
        href = None
        if link_token.attrs:
            href = link_token.attrs.get("href")
        
        # Use parent_token map if child token map is missing (common for inline tokens)
        map_info = link_token.map or parent_token.map
        line_number = map_info[0] + 1 if map_info else 0
        raw_snippet = content_lines[map_info[0]] if map_info and map_info[0] < len(content_lines) else ""
        
        if href:
            # Skip validation for external links
            if re.match(r'^(http|https|mailto):', href, re.IGNORECASE):
                return

            try:
                # Handle Anchor
                target_anchor = None
                href_path = href
                if "#" in href:
                    href_path, target_anchor = href.split("#", 1)

                # Normalize the link target path
                # If href_path is empty, it's an internal link (e.g., #section)
                if not href_path:
                    normalized_link_path = current_file_path.relative_to(self.project_root)
                    full_target_path = current_file_path
                else:
                    normalized_link_path = normalize_path_to_project_root(current_file_path, href_path, project_root=self.project_root)
                    full_target_path = self.project_root / normalized_link_path
                
                # VALIDATION 1: Check if target file exists
                if not full_target_path.exists():
                     # Treat as broken link -> Parsing Error
                    error_node = ParsingErrorNode(
                        id=f"{file_node.id}#link-error-line-{line_number}-{link_index}",
                        file_path=file_node.path,
                        line_number=line_number,
                        error_message=f"Dangling Reference: Target file '{href_path}' does not exist.",
                        raw_content_snippet=raw_snippet
                    )
                    nodes.append(error_node)
                    return

                # VALIDATION 2: Check if anchor exists (if applicable)
                if target_anchor:
                    # We need to check if this anchor exists in the target file
                    # Note: For the *current* file, we might be parsing it right now.
                    # Ideally we should do a 2-pass or post-validation for current file, 
                    # but _get_anchors_for_file reads from disk.
                    # If we are linting, the file on disk is likely the one we are parsing (unless dirty buffer).
                    # Assuming disk content is source of truth for now.
                    
                    target_anchors = self._get_anchors_for_file(full_target_path)
                    if target_anchor not in target_anchors:
                        error_node = ParsingErrorNode(
                            id=f"{file_node.id}#anchor-error-line-{line_number}-{link_index}",
                            file_path=file_node.path,
                            line_number=line_number,
                            error_message=f"Dangling Reference: Anchor '#{target_anchor}' not found in '{href_path or current_file_path.name}'.",
                            raw_content_snippet=raw_snippet
                        )
                        nodes.append(error_node)
                        return

                # Create a REFERENCES edge
                # Ensure unique ID by appending index
                # Include anchor in the edge target ID if present
                target_id = str(normalized_link_path)
                if target_anchor:
                    target_id = f"{target_id}#{target_anchor}"

                edge_id = f"{file_node.id}-REFERENCES-{target_id}-{link_index}"
                
                edges.append(BaseEdge(
                    id=edge_id,
                    edge_type="references",
                    source=file_node.id,
                    target=target_id
                ))
            except ValueError as e:
                # Handle cases where link target cannot be normalized (e.g., external links, invalid paths)
                error_node = ParsingErrorNode(
                    id=f"{file_node.id}#link-error-line-{line_number}-{link_index}",
                    file_path=file_node.path,
                    line_number=line_number,
                    error_message=f"Malformed or unresolvable link target: {href}. Error: {e}",
                    raw_content_snippet=raw_snippet
                )
                nodes.append(error_node)

    def parse(self, file_path: Path, content: str = None) -> Tuple[List[BaseNode], List[BaseEdge]]:
        """
        Parses a Markdown file and converts its content into a list of BaseNodes and BaseEdges.

        Args:
            file_path (Path): The path to the Markdown file.
            content (str, optional): The content of the file. If None, reads from file_path.

        Returns:
            Tuple[List[BaseNode], List[BaseEdge]]: A tuple containing lists of graph nodes and edges.
        """
        if content is None:
            if not file_path.is_file():
                raise FileNotFoundError(f"Markdown file not found: {file_path}")
            content = file_path.read_text()
            # Prime the anchor cache for this file since we have the content
            # (In case we self-reference later, though we read from disk in _get_anchors usually)
            # Actually, to be safe for self-references during this parse, 
            # we might want to pre-scan anchors here if we wanted to avoid reading disk twice.
            # But kept simple for now relying on _get_anchors_for_file reading disk.

        if file_path.is_absolute():
            try:
                normalized_file_path = file_path.relative_to(self.project_root)
            except ValueError:
                # Fallback if not relative to project root (e.g. symlinks or external)
                # But for our use case, we assume it's in the project
                normalized_file_path = file_path 
        else:
            normalized_file_path = file_path

        tokens = self.md.parse(content)

        nodes: List[BaseNode] = []
        edges: List[BaseEdge] = []

        # 1. Create a FileNode for the markdown file itself
        file_node = FileNode(id=str(normalized_file_path), path=normalized_file_path, content=content)
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
                
                slug = self._generate_slug(header_content)
                
                header_id = f"{normalized_file_path}#{slug}"

                new_header_node = HeaderNode(
                    id=header_id,
                    path=normalized_file_path,
                    level=level,
                    content=header_content
                )
                nodes.append(new_header_node)

                # Define CONTAINS relationship: File -> Header
                edges.append(BaseEdge(
                    id=f"{file_node.id}-CONTAINS-{new_header_node.id}",
                    edge_type="contains",
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
                        edge_type="parent_of",
                        source=parent_header.id,
                        target=new_header_node.id
                    ))
                header_stack.append(new_header_node)

            elif token.type == "inline": # Process inline tokens to find nested links and implicit references
                # --- CONTENT CAPTURE START ---
                if header_stack:
                    current_header = header_stack[-1]
                    # Heuristic: If the PREVIOUS token was heading_open, this inline is the title.
                    # We want to skip appending the title again to the body content.
                    is_header_title = (i > 0 and tokens[i-1].type == "heading_open")
                    
                    if not is_header_title and token.content:
                        # Append content to the active header
                        current_header.content += "\n" + token.content
                # --- CONTENT CAPTURE END ---

                # Process children of inline token
                if token.children:
                    for child_token in token.children:
                        if child_token.type == "link_open":
                            link_counter += 1
                            self._process_link_token(child_token, token, file_path, file_node, nodes, edges, content_lines, link_counter)
                        elif child_token.type == "text" or child_token.type == "code_inline":
                            # Apply implicit link detection only to plain text or inline code
                            if child_token.content:
                                implicit_link_pattern = r"[\w\-/]+\.(md|yaml)"
                                for match in re.finditer(implicit_link_pattern, child_token.content):
                                    implicit_path = match.group(0)
                                    try:
                                        resolved_implicit_file = (file_path.parent / implicit_path).resolve()
                                        if resolved_implicit_file.is_file():
                                            normalized_implicit_path = normalize_path_to_project_root(file_path, str(resolved_implicit_file), project_root=self.project_root)
                                            link_counter += 1
                                            edges.append(BaseEdge(
                                                id=f"{file_node.id}-REFERENCES-{normalized_implicit_path}-{link_counter}",
                                                edge_type="references",
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
                                normalized_implicit_path = normalize_path_to_project_root(file_path, str(resolved_implicit_file), project_root=self.project_root)
                                link_counter += 1
                                edges.append(BaseEdge(
                                    id=f"{file_node.id}-REFERENCES-{normalized_implicit_path}-{link_counter}",
                                    edge_type="references",
                                    source=file_node.id,
                                    target=str(normalized_implicit_path)
                                ))
                        except ValueError:
                            pass # Ignore errors for implicit links that don't resolve to project files

            # Capture Code Blocks and Fenced Code
            elif (token.type == "fence" or token.type == "code_block") and header_stack:
                 if token.content:
                     header_stack[-1].content += f"\n```\n{token.content}```\n"

            # Associate content with the current active header
            elif header_stack:
                 # Check if the token represents content (paragraph, list, code block, etc.)
                 pass # Placeholder until we implement robust content extraction


        return nodes, edges