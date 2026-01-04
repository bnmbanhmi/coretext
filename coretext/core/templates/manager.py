import importlib.resources
from typing import List

class TemplateManager:
    """Manages access to built-in BMAD templates."""

    @staticmethod
    def list_templates() -> List[str]:
        """Lists all available template names (without extension)."""
        templates = []
        # Access the templates package
        # Note: coretext.templates must be a valid package with __init__.py
        files = importlib.resources.files("coretext.templates")
        
        for entry in files.iterdir():
            if entry.is_file() and entry.name.endswith(".md"):
                templates.append(entry.name.replace(".md", ""))
        
        return sorted(templates)

    @staticmethod
    def get_template_content(name: str) -> str:
        """
        Retrieves the content of a specific template.
        
        Args:
            name: The name of the template (e.g., 'prd', 'story').
            
        Returns:
            The content of the template file.
            
        Raises:
            FileNotFoundError: If the template does not exist.
            ValueError: If the template name contains invalid characters.
        """
        import re
        if not re.match(r"^[a-zA-Z0-9_-]+$", name):
             raise ValueError("Template name must contain only letters, numbers, underscores, and hyphens.")

        template_file = importlib.resources.files("coretext.templates").joinpath(f"{name}.md")
        if not template_file.is_file():
             raise FileNotFoundError(f"Template '{name}' not found.")
        return template_file.read_text(encoding="utf-8")
