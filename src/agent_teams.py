"""Multi-agent team system — spawn, coordinate, and manage teammate agents.

Concurrency strategy (3-layer protection):
  1. Workspace partitioning — each teammate works in workspace/.agent/{name}/
  2. FileLockManager — advisory per-path locks, agents must acquire before writing
  3. Optimistic concurrency — track mtime at read, reject write if file changed since
"""
import json
import logging
import time
import threading
from pathlib import Path
from typing import Any

from ._constants import ALLOWED_BASE_DIR, client, MODEL_ID
from .compact import MAX_CONTEXT_TOKENS, llm_compact_messages

logger = logging.getLogger("penguin")

VALID_MSG_TYPE = {
    "message",
    "broadcast",
    "shutdown_request",
    "shutdown_response",
    "plan_approval_response",
}

AGENT_WORKSPACE_DIR = ALLOWED_BASE_DIR / ".agent"
SHARED_DIR = ALLOWED_BASE_DIR / "shared"


# ═══════════════════════════════════════════════════════════════
# FileLockManager — prevents concurrent writes to the same file
# ═══════════════════════════════════════════════════════════════

class FileLockManager:
    """Advisory per-path lock with timeout.

    Usage:
        mgr = FileLockManager()
        ok = mgr.acquire("reviewer", "src/main.py")
        if ok:
            try:
                ...  # write the file
            finally:
                mgr.release("reviewer", "src/main.py")
    """

    def __init__(self, timeout: float = 30.0):
        self._locks: dict[str, threading.Lock] = {}
        self._owners: dict[str, str] = {}          # path -> agent name
        self._meta: threading.Lock = threading.Lock()  # guards _locks/_owners
        self._timeout = timeout

    def _get_lock(self, path: str) -> threading.Lock:
        with self._meta:
            if path not in self._locks:
                self._locks[path] = threading.Lock()
            return self._locks[path]

    def acquire(self, agent: str, path: str) -> bool:
        lock = self._get_lock(path)
        acquired = lock.acquire(timeout=self._timeout)
        if acquired:
            with self._meta:
                self._owners[path] = agent
            return True
        owner = self._owners.get(path, "unknown")
        logger.warning("File lock contention: %s blocked on %s (held by %s)", agent, path, owner)
        return False

    def release(self, agent: str, path: str):
        with self._meta:
            if path in self._owners and self._owners[path] == agent:
                del self._owners[path]
            lock = self._locks.get(path)
        if lock:
            lock.release()

    def is_locked(self, path: str) -> bool:
        with self._meta:
            lock = self._locks.get(path)
            if lock is None:
                return False
            return lock.locked()

    def owner(self, path: str) -> str | None:
        with self._meta:
            return self._owners.get(path)


# ═══════════════════════════════════════════════════════════════
# FileVersionTracker — optimistic concurrency (detect stale writes)
# ═══════════════════════════════════════════════════════════════

class FileVersionTracker:
    """Track (mtime, size) when an agent reads a file.  Before write,
    verify the file hasn't been modified by another agent since the read.

    If the agent never read the file, the write is allowed (new file or
    deliberate overwrite).  This prevents the classic lost-update:
        A reads v1 → B writes v2 → A writes based on v1 (clobbers B's work)
    """

    def __init__(self):
        # {agent_name: {path: (mtime_ns, size)}}
        self._versions: dict[str, dict[str, tuple[int, int]]] = {}
        self._lock = threading.Lock()

    def record_read(self, agent: str, path: str):
        try:
            stat = Path(path).stat()
            with self._lock:
                self._versions.setdefault(agent, {})[path] = (stat.st_mtime_ns, stat.st_size)
        except OSError:
            pass

    def check_before_write(self, agent: str, path: str) -> str | None:
        """Return None if write is safe, or an error message if the file
        was modified since the agent last read it."""
        with self._lock:
            snapshot = self._versions.get(agent, {}).get(path)
        if snapshot is None:
            return None  # Agent never read — allow
        try:
            stat = Path(path).stat()
        except OSError:
            return None  # File gone — allow (will be created)
        if (stat.st_mtime_ns, stat.st_size) != snapshot:
            return (
                f"CONFLICT: File '{path}' was modified by another agent since you last read it. "
                f"Re-read the file first, then apply your changes."
            )
        return None

    def clear(self, agent: str):
        with self._lock:
            self._versions.pop(agent, None)


