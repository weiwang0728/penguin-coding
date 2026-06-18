"""PRDBench HTTP API server — implements the ADK-compatible endpoints.

Exposes:
  POST   /apps/{app_name}/users/{user_id}/sessions/{session_id}   — Create session
  DELETE /apps/{app_name}/users/{user_id}/sessions/{session_id}   — Delete session
  POST   /run                                                       — Execute a prompt

Compatible with PRDBench's:
  - Generation/generate_dev.py      (DEV stage, appName=code_agent_local)
  - Evaluation/ready_test.py        (EVAL stage, appName=code_eval_agent_workspace_dir)
  - Evaluation/generate_code_FD.py  (EVAL stage, appName=code_eval_agent)
"""

import json
import logging
import os
import re
import sys
import uuid
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any
from urllib.parse import urlparse

from .adapter import (
    session_manager,
    run_prdbench_agent,
    PRDBenchSession,
)
from .config import APP_NAME, DEFAULT_HOST, DEFAULT_PORT

logger = logging.getLogger("penguin.prdbench.server")


class PRDBenchHandler(BaseHTTPRequestHandler):
    """HTTP request handler implementing PRDBench's ADK-compatible API."""

    def _send_json(self, data: Any, status: int = 200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    def _parse_session_path(self) -> tuple[str, str, str] | None:
        """Parse /apps/{app}/users/{user}/sessions/{session_id} from the path.

        Returns (app_name, user_id, session_id) or None.
        """
        pattern = r"/apps/([^/]+)/users/([^/]+)/sessions/(.+)"
        m = re.match(pattern, self.path)
        if not m:
            return None
        return m.group(1), m.group(2), m.group(3)

    # ── POST ──

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Session creation: POST /apps/{app}/users/{user}/sessions/{session_id}
        session_info = self._parse_session_path()
        if session_info:
            app_name, user_id, session_id = session_info
            body = self._read_body()

            # Delete existing session if any, then create new
            session_manager.delete(session_id)
            session = session_manager.create(session_id, user_id, app_name)

            logger.info(f"Session created: {session_id} (user={user_id}, app={app_name})")
            self._send_json({
                "id": session_id,
                "userId": user_id,
                "appName": app_name,
                "state": {},
                "events": [],
            })
            return

        # Run query: POST /run
        if path == "/run":
            body = self._read_body()
            app_name = body.get("appName", APP_NAME)
            user_id = body.get("userId", "")
            session_id = body.get("sessionId", "")
            new_message = body.get("newMessage", {})
            parts = new_message.get("parts", [])

            # Extract text from parts
            prompt_text = ""
            for part in parts:
                if isinstance(part, dict) and "text" in part:
                    prompt_text += part["text"]

            if not prompt_text:
                self._send_json({"error": "No text in newMessage.parts"}, 400)
                return

            # Get or create session
            session = session_manager.get(session_id)
            if session is None:
                session = session_manager.create(session_id, user_id, app_name)

            # Determine mode from appName and prompt content
            mode = "eval"
            prompt_lower = prompt_text.lower()
            # DEV stage uses appName "code_agent_local"
            if "code_agent_local" in app_name or "develop" in prompt_lower or "prd.md" in prompt_lower:
                mode = "dev"
            # EVAL stage uses appName "code_eval_agent*" and contains metric evaluation
            elif "metric" in prompt_lower or "evaluation metric" in prompt_lower or "score" in prompt_lower:
                mode = "eval"
            elif "debug" in prompt_lower or "fix" in prompt_lower:
                mode = "debug"

            logger.info(
                f"Running agent: session={session_id}, app={app_name}, mode={mode}, "
                f"prompt_len={len(prompt_text)}"
            )

            # Run the agent
            result = run_prdbench_agent(
                user_message=prompt_text,
                session=session,
                mode=mode,
            )

            # Format response to match ADK's expected format
            response_data = {
                "id": str(uuid.uuid4()),
                "content": {
                    "role": "model",
                    "parts": [
                        {
                            "text": result.get("content", ""),
                        }
                    ],
                },
                "author": app_name,
                "timestamp": datetime.now().isoformat(),
            }

            self._send_json(response_data)
            return

        self._send_json({"error": f"Unknown POST path: {path}"}, 404)

    # ── DELETE ──

    def do_DELETE(self):
        session_info = self._parse_session_path()
        if session_info:
            _, _, session_id = session_info
            session_manager.delete(session_id)
            logger.info(f"Session deleted: {session_id}")
            self._send_json({"status": "deleted", "sessionId": session_id})
            return

        self._send_json({"error": "Unknown DELETE path"}, 404)

    # ── GET (health check) ──

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/health"):
            self._send_json({
                "status": "ok",
                "app": APP_NAME,
                "sessions": len(session_manager._sessions),
            })
            return

        self._send_json({"error": "Not found"}, 404)

    def log_message(self, format, *args):
        logger.info(format % args)


def run_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
    """Start the PRDBench HTTP API server."""
    server_address = (host, port)
    httpd = HTTPServer(server_address, PRDBenchHandler)
    logger.info(f"PRDBench server starting on {host}:{port}")
    logger.info(f"App name: {APP_NAME}")
    logger.info(f"Endpoints:")
    logger.info(f"  POST   /apps/{{app}}/users/{{user}}/sessions/{{sid}}  — Create session")
    logger.info(f"  DELETE /apps/{{app}}/users/{{user}}/sessions/{{sid}}  — Delete session")
    logger.info(f"  POST   /run                                         — Execute prompt")
    logger.info(f"  GET    /health                                      — Health check")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
        httpd.shutdown()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    host = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_HOST
    run_server(host, port)
