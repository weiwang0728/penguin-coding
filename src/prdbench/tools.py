"""PRDBench-specific tools: judge (interactive process runner) and shell session management.

These tools replicate the functionality of PRDBench's mcp_tools.py but use
penguin-coding's tool architecture (subclass of Tool, registered via @register_tool).
"""

import json
import logging
import os
import subprocess
import tempfile
import threading
import time
from pathlib import Path
from typing import Optional

from ..tool_registry import register_tool
from ..tools.base import Tool

logger = logging.getLogger("penguin.prdbench")

# ── Shared state for shell sessions ──
_shell_sessions: dict[str, subprocess.Popen] = {}
_session_lock = threading.Lock()
_session_counter = 0
_counter_lock = threading.Lock()


def _next_session_id() -> str:
    global _session_counter
    with _counter_lock:
        _session_counter += 1
        return f"shell_{_session_counter}_{int(time.time())}"


# ── Judge Tool ──

@register_tool
class JudgeTool(Tool):
    """Simulate user interaction with a program and record the full interaction log.

    Starts the program specified by entry_command, feeds lines from input_file
    as user input, and captures the complete terminal output.
    """

    name = "judge"
    description = (
        "Execute a command with simulated user input and return the full "
        "interaction log. Use this for shell_interaction test cases."
    )
    default_permission_level = "allow"
    parameters = {
        "type": "object",
        "properties": {
            "context": {
                "type": "string",
                "description": "Expected output description (what to look for in the output).",
            },
            "entry_command": {
                "type": "string",
                "description": "The command to start the program (e.g. 'python src/main.py').",
            },
            "input_file": {
                "type": "string",
                "description": "Absolute path to a file containing user input lines (one per line).",
            },
            "cwd": {
                "type": "string",
                "description": "Working directory for the command. Defaults to the project root.",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds. Default 60.",
            },
        },
        "required": ["context", "entry_command", "input_file"],
    }

    def execute(self, **kwargs) -> str:
        context = kwargs["context"]
        entry_command = kwargs["entry_command"]
        input_file = kwargs["input_file"]
        cwd = kwargs.get("cwd")
        timeout = kwargs.get("timeout", 60)

        # Read input lines
        try:
            input_path = Path(input_file)
            if not input_path.is_file():
                return f"Error: Input file not found: {input_file}"
            input_lines = input_path.read_text(encoding="utf-8").splitlines()
        except Exception as e:
            return f"Error reading input file: {e}"

        # Build the input string — each line followed by Enter
        input_text = "\n".join(input_lines) + "\n"

        try:
            result = subprocess.run(
                entry_command,
                shell=True,
                input=input_text,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
            )
        except subprocess.TimeoutExpired:
            return json.dumps({
                "status": "timeout",
                "context": context,
                "log": f"Program timed out after {timeout}s",
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "context": context,
                "log": f"Failed to run command: {e}",
            }, ensure_ascii=False)

        output = result.stdout or ""
        stderr = result.stderr or ""
        if stderr:
            output += f"\nSTDERR:\n{stderr}"

        # Build interaction log
        log_lines = []
        log_lines.append(f"$ {entry_command}")
        for line in input_lines:
            log_lines.append(f"[Input] {line}")
        log_lines.append("--- Output ---")
        log_lines.append(output)

        status = "success"
        if result.returncode != 0:
            status = f"exit_code_{result.returncode}"

        return json.dumps({
            "status": status,
            "context": context,
            "log": "\n".join(log_lines),
            "exit_code": result.returncode,
        }, ensure_ascii=False, indent=2)


# ── Interactive Shell Session Tools ──

@register_tool
class StartInteractiveShellTool(Tool):
    """Start a new interactive shell session (pexpect-like)."""

    name = "start_interactive_shell"
    description = (
        "Start a new interactive shell session and return the session_id. "
        "Use run_interactive_shell to send commands, and kill_shell_session to terminate."
    )
    default_permission_level = "allow"
    parameters = {
        "type": "object",
        "properties": {
            "cmd": {
                "type": "string",
                "description": "Initial command to start in the shell (e.g. 'python').",
            },
            "cwd": {
                "type": "string",
                "description": "Working directory for the shell session.",
            },
        },
        "required": ["cmd"],
    }

    def execute(self, **kwargs) -> str:
        cmd = kwargs["cmd"]
        cwd = kwargs.get("cwd")

        session_id = _next_session_id()

        try:
            proc = subprocess.Popen(
                cmd,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd,
            )
        except Exception as e:
            return f"Error starting shell session: {e}"

        with _session_lock:
            _shell_sessions[session_id] = proc

        return json.dumps({
            "session_id": session_id,
            "status": "started",
            "command": cmd,
        })


