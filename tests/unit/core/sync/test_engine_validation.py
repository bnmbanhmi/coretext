import pytest
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock
from coretext.core.sync.engine import SyncEngine, SyncMode, SyncResult
from coretext.core.parser.markdown import MarkdownParser

@pytest.fixture
def parser(tmp_path):
    return MarkdownParser(project_root=tmp_path)

@pytest.fixture
def graph_manager():
    return AsyncMock()

@pytest.mark.asyncio
async def test_sync_engine_validation_valid_links(parser, graph_manager, tmp_path):
    # Setup
    file_a = tmp_path / "file_a.md"
    file_b = tmp_path / "file_b.md"
    file_a.write_text("Link to [File B](./file_b.md)")
    file_b.write_text("# File B")
    
    engine = SyncEngine(parser=parser, graph_manager=graph_manager, project_root=tmp_path)
    
    # Execute
    result = await engine.process_files([str(file_a), str(file_b)], mode=SyncMode.DRY_RUN)
    
    # Verify
    assert result.success
    assert result.error_count == 0

@pytest.mark.asyncio
async def test_sync_engine_validation_broken_links(parser, graph_manager, tmp_path):
    # Setup
    file_a = tmp_path / "file_a.md"
    file_a.write_text("Link to [Non Existent](./non_existent.md)")
    
    engine = SyncEngine(parser=parser, graph_manager=graph_manager, project_root=tmp_path)
    
    # Execute
    result = await engine.process_files([str(file_a)], mode=SyncMode.DRY_RUN)
    
    # Verify
    assert not result.success
    assert result.error_count > 0
    assert any("Dangling Reference" in err for err in result.errors)
    # Check if "Dangling Reference" is expected? The code currently says "Broken link".
    # I should update the code to say "Dangling Reference" to match AC.

@pytest.mark.asyncio
async def test_sync_engine_validation_content_provider(parser, graph_manager, tmp_path):
    # Setup
    file_a = tmp_path / "file_a.md"
    # File doesn't exist on disk with this content, provided via lambda
    file_a.write_text("Original content")
    
    def content_provider(path):
        return "Link to [Non Existent](./non_existent.md)"
    
    engine = SyncEngine(parser=parser, graph_manager=graph_manager, project_root=tmp_path)
    
    # Execute
    result = await engine.process_files([str(file_a)], mode=SyncMode.DRY_RUN, content_provider=content_provider)
    
    # Verify
    assert not result.success
    assert any("Dangling Reference" in err for err in result.errors)
