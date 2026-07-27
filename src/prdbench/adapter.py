"""PRDBench agent adapter — wraps penguin-coding's agent_loop for PRDBench evaluation.

This adapter:
1. Loads PRDBench-specific tools (judge, interactive shell, etc.) alongside penguin's core tools
2. Constructs system prompts matching PRDBench's expected agent behavior
3. Runs the agent loop in a headless mode (no interactive CLI, no permission prompts)
4. Returns results in the format PRDBench's evaluation client expects
"""

import json
import logging
import os
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Activate PRDBench mode — relaxes path restrictions for benchmark access
os.environ["PRDBENCH_MODE"] = "true"

from anthropic import Anthropic

from .._constants import ALLOWED_BASE_DIR, client, eval_client, EVAL_MODEL_ID, MODEL_ID
from ..agent_loop import agent_loop, stream_response
from ..compact import estimate_messages_tokens
from ..execution_log import ExecutionLog
from ..tools import (
    TOOL_DEFINITIONS as BASE_TOOL_DEFINITIONS,
    dispatcher as base_dispatcher,
)
from ..tools.dispatcher import ToolDispatcher
from ..tool_registry import ToolRegistry
from ..permissions import PermissionManager
from ..permissions_config import load_permissions_config
from .config import (
    APP_NAME,
    MAX_ITERATIONS,
    MAX_OUTPUT_TOKENS,
    WORKSPACE_DIR,
    MODEL_NAME,
    MAX_SESSION_TIME,
)
from .prompts import DEVELOPMENT_PROMPT, DEBUG_PROMPT, EVALUATION_PROMPT

logger = logging.getLogger("penguin.prdbench.adapter")

# ── Import PRDBench tools to trigger @register_tool ──
from . import tools as _prdbench_tools  # noqa: F401


# ── System Prompt for PRDBench Evaluation Agent ──

EVAL_SYSTEM_PROMPT = """You are an interactive CLI agent specializing in software quality assurance (QA) automation. Your primary goal is to rigorously, safely, and efficiently evaluate the implementation of a codebase against a provided evaluation plan, utilizing your available tools.

# Core Mandates

- **Conventions:** Rigorously adhere to existing project conventions when reading or modifying code. Analyze surrounding code, tests, and configuration first.
- **Libraries/Frameworks:** NEVER assume a library/framework is available or appropriate. Verify its established usage within the project before employing it.
- **Path Construction:** Before using any file system tool, you must construct the full absolute path for the file_path argument. Always combine the absolute path of the project's root directory with the file's path relative to the root.
- **No Code Modification:** Never modify the codebase, test plan, or any files unless explicitly instructed.
- **Structured Reporting:** For each test, output a structured JSON report with all required fields and no extra commentary unless requested.
- **Ambiguity Handling:** If any test case is unclear or cannot be executed as written, halt and request clarification rather than making assumptions.
- **Isolation:** Run each test in a clean, isolated directory. Reset files, databases, or state as needed before each test.
- **Test Plan Fidelity:** Execute every test case in the test plan exactly as described. Do not invent, modify, or skip any test cases.

# Primary Workflows
## Basic Evaluation
When requested to evaluate code functionality according to the metrics in the test plan, first use `run_command` to switch working directory to the project root directory, i.e., `cd /path/to/project/`.
Then, analyze and execute each test case one by one, strictly following the workflow below for every single test case. Every test case must go through the following six steps:
1. **Understand:** Carefully examine each metric object in the test plan. For every test case, fully understand its `metric`, `description`, `type`, `test_command`, `test_input`, `input_files`, `expected_output_files`, and `expected_output`.
2. **Prepare:** Ensure all `input_files` and `test_input` are present and correctly formatted.
3. **Execute:**
   - For `shell_interaction` type test case, use `judge` to simulate user interaction and record the entire interaction process.
   - For `unit_test` type test case, use `run_command` to execute the test command.
   - For `file_comparison` type test case, use `run_command` to execute the file-generation command.
4. **Verify:** Compare the observed output against the expected output as described in the test plan.
5. **Report:** Generate a structured JSON report with all required fields (metric, description, score, and explanation). `metric` and `description` are from the test plan, `score` is a number of 0, 1, or 2, and `explanation` is a concise explanation justifying the assigned score.
6. **Ambiguity Handling:** If any step cannot be performed as described, halt and request clarification.

After all test cases are executed, output a summary JSON array containing the report for all test cases in order, and write it to the specified report file.

# Tools Available
You have access to these tools:
- `read_file`: Read file contents by path
- `write_file`: Write content to a file
- `edit_file`: Edit an existing file
- `list_directory`: List directory contents
- `list_workspace`: List all files in a workspace directory recursively
- `run_command`: Run a shell command
- `judge`: Simulate user interaction with a program (for shell_interaction tests)
- `start_interactive_shell`: Start an interactive shell session
- `run_interactive_shell`: Send input to an interactive shell session
- `kill_shell_session`: Terminate a shell session
- `search_files`: Search for patterns in files
- `exit_loop`: Signal that you have finished all tasks

# Operational Guidelines
- Always use absolute paths when referring to files.
- For standard, non-interactive commands, prefer `run_command`. For interactive sessions, use `start_interactive_shell` + `run_interactive_shell`.
- Use `judge` for simulating user interaction in shell_interaction test cases.
- Call `exit_loop` when you finish the evaluation.
- When writing to a file, the content must be a string format.
"""


