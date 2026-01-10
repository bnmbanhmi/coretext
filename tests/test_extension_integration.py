import json
import tomllib
from pathlib import Path
import pytest

def test_extension_manifest_structure():
    """Verify gemini-extension.json contains the required MCP configuration."""
    manifest_path = Path("gemini-extension.json")
    
    if not manifest_path.exists():
        pytest.skip("gemini-extension.json not created yet")
    
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
        
    # Check for mcpServers section
    assert "mcpServers" in manifest, "Manifest missing 'mcpServers' section"
    
    # Check for coretext server definition
    assert "coretext" in manifest["mcpServers"], "Manifest missing 'coretext' server definition"
    server_config = manifest["mcpServers"]["coretext"]
    assert "adapter" in server_config["args"], "MCP Server should use 'adapter' command"

def test_custom_commands_definition():
    """Verify commands/coretext.toml exists and is valid."""
    commands_path = Path("commands/coretext.toml")
    
    if not commands_path.exists():
        pytest.skip("commands/coretext.toml not created yet")
        
    with open(commands_path, "rb") as f:
        data = tomllib.load(f)
        
    assert "commands" in data, "TOML missing 'commands' section"
    assert len(data["commands"]) >= 11, "Missing some commands (expected at least 11)"
    
    command_names = [c["name"] for c in data["commands"]]
    expected_commands = [
        "status", "init", "start", "stop", "lint", 
        "sync", "apply-schema", "new", "install-hooks", 
        "inspect", "ping"
    ]
    
    for cmd in expected_commands:
        assert cmd in command_names, f"Missing command: {cmd}"
        
        # Verify cwd is set correctly for each command
        cmd_def = next(c for c in data["commands"] if c["name"] == cmd)
        assert "${extensionPath}" in cmd_def["cwd"], f"Command {cmd} missing ${{extensionPath}} in cwd"