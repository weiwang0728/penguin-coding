"""PRDBench adapter configuration."""

import os
from pathlib import Path


# ── Server ──
DEFAULT_PORT = int(os.getenv("PRDBENCH_PORT", "5678"))
DEFAULT_HOST = os.getenv("PRDBENCH_HOST", "0.0.0.0")

# ── App name (must match PRDBench's generate_code_FD.py appName) ──
APP_NAME = "code_eval_agent"

# ── MCP server ports (used by PRDBench's start_adk_server.sh) ──
PYTHON_INTERPRETER_PORT = os.getenv("PYTHON_INTERPRETER_PORT", "9001")
FILE_OPERATIONS_PORT = os.getenv("FILE_OPERATIONS_PORT", "8002")
SYSTEM_OPERATIONS_PORT = os.getenv("SYSTEM_OPERATIONS_PORT", "8003")

# ── Workspace ──
# PRDBench sets CODE_AGENT_WORKSPACE_DIR; fall back to penguin's workspace
WORKSPACE_DIR = os.getenv(
    "CODE_AGENT_WORKSPACE_DIR",
    str(Path(__file__).resolve().parent.parent / "workspace"),
)
if not os.path.isabs(WORKSPACE_DIR):
    WORKSPACE_DIR = os.path.abspath(WORKSPACE_DIR)

# ── Agent parameters ──
MAX_ITERATIONS = int(os.getenv("PRDBENCH_MAX_ITERATIONS", "100"))
MAX_OUTPUT_TOKENS = int(os.getenv("PRDBENCH_MAX_OUTPUT_TOKENS", "16384"))
ESCALATED_MAX_TOKENS = 65536

# ── Model ──
# Uses penguin-coding's existing .env MODEL_ID / API_KEY / BASE_URL
MODEL_NAME = os.getenv("PRDBENCH_MODEL_NAME", "penguin")

# ── Security ──
ALLOWED_EXTENSIONS = [
    ".py", ".txt", ".md", ".json", ".yaml", ".yml",
    ".csv", ".sql", ".in", ".jsonl",
]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
SANDBOX_MODE = True
SAFE_COMMANDS = [
    "ls", "pwd", "echo", "cat", "head", "tail", "grep", "find",
    "python", "python3", "chmod", "cd", "pytest", "pip", "mkdir",
]

# ── Session ──
MAX_SESSION_TIME = int(os.getenv("MAX_SESSION_TIME", "600"))

# ── Report paths ──
REPORTS_DIR_NAME = "reports"