# ── System Prompt for PRDBench Development Agent ──

DEV_SYSTEM_PROMPT = f"""You are an expert Python developer. Your task is to implement a complete Python project according to the given PRD (Product Requirements Document) and test plan.

# Rules
1. **Write ALL source files under the project's src/ directory** using absolute paths.
2. **Use absolute paths for all file operations.**
3. **Do NOT ask questions.** Complete the entire project and submit directly.

# Implementation Strategy
1. Read PRD.md and detailed_test_plan.json to understand requirements.
2. Plan the file structure.
3. Write source files one by one using write_file.
4. Run tests with run_command to verify.
5. Fix any issues with edit_file.
6. Call exit_loop when done.

# Tools Available
- `write_file`: Write content to a file
- `edit_file`: Edit an existing file (use for fixes)
- `read_file`: Read file contents
- `run_command`: Run a shell command (for testing)
- `list_directory`: List directory contents
- `list_workspace`: List all files in a workspace directory
- `search_files`: Search for patterns in files
- `exit_loop`: Signal that you have finished all tasks

Working directory: {{workspace_dir}}
"""


# ── Session Management ──

class PRDBenchSession:
    """Manages a single agent evaluation/development session."""

    def __init__(self, session_id: str, user_id: str, app_name: str):
        self.session_id = session_id
        self.user_id = user_id
        self.app_name = app_name
        self.created_at = datetime.now()
        self.messages: list[dict[str, Any]] = []
        self.last_activity = datetime.now()

    def is_expired(self) -> bool:
        elapsed = (datetime.now() - self.last_activity).total_seconds()
        return elapsed > MAX_SESSION_TIME

    def touch(self):
        self.last_activity = datetime.now()


class SessionManager:
    """Thread-safe session manager for PRDBench agent."""

    def __init__(self):
        self._sessions: dict[str, PRDBenchSession] = {}
        self._lock = threading.Lock()

    def create(self, session_id: str, user_id: str, app_name: str) -> PRDBenchSession:
        import threading
        with self._lock:
            session = PRDBenchSession(session_id, user_id, app_name)
            self._sessions[session_id] = session
            logger.info(f"Created session: {session_id}")
            return session

    def get(self, session_id: str) -> Optional[PRDBenchSession]:
        with self._lock:
            return self._sessions.get(session_id)

    def delete(self, session_id: str) -> bool:
        with self._lock:
            removed = self._sessions.pop(session_id, None)
            if removed:
                logger.info(f"Deleted session: {session_id}")
            return removed is not None


# Global session manager
session_manager = SessionManager()


# ── Build tool definitions for PRDBench mode ──

def _build_prdbench_dispatcher() -> ToolDispatcher:
    """Create a dispatcher with both penguin core tools and PRDBench-specific tools."""
    disp = ToolDispatcher()

    # Register core tools
    for name in ToolRegistry.all_names():
        inst = ToolRegistry.create_instance(name)
        if inst and inst.name not in (
            # Skip team tools — not needed for PRDBench
            "team_spawn", "team_list", "team_shutdown",
            "team_send", "team_broadcast",
            # Skip delegate — not needed for PRDBench
            "delegate",
            # Skip task/skill tools — not needed for PRDBench
            "task", "load_skill",
        ):
            disp.register(inst)

    # Initialize permission manager in permissive mode
    config = load_permissions_config()
    config["profile"] = "permissive"
    perm = PermissionManager(config)
    perm.set_registry(disp._registry)
    disp.set_permission_manager(perm)

    return disp


