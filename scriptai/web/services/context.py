from __future__ import annotations

import threading
from collections import deque
from typing import Any, Deque, Dict, List, Optional

from scriptai.web.services.registry import monitoring_manager


class ContextManager:
    def __init__(self, max_messages_per_context: int = 100, max_chars_per_context: int = 10000):
        self._store: Dict[str, Deque[Dict[str, Any]]] = {}
        self._locks: Dict[str, threading.Lock] = {}
        self.max_messages = max_messages_per_context
        self.max_chars = max_chars_per_context

    def _get_lock(self, key: str) -> threading.Lock:
        if key not in self._locks:
            self._locks[key] = threading.Lock()
        return self._locks[key]

    def _get_context(self, key: str) -> Deque[Dict[str, Any]]:
        if key not in self._store:
            self._store[key] = deque()
        return self._store[key]

    def add_message(self, key: str, role: str, content: str) -> None:
        lock = self._get_lock(key)
        with lock:
            context = self._get_context(key)
            context.append({"role": role, "content": content})
            # Enforce max messages
            while len(context) > self.max_messages:
                context.popleft()
            # Enforce max total characters
            total_chars = sum(len(m.get("content", "")) for m in context)
            while total_chars > self.max_chars and len(context) > 1:
                context.popleft()
                total_chars = sum(len(m.get("content", "")) for m in context)

    def get_context(self, key: str) -> List[Dict[str, Any]]:
        lock = self._get_lock(key)
        with lock:
            return list(self._get_context(key))

    def clear_context(self, key: str) -> None:
        lock = self._get_lock(key)
        with lock:
            if key in self._store:
                self._store[key].clear()

    def get_stats(self, key: str) -> Dict[str, Any]:
        lock = self._get_lock(key)
        with lock:
            msgs = self._get_context(key)
            total_chars = sum(len(m.get("content", "")) for m in msgs)
            return {
                "messages_count": len(msgs),
                "content_chars": total_chars,
            }


__all__ = ["ContextManager"]