"""Tests for session auto-save feature."""

import json
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from src.session import (
    SESSION_DIR,
    _extract_session_name,
    autosave_session,
    load_session,
    list_sessions,
    save_session,
    _current_session_file,
)


@pytest.fixture(autouse=True)
def tmp_session_dir(tmp_path, monkeypatch):
    """Redirect SESSION_DIR to a temp dir and reset module state for each test."""
    monkeypatch.setattr("src.session.SESSION_DIR", tmp_path)
    monkeypatch.setattr("src.session._current_session_file", None)
    yield tmp_path


# ── _extract_session_name ─────────────────────────────────────────────

class TestExtractSessionName:
    def test_string_content(self):
        msgs = [{"role": "user", "content": "Hello world"}]
        assert _extract_session_name(msgs) == "Hello world"

    def test_list_content_text_block(self):
        msgs = [{"role": "user", "content": [{"type": "text", "text": "Fix the bug"}]}]
        assert _extract_session_name(msgs) == "Fix the bug"

    def test_truncate_to_60_chars(self):
        long_text = "x" * 100
        msgs = [{"role": "user", "content": long_text}]
        assert _extract_session_name(msgs) == "x" * 60
        assert len(_extract_session_name(msgs)) == 60

    def test_last_user_message_wins(self):
        msgs = [
            {"role": "user", "content": "First"},
            {"role": "assistant", "content": "Ok"},
            {"role": "user", "content": "Second"},
        ]
        assert _extract_session_name(msgs) == "Second"

    def test_empty_messages(self):
        assert _extract_session_name([]) == "untitled"

    def test_no_user_messages(self):
        msgs = [{"role": "assistant", "content": "Hi"}]
        assert _extract_session_name(msgs) == "untitled"

    def test_empty_string_content(self):
        msgs = [{"role": "user", "content": ""}]
        assert _extract_session_name(msgs) == "untitled"

    def test_whitespace_only_stripped(self):
        msgs = [{"role": "user", "content": "   hello   "}]
        assert _extract_session_name(msgs) == "hello"

    def test_list_content_no_text_block(self):
        msgs = [{"role": "user", "content": [{"type": "image", "url": "x"}]}]
        assert _extract_session_name(msgs) == "untitled"

    def test_non_string_non_list_content(self):
        msgs = [{"role": "user", "content": 123}]
        assert _extract_session_name(msgs) == "untitled"


# ── autosave_session ──────────────────────────────────────────────────

class TestAutosaveSession:
    def test_first_save_creates_file(self, tmp_session_dir):
        msgs = [{"role": "user", "content": "Hello"}]
        sid = autosave_session(msgs, "test-model")
        assert sid
        path = tmp_session_dir / f"{sid}.json"
        assert path.exists()

    def test_first_save_has_correct_fields(self, tmp_session_dir):
        msgs = [{"role": "user", "content": "Hello"}]
        sid = autosave_session(msgs, "test-model")
        data = json.loads((tmp_session_dir / f"{sid}.json").read_text())
        assert data["id"] == sid
        assert data["name"] == "Hello"
        assert data["model"] == "test-model"
        assert data["messages"] == msgs
        assert "saved_at" in data

    def test_second_save_overwrites_same_file(self, tmp_session_dir):
        msgs1 = [{"role": "user", "content": "First"}]
        sid1 = autosave_session(msgs1, "test-model")

        msgs2 = msgs1 + [{"role": "assistant", "content": "Ok"}, {"role": "user", "content": "Second"}]
        sid2 = autosave_session(msgs2, "test-model")

        assert sid1 == sid2
        files = list(tmp_session_dir.glob("*.json"))
        assert len(files) == 1

    def test_overwrite_updates_name_to_last_input(self, tmp_session_dir):
        msgs = [{"role": "user", "content": "First"}]
        sid = autosave_session(msgs, "test-model")

        msgs.append({"role": "assistant", "content": "Ok"})
        msgs.append({"role": "user", "content": "Second"})
        autosave_session(msgs, "test-model")

        data = json.loads((tmp_session_dir / f"{sid}.json").read_text())
        assert data["name"] == "Second"

    def test_overwrite_updates_messages(self, tmp_session_dir):
        msgs1 = [{"role": "user", "content": "First"}]
        sid = autosave_session(msgs1, "test-model")

        msgs2 = msgs1 + [{"role": "assistant", "content": "Done"}]
        autosave_session(msgs2, "test-model")

        data = json.loads((tmp_session_dir / f"{sid}.json").read_text())
        assert len(data["messages"]) == 2

    def test_overwrite_updates_saved_at(self, tmp_session_dir):
        msgs = [{"role": "user", "content": "Hello"}]
        sid = autosave_session(msgs, "test-model")
        data1 = json.loads((tmp_session_dir / f"{sid}.json").read_text())

        time.sleep(1.1)
        msgs.append({"role": "assistant", "content": "Hi"})
        autosave_session(msgs, "test-model")
        data2 = json.loads((tmp_session_dir / f"{sid}.json").read_text())

        assert data2["saved_at"] != data1["saved_at"]

    def test_overwrite_updates_model(self, tmp_session_dir):
        msgs = [{"role": "user", "content": "Hello"}]
        sid = autosave_session(msgs, "model-v1")

        autosave_session(msgs, "model-v2")
        data = json.loads((tmp_session_dir / f"{sid}.json").read_text())
        assert data["model"] == "model-v2"


