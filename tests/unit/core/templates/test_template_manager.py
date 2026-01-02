import pytest
from unittest.mock import patch, MagicMock
from coretext.core.templates.manager import TemplateManager

def test_list_templates():
    # Mocking importlib.resources.files
    with patch("importlib.resources.files") as mock_files:
        mock_entry1 = MagicMock()
        mock_entry1.is_file.return_value = True
        mock_entry1.name = "prd.md"
        
        mock_entry2 = MagicMock()
        mock_entry2.is_file.return_value = True
        mock_entry2.name = "story.md"
        
        mock_entry3 = MagicMock()
        mock_entry3.is_file.return_value = True
        mock_entry3.name = "__init__.py" # Should be ignored

        mock_files.return_value.iterdir.return_value = [mock_entry1, mock_entry2, mock_entry3]
        
        templates = TemplateManager.list_templates()
        assert "prd" in templates
        assert "story" in templates
        assert "__init__" not in templates
        assert len(templates) == 2

def test_get_template_content_found():
    with patch("importlib.resources.files") as mock_files:
        mock_path = MagicMock()
        mock_path.is_file.return_value = True
        mock_path.read_text.return_value = "# Template Content"
        
        mock_files.return_value.joinpath.return_value = mock_path
        
        content = TemplateManager.get_template_content("prd")
        assert content == "# Template Content"
        mock_files.return_value.joinpath.assert_called_with("prd.md")

def test_get_template_content_not_found():
    with patch("importlib.resources.files") as mock_files:
        mock_path = MagicMock()
        mock_path.is_file.return_value = False # Not found
        
        mock_files.return_value.joinpath.return_value = mock_path
        
        with pytest.raises(FileNotFoundError):
            TemplateManager.get_template_content("nonexistent")
