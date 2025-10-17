"""
Session persistence utilities for ScriptAI.

Stores per-project chat sessions under a ".scriptai_sessions" folder at the
project root. A session is a JSON Lines file containing a session_start event,
one or more interaction events, and a session_end event.

Privacy mode: When DATA_PRIVACY_MODE=true, no session files are written.
"""

from __future__ import annotations

import os
import json
import socket
import uuid
from datetime import datetime
from typing import Optional, Dict, Any


SESSION_DIR_NAME = ".scriptai_sessions"
ENV_SESSION_DIR = "SCRIPT_AI_SESSION_DIR"


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    v = raw.strip().lower()
    if v in {"1", "true", "yes", "on"}:
        return True
    if v in {"0", "false", "no", "off"}:
        return False
    return default


def find_project_root(start_path: Optional[str] = None) -> str:
    """Find a reasonable project root by walking up for common markers.

    Markers considered: .git, pyproject.toml, package.json, requirements.txt,
    setup.py, .hg, .svn
    """
    path = os.path.abspath(start_path or os.getcwd())
    prev = None
    markers = {
        ".git",
        "pyproject.toml",
        "package.json",
        "requirements.txt",
        "setup.py",
        ".hg",
        ".svn",
    }
    while path and path != prev:
        for m in markers:
            if os.path.exists(os.path.join(path, m)):
                return path
        prev = path
        path = os.path.dirname(path)
    # Fallback to starting directory if no markers found
    return os.path.abspath(start_path or os.getcwd())


def ensure_session_dir(project_root: Optional[str] = None) -> str:
    """Ensure the session directory exists and return its path.

    Honors ENV_SESSION_DIR if set; otherwise creates ".scriptai_sessions"
    at the project root.
    """
    override = os.getenv(ENV_SESSION_DIR)
    if override:
        session_dir = os.path.abspath(override)
    else:
        root = find_project_root(project_root)
        session_dir = os.path.join(root, SESSION_DIR_NAME)
    os.makedirs(session_dir, exist_ok=True)
    return session_dir


class SessionLogger:
    """Simple session logger that writes JSONL events per project."""

    def __init__(
        self, project_root: Optional[str] = None, privacy_mode: Optional[bool] = None
    ):
        self.privacy_mode = (
            _env_bool("DATA_PRIVACY_MODE", False)
            if privacy_mode is None
            else bool(privacy_mode)
        )
        self.project_root = find_project_root(project_root)
        self.session_dir = None  # type: Optional[str]
        self.session_path = None  # type: Optional[str]
        self.session_id = None  # type: Optional[str]
        self.host = socket.gethostname()

        # If privacy mode is on, avoid creating directories
        if not self.privacy_mode:
            try:
                self.session_dir = ensure_session_dir(self.project_root)
            except Exception:
                # If we cannot create the directory (read-only FS, etc.),
                # keep session_dir as None and effectively no-op.
                self.session_dir = None

    def start(
        self, label: Optional[str] = None, model: Optional[str] = None
    ) -> Optional[str]:
        if self.privacy_mode:
            return None
        if not self.session_dir:
            return None

        self.session_id = str(uuid.uuid4())
        ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        filename = f"session-{ts}-{os.getpid()}-{self.session_id}.jsonl"
        self.session_path = os.path.join(self.session_dir, filename)

        # Write session_start event
        self._write_event(
            {
                "type": "session_start",
                "timestamp": datetime.utcnow().isoformat(),
                "id": self.session_id,
                "label": label or "cli",
                "model": model or None,
                "host": self.host,
                "project_root": self.project_root,
                "version": self._read_version(),
            }
        )
        return self.session_path

    def _read_version(self) -> Optional[str]:
        try:
            version_file = os.path.join(self.project_root, "VERSION")
            if os.path.exists(version_file):
                with open(version_file, "r", encoding="utf-8") as f:
                    return f.read().strip() or None
        except Exception:
            pass
        # Fallback to package version from environment at runtime is omitted
        return None

    def _write_event(self, data: Dict[str, Any]) -> None:
        if self.privacy_mode or not self.session_path:
            return
        try:
            with open(self.session_path, "a", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(data, ensure_ascii=False))
                f.write("\n")
        except Exception:
            # Silently ignore file I/O errors for resilience
            pass

    def record_interaction(
        self,
        prompt: str,
        output: Optional[str],
        model: str,
        success: bool,
        error: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.privacy_mode or not self.session_path:
            return
        event = {
            "type": "interaction",
            "timestamp": datetime.utcnow().isoformat(),
            "model": model,
            "prompt": prompt,
            "output": output or "",
            "output_len": len(output or ""),
            "success": bool(success),
            "error": error or None,
        }
        if extra and isinstance(extra, dict):
            try:
                # Shallow merge with precedence to event keys
                merged = {**extra, **event}
                event = merged
            except Exception:
                pass
        self._write_event(event)

    def end(self, status: str = "completed") -> None:
        if self.privacy_mode or not self.session_path:
            return
        self._write_event(
            {
                "type": "session_end",
                "timestamp": datetime.utcnow().isoformat(),
                "id": self.session_id,
                "status": status,
            }
        )