@register_tool
class RunInteractiveShellTool(Tool):
    """Send a command to an existing interactive shell session."""

    name = "run_interactive_shell"
    description = (
        "Send user input to an active shell session and get the output. "
        "The session must have been started with start_interactive_shell."
    )
    default_permission_level = "allow"
    parameters = {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "description": "The session ID returned by start_interactive_shell.",
            },
            "user_input": {
                "type": "string",
                "description": "The input/command to send to the shell.",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds for this input. Default 30.",
            },
        },
        "required": ["session_id", "user_input"],
    }

    def execute(self, **kwargs) -> str:
        session_id = kwargs["session_id"]
        user_input = kwargs["user_input"]
        timeout = kwargs.get("timeout", 30)

        with _session_lock:
            proc = _shell_sessions.get(session_id)

        if proc is None:
            return f"Error: No active session with id '{session_id}'"

        if proc.poll() is not None:
            # Process already terminated — collect remaining output
            stdout, stderr = proc.communicate(timeout=5)
            output = stdout or ""
            if stderr:
                output += f"\nSTDERR:\n{stderr}"
            with _session_lock:
                _shell_sessions.pop(session_id, None)
            return json.dumps({
                "status": "terminated",
                "exit_code": proc.returncode,
                "output": output,
            })

        try:
            proc.stdin.write(user_input + "\n")
            proc.stdin.flush()
        except BrokenPipeError:
            stdout, stderr = proc.communicate(timeout=5)
            output = stdout or ""
            if stderr:
                output += f"\nSTDERR:\n{stderr}"
            return json.dumps({
                "status": "terminated",
                "exit_code": proc.returncode,
                "output": output,
            })

        # Give the process a moment to produce output
        time.sleep(min(2, timeout))

        # Non-blocking read of available output
        import select
        output = ""
        try:
            while True:
                ready, _, _ = select.select([proc.stdout], [], [], 1.0)
                if not ready:
                    break
                chunk = proc.stdout.read(4096)
                if not chunk:
                    break
                output += chunk
        except Exception:
            pass

        return json.dumps({
            "status": "running",
            "output": output,
        })


@register_tool
class KillShellSessionTool(Tool):
    """Terminate an interactive shell session."""

    name = "kill_shell_session"
    description = "Terminate an active shell session to free resources."
    default_permission_level = "allow"
    parameters = {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "description": "The session ID to terminate.",
            },
        },
        "required": ["session_id"],
    }

    def execute(self, **kwargs) -> str:
        session_id = kwargs["session_id"]

        with _session_lock:
            proc = _shell_sessions.pop(session_id, None)

        if proc is None:
            return f"Warning: No active session with id '{session_id}'"

        try:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=3)
        except Exception as e:
            return f"Warning: Error terminating session: {e}"

        return f"Session '{session_id}' terminated."


# ── List Workspace Tool (PRDBench naming) ──

@register_tool
class ListWorkspaceTool(Tool):
    """List files in a workspace directory (PRDBench-compatible wrapper)."""

    name = "list_workspace"
    description = "List files and directories at the given absolute path."
    default_permission_level = "allow"
    parameters = {
        "type": "object",
        "properties": {
            "workspace_name": {
                "type": "string",
                "description": "Absolute path to the directory to list.",
            },
        },
        "required": ["workspace_name"],
    }

    def execute(self, **kwargs) -> str:
        workspace_name = kwargs["workspace_name"]
        try:
            path = Path(workspace_name)
            if not path.is_dir():
                return f"Error: '{workspace_name}' is not a directory"
            entries = sorted(
                path.rglob("*"),
                key=lambda p: (not p.is_dir(), str(p).lower()),
            )
            lines = []
            for entry in entries:
                rel = entry.relative_to(path)
                prefix = "[DIR]  " if entry.is_dir() else "[FILE] "
                size = ""
                try:
                    if entry.is_file():
                        size = f" ({entry.stat().st_size} bytes)"
                except OSError:
                    pass
                lines.append(f"{prefix}{rel}{size}")
            return "\n".join(lines) if lines else "(empty directory)"
        except PermissionError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Error listing workspace: {e}"


# ── Exit Loop Tool (signal task completion) ──

@register_tool
class ExitLoopTool(Tool):
    """Signal that the agent has finished its task."""

    name = "exit_loop"
    description = "Call when you finish all tasks to signal completion."
    default_permission_level = "allow"
    parameters = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    def execute(self, **kwargs) -> str:
        return "Loop exit signaled. Task complete."
