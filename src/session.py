"""Session persistence — save and load conversation history."""

import json
import time
from pathlib import Path

SESSION_DIR = Path.home() / ".penguin_sessions"

_current_session_file: str | None = None


def _extract_session_name(messages: list) -> str:
    for msg in reversed(messages):
        if msg.get("role") != "user":
            continue
        content = msg.get("content", "")
        if isinstance(content, str):
            text = content.strip()
        elif isinstance(content, list):
            text = ""
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text = block.get("text", "").strip()
                    break
        else:
            continue
        if text:
            return text[:60]
    return "untitled"


def save_session(messages: list, model: str) -> str:
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    session_id = time.strftime("%Y%m%d_%H%M%S")
    name = _extract_session_name(messages)
    data = {
        "id": session_id,
        "name": name,
        "model": model,
        "messages": messages,
        "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    path = SESSION_DIR / f"{session_id}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return session_id


def autosave_session(messages: list, model: str) -> str:
    global _current_session_file
    name = _extract_session_name(messages)

    if _current_session_file:
        path = SESSION_DIR / _current_session_file
        data = json.loads(path.read_text())
        data["messages"] = messages
        data["name"] = name
        data["saved_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        data["model"] = model
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        return data["id"]

    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    session_id = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{session_id}.json"
    data = {
        "id": session_id,
        "name": name,
        "model": model,
        "messages": messages,
        "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    path = SESSION_DIR / filename
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    _current_session_file = filename
    return session_id


def load_session(session_id: str) -> tuple | None:
    global _current_session_file
    filename = f"{session_id}.json"
    path = SESSION_DIR / filename
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    _current_session_file = filename
    return data["messages"], data["model"]


def list_sessions() -> list[dict]:
    if not SESSION_DIR.exists():
        return []
    sessions = []
    for path in sorted(SESSION_DIR.glob("*.json"), reverse=True):
        try:
            data = json.loads(path.read_text())
            sessions.append({
                "id": data["id"],
                "name": data.get("name", ""),
                "model": data["model"],
                "saved_at": data["saved_at"],
            })
        except (json.JSONDecodeError, KeyError):
            continue
    return sessions
