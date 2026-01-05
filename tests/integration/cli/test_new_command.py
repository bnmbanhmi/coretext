from typer.testing import CliRunner
from coretext.cli.commands import app

runner = CliRunner()

def test_new_command_list():
    result = runner.invoke(app, ["new", "--list"])
    assert result.exit_code == 0
    assert "Template Name" in result.stdout
    assert "prd" in result.stdout
    assert "story" in result.stdout
    assert "epic" in result.stdout
    assert "architecture" in result.stdout

def test_new_command_create_file(tmp_path):
    output_file = tmp_path / "test_story.md"
    result = runner.invoke(app, ["new", "story", str(output_file)])
    
    assert result.exit_code == 0
    assert "Successfully created" in result.stdout
    assert output_file.exists()
    content = output_file.read_text()
    assert "# Story {{story_id}}: {{story_title}}" in content

def test_new_command_overwrite_protection(tmp_path):
    output_file = tmp_path / "test_existing.md"
    output_file.write_text("Old content")
    
    # Simulate user saying "n" (no)
    result = runner.invoke(app, ["new", "story", str(output_file)], input="n\n")
    
    assert result.exit_code == 0 # Exit code 0 because it's a clean cancellation
    assert "File" in result.stdout and "already exists" in result.stdout
    assert "Operation cancelled" in result.stdout
    assert output_file.read_text() == "Old content"

def test_new_command_interactive_overwrite_yes(tmp_path):
    output_file = tmp_path / "test_overwrite_interactive.md"
    output_file.write_text("Old content")
    
    # Simulate user saying "y" (yes)
    result = runner.invoke(app, ["new", "story", str(output_file)], input="y\n")
    
    assert result.exit_code == 0
    assert "Successfully created" in result.stdout
    content = output_file.read_text()
    assert "# Story {{story_id}}: {{story_title}}" in content

def test_new_command_invalid_name_error():
    result = runner.invoke(app, ["new", "../bad", "out.md"])
    assert result.exit_code == 1
    assert "Template name must contain only letters" in result.stdout

def test_new_command_invalid_template():
    result = runner.invoke(app, ["new", "invalid_template", "out.md"])
    assert result.exit_code == 1
    assert "Template 'invalid_template' not found" in result.stdout