def _build_prdbench_tool_definitions() -> list[dict]:
    """Build the tool definitions list for PRDBench LLM calls."""
    disp = _build_prdbench_dispatcher()
    return disp.get_tool_definitions()


# ── Agent Runner ──

def run_prdbench_agent(
    user_message: str,
    session: PRDBenchSession,
    mode: str = "eval",
    max_iterations: int = MAX_ITERATIONS,
    log_file: str | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Run penguin-coding's agent loop in headless PRDBench mode.

    Args:
        user_message: The prompt to send to the agent.
        session: The PRDBenchSession tracking this conversation.
        mode: One of "dev", "debug", "eval" — selects the system prompt.
        max_iterations: Maximum agent loop iterations.

    Returns:
        Dict with response content and metadata.
    """
    import threading

    # Select system prompt based on mode
    workspace_dir = WORKSPACE_DIR
    if mode == "dev":
        system_prompt = DEV_SYSTEM_PROMPT.format(workspace_dir=workspace_dir)
    elif mode == "debug":
        system_prompt = DEV_SYSTEM_PROMPT.format(workspace_dir=workspace_dir)
    else:
        system_prompt = EVAL_SYSTEM_PROMPT

    # EVAL 模式用独立模型解耦 DEV/EVAL 系统性偏差
    if mode == "eval":
        if not EVAL_MODEL_ID:
            logger.warning(
                "EVAL_MODEL_ID not set in .env; falling back to main MODEL_ID. "
                "DEV/EVAL systematic bias cannot be decoupled in this run."
            )
        run_client = eval_client
        run_model_id = EVAL_MODEL_ID or MODEL_ID
    else:
        run_client = client
        run_model_id = MODEL_ID

    # Build dispatcher and tool definitions for this run
    disp = _build_prdbench_dispatcher()
    tools = disp.get_tool_definitions()

    exec_log = ExecutionLog(path=log_file, enabled=bool(log_file), run_id=run_id) if log_file else None

    def _on_content(text: str) -> None:
        if exec_log:
            exec_log.log_llm_text(text)

    def _on_tool_start(name: str, kwargs: dict) -> None:
        if exec_log:
            exec_log.log_tool_start(name, kwargs)

    def _on_tool_result(name: str, result: str) -> None:
        if exec_log:
            exec_log.log_tool_result(name, result)

    if exec_log:
        exec_log.log_run_started(case_id=session.session_id, workspace_dir=workspace_dir)

    session.touch()

    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            # Run agent_loop headlessly — skip all permission checks
            content, messages = agent_loop(
                client=run_client,
                user_message=user_message,
                max_iterations=max_iterations,
                messages=session.messages,
                system_prompt=system_prompt,
                tools=tools,
                tool_dispatcher=disp,
                confirm_callback=lambda name, args, reason: True,  # auto-approve all
                on_content=_on_content,
                on_tool_start=_on_tool_start,
                on_tool_result=_on_tool_result,
                model_id=run_model_id,
            )

            # Update session messages for continuation
            session.messages = messages
            session.touch()

            if exec_log:
                exec_log.log_run_finished(
                    turn_count=len(messages) // 2,
                    tool_call_count=exec_log.tool_call_count,
                    exit_code=0,
                )

            return {
                "status": "success",
                "content": content,
                "session_id": session.session_id,
                "timestamp": datetime.now().isoformat(),
            }

        except (TimeoutError, OSError) as e:
            if attempt < max_retries:
                logger.warning(f"Agent loop timeout (attempt {attempt + 1}/{max_retries + 1}), retrying...")
                import time
                time.sleep(5)
                continue
            if exec_log:
                exec_log.log_run_terminated(reason=f"{type(e).__name__}: {e}")
            logger.error(f"Agent loop error after {max_retries + 1} attempts: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "session_id": session.session_id,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            if exec_log:
                exec_log.log_run_terminated(reason=f"{type(e).__name__}: {e}")
            logger.error(f"Agent loop error: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "session_id": session.session_id,
                "timestamp": datetime.now().isoformat(),
            }

    if exec_log:
        exec_log.log_run_terminated(reason="Max retries exceeded")

    # Should not reach here
    return {
        "status": "error",
        "error": "Max retries exceeded",
        "session_id": session.session_id,
        "timestamp": datetime.now().isoformat(),
    }
