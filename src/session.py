"""Session persistence — save and load conversation history."""

import json
import time
from pathlib import Path

SESSION_DIR = Path.home() / ".penguin_sessions"


def save_session(messages: list, model: str) -> str:
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    session_id = time.strftime("%Y%m%d_%H%M%S")
    data = {
        "id": session_id,
        "model": model,
        "messages": messages,
        "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    path = SESSION_DIR / f"{session_id}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return session_id


def load_session(session_id: str) -> tuple | None:
    path = SESSION_DIR / f"{session_id}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    return data["messages"], data["model"]


def list_sessions() -> list[dict]:
    if not SESSION_DIR.exists():
        return []
    sessions = []
    for path in sorted(SESSION_DIR.glob("*.json"), reverse=True):
        try:
            data = json.loads(path.read_text())
            preview = ""
            for msg in data["messages"][:3]:
                content = msg.get("content", "")
                if isinstance(content, str):
                    preview = content[:60]
                    break
                elif isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            preview = block.get("text", "")[:60]
                            break
                    if preview:
                        break
            sessions.append({
                "id": data["id"],
                "model": data["model"],
                "saved_at": data["saved_at"],
                "preview": preview,
            })
        except (json.JSONDecodeError, KeyError):
            continue
    return sessions
