# coretext/db/client.py

import platform
import asyncio
import os
import aiohttp
import tarfile
import zipfile
import shutil
import subprocess
from pathlib import Path
from io import BytesIO

class SurrealDBClient:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.bin_dir = Path.home() / ".coretext" / "bin"
        self.db_path = project_root / ".coretext" / "surreal.db"
        self.pid_file = project_root / ".coretext" / "daemon.pid"
        self.surreal_path = self.bin_dir / ("surreal.exe" if platform.system().lower() == "windows" else "surreal")
        self.process = None

    def _get_platform_info(self) -> tuple[str, str, str]:
        """Returns (os_name, arch_name, extension)"""
        system = platform.system().lower()
        machine = platform.machine().lower()

        if system == "linux":
            ext = "tar.gz"
            if machine == "x86_64":
                return "linux", "amd64", ext
            elif machine == "aarch64":
                return "linux", "arm64", ext
        elif system == "darwin":
            ext = "tar.gz"
            if machine == "x86_64":
                return "darwin", "amd64", ext
            elif machine == "arm64":
                return "darwin", "arm64", ext
        elif system == "windows":
            ext = "zip"
            if machine == "amd64" or machine == "x86_64":
                return "windows", "amd64", ext
        
        raise RuntimeError(f"Unsupported platform: {system} {machine}")

    async def download_surreal_binary(self, version: str = "1.4.1"):
        os_name, arch_name, ext = self._get_platform_info()
        filename = f"surreal-v{version}-{os_name}-{arch_name}.{ext}"
        url = f"https://github.com/surrealdb/surrealdb/releases/download/v{version}/{filename}"
        
        if self.surreal_path.exists():
            # Check if executable
            if not os.access(self.surreal_path, os.X_OK):
                os.chmod(self.surreal_path, 0o755)
            return

        self.bin_dir.mkdir(parents=True, exist_ok=True)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise RuntimeError(f"Failed to download SurrealDB binary from {url}: {response.status}")
                
                content = await response.read()
                
                # Extract logic
                if ext == "tar.gz":
                    with tarfile.open(fileobj=BytesIO(content), mode="r:gz") as tar:
                        # Find the 'surreal' binary in the archive
                        member = None
                        for m in tar.getmembers():
                            if m.name.endswith("surreal") or m.name.endswith("surreal.exe"):
                                member = m
                                break
                        if not member:
                            raise RuntimeError(f"Could not find 'surreal' binary in archive {filename}")
                        
                        f = tar.extractfile(member)
                        if f:
                            self.surreal_path.write_bytes(f.read())
                elif ext == "zip":
                    with zipfile.ZipFile(BytesIO(content)) as zf:
                        # Find the 'surreal.exe' binary
                        member_name = None
                        for name in zf.namelist():
                            if name.endswith("surreal.exe"):
                                member_name = name
                                break
                        if not member_name:
                            raise RuntimeError(f"Could not find 'surreal.exe' binary in archive {filename}")
                        
                        self.surreal_path.write_bytes(zf.read(member_name))
                
                if not self.surreal_path.exists():
                     raise RuntimeError(f"Failed to extract surreal binary to {self.surreal_path}")

                os.chmod(self.surreal_path, 0o755)

    def start_detached(self, port: int = 8000):
        """Starts SurrealDB as a detached process."""
        if not self.surreal_path.exists():
            raise RuntimeError("SurrealDB binary not found. Run 'coretext init' first.")
        
        # Note: We don't check is_running() here because the caller might handle logic differently
        # or we might want to start even if we think it's running (stale pid handling by caller).
        # But generally caller should check.

        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        args = [
            str(self.surreal_path),
            "start",
            "--log", "trace",
            "--user", "root",
            "--pass", "root",
            f"rocksdb:{self.db_path}",
            "--bind", f"127.0.0.1:{port}",
            "--unauthenticated"
        ]

        # Use start_new_session=True to detach from terminal
        process = subprocess.Popen(
            args,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        if process.pid:
            self.pid_file.parent.mkdir(parents=True, exist_ok=True)
            self.pid_file.write_text(str(process.pid))

    async def start_surreal_db(self, port: int = 8000):
        if not self.surreal_path.exists():
            raise RuntimeError("SurrealDB binary not found. Run 'coretext init' first.")
        
        if await self.is_running():
            return # Already running

        # Create .coretext directory if it doesn't exist (for the DB file)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        args = [
            str(self.surreal_path),
            "start",
            "--log", "trace",
            "--user", "root",
            "--pass", "root",
            f"rocksdb:{self.db_path}",
            "--bind", f"127.0.0.1:{port}",
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
