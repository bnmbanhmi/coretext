from pydantic import BaseModel, Field
from pathlib import Path
import yaml

class SystemConfig(BaseModel):
    memory_limit_mb: int = Field(default=50, description="Soft memory limit for the daemon in MB")
    background_priority: bool = Field(default=True, description="Whether to run background operations at lowest priority")

class Config(BaseModel):
    daemon_port: int = 8000
    mcp_port: int = 8001
    log_level: str = "INFO"
    surreal_url: str = "ws://localhost:8000/rpc"
    surreal_ns: str = "coretext"
    surreal_db: str = "coretext"
    system: SystemConfig = Field(default_factory=SystemConfig)

def load_config(project_root: Path | None = None) -> Config:
    if project_root is None:
        project_root = Path.cwd()
        
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
system:
  memory_limit_mb: 50
  background_priority: true
"""