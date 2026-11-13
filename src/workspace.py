"""Process-wide workspace configuration; set the environment before importing src."""
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")
WORKSPACE_DIR = Path(
    os.getenv("CODE_AGENT_WORKSPACE_DIR") or PROJECT_ROOT / "workspace"
).expanduser().resolve()