# ── load_session + autosave interaction ────────────────────────────────

class TestLoadSessionAutosave:
    def test_load_then_autosave_overwrites_original(self, tmp_session_dir):
        msgs = [{"role": "user", "content": "Original"}]
        sid = save_session(msgs, "test-model")

        loaded = load_session(sid)
        assert loaded is not None
        loaded_msgs, loaded_model = loaded

        loaded_msgs.append({"role": "assistant", "content": "Reply"})
        loaded_msgs.append({"role": "user", "content": "Follow-up"})
        sid2 = autosave_session(loaded_msgs, loaded_model)

        assert sid2 == sid
        files = list(tmp_session_dir.glob("*.json"))
        assert len(files) == 1

        data = json.loads((tmp_session_dir / f"{sid}.json").read_text())
        assert data["name"] == "Follow-up"
        assert len(data["messages"]) == 3

    def test_load_nonexistent_returns_none(self, tmp_session_dir):
        assert load_session("nonexistent_9999") is None


# ── list_sessions ──────────────────────────────────────────────────────

class TestListSessions:
    def test_empty_dir(self, tmp_session_dir):
        assert list_sessions() == []

    def test_returns_name_field(self, tmp_session_dir):
        msgs = [{"role": "user", "content": "My session name"}]
        save_session(msgs, "test-model")

        sessions = list_sessions()
        assert len(sessions) == 1
        assert sessions[0]["name"] == "My session name"

    def test_sorted_by_most_recent(self, tmp_session_dir):
        with patch("src.session.time.strftime") as mock_time:
            mock_time.side_effect = ["20260101_120000", "2026-01-01 12:00:00",
                                     "20260102_120000", "2026-01-02 12:00:00"]
            save_session([{"role": "user", "content": "Old"}], "m1")
            save_session([{"role": "user", "content": "New"}], "m2")

        sessions = list_sessions()
        assert len(sessions) == 2
        assert sessions[0]["name"] == "New"
        assert sessions[1]["name"] == "Old"

    def test_corrupted_json_skipped(self, tmp_session_dir):
        (tmp_session_dir / "bad.json").write_text("not json")
        msgs = [{"role": "user", "content": "Good"}]
        save_session(msgs, "test-model")

        sessions = list_sessions()
        assert len(sessions) == 1
        assert sessions[0]["name"] == "Good"

    def test_missing_name_defaults_empty(self, tmp_session_dir):
        data = {"id": "20260101_000000", "model": "m1", "messages": [], "saved_at": "now"}
        (tmp_session_dir / "20260101_000000.json").write_text(json.dumps(data))

        sessions = list_sessions()
        assert sessions[0]["name"] == ""


# ── save_session (backward compatibility) ──────────────────────────────

class TestSaveSession:
    def test_creates_new_file_each_time(self, tmp_session_dir):
        with patch("src.session.time.strftime") as mock_time:
            mock_time.side_effect = ["20260101_120000", "2026-01-01 12:00:00",
                                     "20260102_120000", "2026-01-02 12:00:00"]
            sid1 = save_session([{"role": "user", "content": "A"}], "m1")
            sid2 = save_session([{"role": "user", "content": "B"}], "m1")
        assert sid1 != sid2
        files = list(tmp_session_dir.glob("*.json"))
        assert len(files) == 2

    def test_includes_name_field(self, tmp_session_dir):
        sid = save_session([{"role": "user", "content": "Hello"}], "m1")
        data = json.loads((tmp_session_dir / f"{sid}.json").read_text())
        assert data["name"] == "Hello"
