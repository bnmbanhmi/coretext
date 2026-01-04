from pydantic import BaseModel
from pathlib import Path
import yaml

class Config(BaseModel):
    daemon_port: int = 8000
    mcp_port: int = 8001
    log_level: str = "INFO"
    surreal_url: str = "ws://localhost:8000/rpc"
    surreal_ns: str = "coretext"
    surreal_db: str = "coretext"

def load_config(project_root: Path) -> Config:
    config_path = project_root / ".coretext" / "config.yaml"
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                data = yaml.safe_load(f)
                return Config(**data)
        except Exception:
            # Fallback to defaults if parsing fails
            pass
    return Config()

DEFAULT_CONFIG_CONTENT = """# CoreText Configuration
daemon_port: 8000
mcp_port: 8001
log_level: INFO
"""