# ═══════════════════════════════════════════════════════════════
# MessageBus — JSONL inbox per teammate (thread-safe)
# ═══════════════════════════════════════════════════════════════

class MessageBus:
    """JSONL-based message bus — one inbox file per teammate."""

    def __init__(self, inbox_dir: Path):
        self.dir = inbox_dir
        self.dir.mkdir(parents=True, exist_ok=True)
        self._locks: dict[str, threading.Lock] = {}
        self._meta_lock = threading.Lock()

    def _get_lock(self, name: str) -> threading.Lock:
        with self._meta_lock:
            if name not in self._locks:
                self._locks[name] = threading.Lock()
            return self._locks[name]

    def send(
        self,
        sender: str,
        to: str,
        content: str,
        msg_type: str = "message",
        extra: dict | None = None,
    ) -> str:
        if msg_type not in VALID_MSG_TYPE:
            return f"Error: Invalid type '{msg_type}'. Valid: {VALID_MSG_TYPE}"
        msg = {
            "type": msg_type,
            "from": sender,
            "content": content,
            "timestamp": time.time(),
        }
        if extra:
            msg.update(extra)
        lock = self._get_lock(to)
        with lock:
            inbox_path = self.dir / f"{to}.jsonl"
            with open(inbox_path, "a") as f:
                f.write(json.dumps(msg) + "\n")
        return f"Sent {msg_type} to {to}"

    def read_inbox(self, name: str) -> list[dict]:
        lock = self._get_lock(name)
        with lock:
            inbox_path = self.dir / f"{name}.jsonl"
            if not inbox_path.exists():
                return []
            messages = []
            for line in inbox_path.read_text().strip().splitlines():
                if line:
                    messages.append(json.loads(line))
            inbox_path.write_text("")
            return messages

    def broadcast(self, sender: str, content: str, teammates: list[str]) -> str:
        count = 0
        for name in teammates:
            if name != sender:
                self.send(sender, name, content, "broadcast")
                count += 1
        return f"Broadcast to {count} teammates"


# ═══════════════════════════════════════════════════════════════
# WorkspaceResolver — path rewriting per agent
# ═══════════════════════════════════════════════════════════════

class WorkspaceResolver:
    """Map a teammate's relative/absolute paths into their partitioned
    workspace, while allowing explicit access to the shared area.

    Rules:
      - Relative paths → workspace/.agent/{agent_name}/
      - "shared/..." → workspace/shared/
      - Absolute paths under ALLOWED_BASE_DIR → rewritten to agent workspace
      - Paths already under .agent/{agent}/ → passed through
      - Coordinator (agent=None) → no rewriting, uses workspace/ directly
    """

    def __init__(self):
        AGENT_WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
        SHARED_DIR.mkdir(parents=True, exist_ok=True)

    def resolve(self, path: str, agent: str | None = None) -> str:
        """Resolve path for a given agent. Returns absolute path string."""
        if agent is None:
            return path  # Coordinator — no rewriting

        p = Path(path)

        # Already inside this agent's workspace — pass through
        agent_dir = AGENT_WORKSPACE_DIR / agent
        try:
            if p.is_absolute():
                p.resolve().relative_to(agent_dir)
                return str(p)
        except (ValueError, RuntimeError):
            pass

        # Explicit shared/ prefix → shared area
        if not p.is_absolute() and str(p).startswith("shared"):
            return str(SHARED_DIR / str(p)[7:].lstrip("/\\"))

        # Already absolute under ALLOWED_BASE_DIR → remap into agent workspace
        if p.is_absolute():
            try:
                rel = p.resolve().relative_to(ALLOWED_BASE_DIR)
                return str(agent_dir / rel)
            except (ValueError, RuntimeError):
                return str(p)  # Outside workspace — leave as-is (tools will reject)

        # Relative path → agent workspace
        return str(agent_dir / path)

    def ensure_agent_workspace(self, agent: str):
        """Create the agent's workspace directory if it doesn't exist."""
        agent_dir = AGENT_WORKSPACE_DIR / agent
        agent_dir.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════
