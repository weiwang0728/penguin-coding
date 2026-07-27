"""Minimal structured execution log for headless agent runs.

Writes JSONL events to a file for post-hoc audit of agent behavior.
Thread-safe via a single lock around file append.

Events:
  run_started    {case_id, workspace_dir}
  run_finished   {turn_count, tool_call_count, exit_code}
  run_terminated {reason, partial_turn_id}
  tool_start     {name, input}
  tool_result    {name, result}
  llm_text       {text}

Designed for headless serial runs (PRDBench DEV/EVAL). Does not track
turn_id / tool_use_id / parent_span_id - those require extended callback
signatures in agent_loop. Upgrade path: extend callbacks, add fields here.
"""

import json
import threading
import time
from pathlib import Path
from typing import Any


class ExecutionLog:
    def __init__(
        self,
        path: str | Path,
        enabled: bool = True,
        max_result_chars: int = 4096,
        run_id: str | None = None,
    ):
        self.path = Path(path)
        self.enabled = enabled
        self.max_result_chars = max_result_chars
        self.run_id = run_id
        self._lock = threading.Lock()
        self._seq = 0
        self._tool_call_count = 0

        if self.enabled:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text("", encoding="utf-8")

    def _emit(self, event: str, **fields: Any) -> None:
        if not self.enabled:
            return
        with self._lock:
            self._seq += 1
            record = {
                "seq": self._seq,
                "ts": time.time(),
                "event": event,
                "run_id": self.run_id,
                **fields,
            }
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    def _truncate(self, s: str) -> str:
        if not isinstance(s, str):
            s = str(s)
        if len(s) <= self.max_result_chars:
            return s
        head = self.max_result_chars - 512 - 40
        return (
            s[:head]
            + f"...[truncated {len(s) - self.max_result_chars} chars]..."
            + s[-512:]
        )

    def log_run_started(self, case_id: str, workspace_dir: str) -> None:
        self._emit("run_started", case_id=case_id, workspace_dir=workspace_dir)

    def log_run_finished(self, turn_count: int, tool_call_count: int, exit_code: int = 0) -> None:
        self._emit(
            "run_finished",
            turn_count=turn_count,
            tool_call_count=tool_call_count,
            exit_code=exit_code,
        )

    def log_run_terminated(self, reason: str, partial_turn_id: int = 0) -> None:
        self._emit(
            "run_terminated",
            reason=reason,
            partial_turn_id=partial_turn_id,
        )

    def log_tool_start(self, name: str, input: dict) -> None:
        self._tool_call_count += 1
        self._emit("tool_start", name=name, input=input)

    def log_tool_result(self, name: str, result: str) -> None:
        self._emit("tool_result", name=name, result=self._truncate(result))

    def log_llm_text(self, text: str) -> None:
        self._emit("llm_text", text=text)

    @property
    def tool_call_count(self) -> int:
        return self._tool_call_count
