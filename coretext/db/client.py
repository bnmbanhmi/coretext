# coretext/db/client.py

import platform
import asyncio
import os
import aiohttp
from pathlib import Path

class SurrealDBClient:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.bin_dir = Path.home() / ".coretext" / "bin"
        self.db_path = project_root / ".coretext" / "surreal.db"
        self.surreal_path = self.bin_dir / self._get_surreal_binary_name()
        self.process = None

    def _get_surreal_binary_name(self) -> str:
        # Determine the platform and architecture
        os_name = platform.system().lower()
        arch_name = platform.machine().lower()

        if "linux" in os_name:
            if "x86_64" in arch_name:
                return "surreal-x86_64-unknown-linux-gnu"
            elif "aarch64" in arch_name:
                return "surreal-aarch64-unknown-linux-gnu"
        elif "darwin" in os_name: # macOS
            if "x86_64" in arch_name:
                return "surreal-x86_64-apple-darwin"
            elif "arm64" in arch_name:
                return "surreal-aarch64-apple-darwin"
        elif "windows" in os_name:
            if "amd64" in arch_name:
                return "surreal-x86_64-pc-windows-msvc.exe"
        
        raise RuntimeError(f"Unsupported OS/architecture: {os_name}/{arch_name}")

    async def download_surreal_binary(self, version: str = "1.4.1"):
        binary_name = self._get_surreal_binary_name()
        url = f"https://github.com/surrealdb/surrealdb/releases/download/v{version}/{binary_name}"
        
        if self.surreal_path.exists():
            return

        self.bin_dir.mkdir(parents=True, exist_ok=True)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise RuntimeError(f"Failed to download SurrealDB binary from {url}: {response.status}")
                
                content = await response.read()
                self.surreal_path.write_bytes(content)
                os.chmod(self.surreal_path, 0o755)

    async def start_surreal_db(self):
        if not self.surreal_path.exists():
            raise RuntimeError("SurrealDB binary not found. Run 'coretext init' first.")
        
        if self.process and self.process.returncode is None:
            return # Already running

        # Create .coretext directory if it doesn't exist (for the DB file)
        self.db_path.parent.mkdir(exist_ok=True)

        args = [
            str(self.surreal_path),
            "start",
            "--log", "trace",
            "--user", "root",
            "--pass", "root",
            f"file:{self.db_path}"
        ]

        self.process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

    async def stop_surreal_db(self):
        if self.process and self.process.returncode is None:
            self.process.terminate()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self.process.kill()
                await self.process.wait()
            self.process = None