# TeamManager — orchestration layer
# ═══════════════════════════════════════════════════════════════

class TeamManager:
    """Manage a team of teammate agents running in background threads."""

    def __init__(self, team_dir: Path):
        self.team_dir = team_dir
        self.team_dir.mkdir(parents=True, exist_ok=True)
        self.config_path = self.team_dir / "config.json"
        self.config = self._load_config()
        self.threads: dict[str, threading.Thread] = {}
        self._stop_flags: dict[str, threading.Event] = {}
        self._config_lock = threading.Lock()

        self.bus = MessageBus(ALLOWED_BASE_DIR / ".inbox")
        self.lock_mgr = FileLockManager()
        self.version_tracker = FileVersionTracker()
        self.workspace = WorkspaceResolver()

    # ── Config persistence (thread-safe) ──

    def _load_config(self) -> dict:
        if self.config_path.exists():
            return json.loads(self.config_path.read_text())
        return {"team_name": "default", "members": []}

    def _save_config(self):
        with self._config_lock:
            self.config_path.write_text(json.dumps(self.config, indent=2))

    def _find_member(self, name: str) -> dict | None:
        for m in self.config["members"]:
            if m["name"] == name:
                return m
        return None

    # ── Public API ──

    def spawn(self, name: str, role: str, prompt: str) -> str:
        member = self._find_member(name)
        if member:
            if member["status"] not in {"idle", "shutdown"}:
                return f"Error: '{name}' is currently {member['status']}"
            member["status"] = "working"
            member["role"] = role
        else:
            member = {"name": name, "role": role, "status": "working"}
            self.config["members"].append(member)
        self._save_config()

        # Create agent workspace
        self.workspace.ensure_agent_workspace(name)

        stop_event = threading.Event()
        self._stop_flags[name] = stop_event

        thread = threading.Thread(
            target=self._teammate_loop,
            args=(name, role, prompt, stop_event),
            daemon=True,
        )
        self.threads[name] = thread
        thread.start()
        return f"Spawned '{name}' (role: {role})"

    def list_members(self) -> str:
        members = self.config.get("members", [])
        if not members:
            return "No team members."
        lines = []
        for m in members:
            ws = AGENT_WORKSPACE_DIR / m["name"]
            lines.append(
                f"  {m['name']} | role: {m.get('role', '?')} | status: {m.get('status', '?')} | workspace: {ws}"
            )
        return "\n".join(lines)

    def shutdown(self, name: str) -> str:
        member = self._find_member(name)
        if not member:
            return f"Error: No member '{name}'"
        if name in self._stop_flags:
            self._stop_flags[name].set()
        if member["status"] in {"working", "idle"}:
            member["status"] = "shutdown"
            self._save_config()
        return f"Shutdown request sent to '{name}'"

    def send_message(self, sender: str, to: str, content: str) -> str:
        member = self._find_member(to)
        if not member:
            return f"Error: No member '{to}'"
        return self.bus.send(sender, to, content, "message")

    def broadcast_message(self, sender: str, content: str) -> str:
        teammates = [m["name"] for m in self.config.get("members", [])]
        return self.bus.broadcast(sender, content, teammates)

    # ── Agent-scoped tool execution ──

    def _agent_execute_tool(self, agent: str, name: str, args: dict) -> str:
        """Execute a tool on behalf of an agent with concurrency guards.

        Applies:
          - Path rewriting via WorkspaceResolver
          - File locking for write operations
          - Optimistic concurrency check for write operations
          - Version tracking on read operations
        """
        from .tools import _truncate_for_context, execute_tool, resolve_and_validate_path

        WRITE_TOOLS = {"write_file", "edit_file"}
        READ_TOOLS = {"read_file", "search_files", "list_directory"}

        # Rewrite paths for this agent
        if name in ("read_file", "write_file", "edit_file", "list_directory", "search_files"):
            key = "path" if "path" in args else "path"
            if key in args:
                original = args[key]
                args[key] = self.workspace.resolve(original, agent)

        # Pre-write guards
        if name in WRITE_TOOLS:
            path = args.get("path", "")
            # 1) Optimistic concurrency check
            conflict = self.version_tracker.check_before_write(agent, path)
            if conflict:
                return conflict
            # 2) Acquire file lock
            if not self.lock_mgr.acquire(agent, path):
                owner = self.lock_mgr.owner(path) or "another agent"
                return (
                    f"CONFLICT: File '{path}' is currently being written by {owner}. "
                    f"Wait and retry."
                )

        # Track reads for later conflict detection
        if name in READ_TOOLS:
            path = args.get("path", "")
            if path:
                self.version_tracker.record_read(agent, path)

        try:
            return execute_tool(name, args, skip_permission_check=True)
        finally:
            if name in WRITE_TOOLS:
                path = args.get("path", "")
                self.lock_mgr.release(agent, path)

    # ── Teammate execution loop ──

    def _teammate_loop(
        self,
        name: str,
        role: str,
        prompt: str,
        stop_event: threading.Event,
    ):
        # Lazy imports to break circular dependency with tools.py
        from .tools import TOOL_DEFINITIONS, _truncate_for_context

        agent_workspace = AGENT_WORKSPACE_DIR / name
        sys_prompt = (
            f"You are '{name}', a teammate with role: {role}.\n"
            f"Your private workspace: {agent_workspace}\n"
            f"Shared area for cross-agent files: {SHARED_DIR}\n\n"
            f"Workspace rules:\n"
            f"- Relative paths resolve to your private workspace ({agent_workspace})\n"
            f"- Use 'shared/...' prefix to write to the shared area visible to all agents\n"
            f"- If you get a CONFLICT error, re-read the file and retry\n"
            f"- Use send_message to coordinate with other teammates before editing shared files\n\n"
            f"Complete your assigned task thoroughly. When done, provide a concise summary.\n"
            f"Do NOT delegate — complete the work yourself."
        )

        # Tools available to teammates (block delegate + team tools to prevent recursion)
        _TEAM_BLOCKED = {"delegate", "team_spawn", "team_shutdown", "team_send", "team_broadcast"}
        teammate_tools = [t for t in TOOL_DEFINITIONS if t["name"] not in _TEAM_BLOCKED]

        # Add teammate-specific tools
        send_msg_schema = {
            "name": "send_message",
            "description": "Send a message to another teammate.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Name of the teammate to send to"},
                    "content": {"type": "string", "description": "Message content"},
                },
                "required": ["to", "content"],
            },
        }
        teammate_tools.append(send_msg_schema)

        messages: list[dict[str, Any]] = [{"role": "user", "content": prompt}]
        max_iterations = 50
        max_output_tokens = 16384

        for iteration in range(max_iterations):
            if stop_event.is_set():
                self._set_status(name, "shutdown")
                self.version_tracker.clear(name)
                logger.info("Teammate '%s' stopped by shutdown request", name)
                return

            # Poll inbox and inject messages
            inbox_msgs = self.bus.read_inbox(name)
            if inbox_msgs:
                msg_lines = []
                for msg in inbox_msgs:
                    if msg["type"] == "shutdown_request":
                        self._set_status(name, "shutdown")
                        self.bus.send(name, msg["from"], "Shutdown acknowledged", "shutdown_response")
                        self.version_tracker.clear(name)
                        logger.info("Teammate '%s' shutting down per request", name)
                        return
                    msg_lines.append(f"[From {msg['from']} ({msg['type']})]: {msg['content']}")
                messages.append({
                    "role": "user",
                    "content": "<inbox>\n" + "\n".join(msg_lines) + "\n</inbox>"
                })

            # Compact if needed
            messages[:] = llm_compact_messages(
                messages, client, MODEL_ID, max_tokens=MAX_CONTEXT_TOKENS
            )

            collected_content = ""
            has_tool_calls = False
            was_truncated = False
            tool_calls_list: list[dict] = []

            # Call LLM
            try:
                with client.messages.stream(
                    model=MODEL_ID,
                    max_tokens=max_output_tokens,
                    system=sys_prompt,
                    messages=messages,
                    tools=teammate_tools,
                ) as stream:
                    tool_use_blocks: dict[int, dict[str, Any]] = {}
                    for event in stream:
                        if event.type == "content_block_delta":
                            if event.delta.type == "text_delta":
                                collected_content += event.delta.text
                            elif event.delta.type == "input_json_delta":
                                idx = event.index
                                if idx in tool_use_blocks and not tool_use_blocks[idx].get("_complete"):
                                    tool_use_blocks[idx]["_partial_json"] += event.delta.partial_json
                        elif event.type == "content_block_start":
                            if event.content_block.type == "tool_use":
                                tool_use_blocks[event.index] = {
                                    "id": event.content_block.id,
                                    "name": event.content_block.name,
                                    "_partial_json": "",
                                    "_complete": False,
                                }
                        elif event.type == "content_block_stop":
                            if event.index in tool_use_blocks:
                                block = tool_use_blocks[event.index]
                                block["_complete"] = True
                                raw_json = block["_partial_json"]
                                if raw_json:
                                    try:
                                        block["input"] = json.loads(raw_json)
                                    except json.JSONDecodeError:
                                        block["input"] = {}
                                else:
                                    block["input"] = {}

                    final_msg = stream.get_final_message()
                    if final_msg.stop_reason == "max_tokens":
                        was_truncated = True

                tool_calls_list = [
                    {"id": b["id"], "name": b["name"], "input": b["input"]}
                    for _, b in sorted(tool_use_blocks.items())
                ]
                if tool_calls_list:
                    has_tool_calls = True

            except Exception as e:
                logger.error("Teammate '%s' API error: %s", name, e)
                self._set_status(name, "error")
                self.version_tracker.clear(name)
                return

            # Build assistant message
            assistant_content: list[dict[str, Any]] = []
            if collected_content:
                assistant_content.append({"type": "text", "text": collected_content})
            for tc in tool_calls_list:
                assistant_content.append({
                    "type": "tool_use",
                    "id": tc["id"],
                    "name": tc["name"],
                    "input": tc["input"],
                })
            messages.append({"role": "assistant", "content": assistant_content})

            # Handle truncation
            if was_truncated:
                messages.append({
                    "role": "user",
                    "content": "[System: Response truncated. Continue from where you left off.]"
                })
                continue

            # No tool calls → task complete
            if not has_tool_calls:
                self._set_status(name, "idle")
                self.version_tracker.clear(name)
                logger.info("Teammate '%s' completed task", name)
                return

            # Execute tool calls with concurrency guards
            tool_results: list[dict[str, Any]] = []
            for tc in tool_calls_list:
                fn_name = tc["name"]
                fn_args = dict(tc["input"])  # copy to avoid mutating original

                if fn_name == "send_message":
                    result = self.bus.send(name, fn_args.get("to", ""), fn_args.get("content", ""))
                else:
                    result = self._agent_execute_tool(name, fn_name, fn_args)

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tc["id"],
                    "content": _truncate_for_context(result),
                })

            messages.append({"role": "user", "content": tool_results})

        # Hit iteration limit
        self._set_status(name, "idle")
        self.version_tracker.clear(name)
        logger.warning("Teammate '%s' hit iteration limit", name)

    def _set_status(self, name: str, status: str):
        member = self._find_member(name)
        if member:
            member["status"] = status
            self._save_config()


# ── Global singleton ──
TEAM_MANAGER = TeamManager(ALLOWED_BASE_DIR / ".team")
