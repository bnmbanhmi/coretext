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
        self.pid_file = project_root / ".coretext" / "daemon.pid"
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
        
        if await self.is_running():
            return # Already running

        # Create .coretext directory if it doesn't exist (for the DB file)
        self.db_path.parent.mkdir(exist_ok=True)

        args = [
            str(self.surreal_path),
            "start",
            "--log", "trace",
            "--user", "root",
            "--pass", "root",
            f"rocksdb:{self.db_path}",
            "--unauthenticated" # Disable authentication for local development
        ]

        self.process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        if self.process.pid:
            self.pid_file.write_text(str(self.process.pid))

    async def stop_surreal_db(self):
        pid = None
        if self.process and self.process.returncode is None:
            pid = self.process.pid
            self.process.terminate()
        elif self.pid_file.exists():
            try:
                pid = int(self.pid_file.read_text().strip())
                os.kill(pid, 15) # SIGTERM
            except (ValueError, OSError):
                pass # Process might be already gone or file corrupted

        if pid:
            # Simple wait logic, could be more robust
            try:
                # If we have a process object, use it
                if self.process:
                    await asyncio.wait_for(self.process.wait(), timeout=5.0)
                else:
                    # Polling for process exit if we don't have the object
                    for _ in range(50):
                        try:
                            os.kill(pid, 0)
                            await asyncio.sleep(0.1)
                        except OSError:
                            break
            except asyncio.TimeoutError:
                if self.process:
                    self.process.kill()
                    await self.process.wait()
                else:
                    try:
                        os.kill(pid, 9) # SIGKILL
                    except OSError:
                        pass
            
        self.process = None
        if self.pid_file.exists():
            self.pid_file.unlink()

    async def is_running(self) -> bool:
        # Check internal process object
        if self.process and self.process.returncode is None:
            return True
        
        # Check PID file
        if self.pid_file.exists():
            try:
                pid = int(self.pid_file.read_text().strip())
                os.kill(pid, 0) # Check if process exists
                return True
            except (ValueError, OSError):
                # PID file invalid or process dead
                return False
        
        return False
