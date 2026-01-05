import pytest
import subprocess
import time
import socket
import os
from typing import Generator

@pytest.fixture(scope="session")
def daemon_process() -> Generator[int, None, None]:
    """
    Starts the coretext daemon on a test port.
    Returns the port number.
    """
    port = 8001
    # Check if port is already in use
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('127.0.0.1', port)) == 0:
            # Port in use, find another one
            port = 8002
            
    # Start the daemon
    # Note: This assumes the package is installed or PYTHONPATH is set
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    
    process = subprocess.Popen(
        ["uvicorn", "coretext.server.app:app", "--host", "127.0.0.1", "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )
    
    # Wait for server to be ready
    start_time = time.time()
    timeout = 5
    ready = False
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                ready = True
                break
        except (socket.error, ConnectionRefusedError):
            time.sleep(0.1)
    
    if not ready:
        process.terminate()
        stdout, stderr = process.communicate()
        pytest.fail(f"Daemon failed to start within timeout. Stdout: {stdout.decode()}, Stderr: {stderr.decode()}")
        
    yield port
    
    # Teardown
    process.terminate()
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        process.kill()
