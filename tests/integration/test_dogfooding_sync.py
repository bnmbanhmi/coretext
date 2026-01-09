import pytest
import asyncio
from pathlib import Path
from surrealdb import AsyncSurreal
from coretext.config import load_config
import subprocess

@pytest.mark.asyncio
async def test_sync_indexes_knowledge_files():
    """Verify that coretext sync indexes files in the knowledge folder."""
    project_root = Path.cwd()
    config = load_config(project_root)
    
    # 1. Run sync using default config (which points to _coretext-knowledge)
    result = subprocess.run(
        ["poetry", "run", "coretext", "sync", "--project-root", str(project_root)],
        capture_output=True,
        text=True
    )
    
    # 2. Check DB for the knowledge file
    async with AsyncSurreal(f"ws://localhost:{config.daemon_port}/rpc") as db:
        await db.connect()
        await db.use(config.surreal_ns, config.surreal_db)
        
        # Query for a file node using string::contains
        target_substring = "_coretext-knowledge/report.md"
        query = "SELECT * FROM node WHERE string::contains(path, $sub)"
        result = await db.query(query, {"sub": target_substring})
        
        found = False
        items = []
        if isinstance(result, list) and len(result) > 0:
            first = result[0]
            if isinstance(first, dict) and first.get('status') == 'OK':
                items = first.get('result', [])
            elif isinstance(first, list):
                items = first
            else:
                items = result # Flat list
        
        if items:
            found = True
        
        assert found, f"Knowledge file matching {target_substring} was not found in the graph."

@pytest.mark.asyncio
async def test_sync_indexes_archived_files():
    """Verify that coretext sync indexes .md files in knowledge subfolders."""
    project_root = Path.cwd()
    config = load_config(project_root)
    
    async with AsyncSurreal(f"ws://localhost:{config.daemon_port}/rpc") as db:
        await db.connect()
        await db.use(config.surreal_ns, config.surreal_db)
        
        target_substring = "_coretext-knowledge/archive/atdd-checklist-epic-2.md"
        query = "SELECT * FROM node WHERE string::contains(path, $sub)"
        result = await db.query(query, {"sub": target_substring})
        
        found = False
        items = []
        if isinstance(result, list) and len(result) > 0:
            first = result[0]
            if isinstance(first, dict) and first.get('status') == 'OK':
                items = first.get('result', [])
            elif isinstance(first, list):
                items = first
            else:
                items = result # Flat list
        
        if items:
            found = True
            
        assert found, f"Knowledge file matching {target_substring} was not found in the graph."