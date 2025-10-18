from __future__ import annotations

import threading
from collections import deque
from typing import Any, Deque, Dict, List


class ContextManager:
    def __init__(
        self,
        enabled: bool = True,
        max_messages: int = 100,
        summarize_after: int = 10,
        max_summary_chars: int = 5000,
        max_chars: int = 100000,
    ):
        # Feature switch
        self.enabled = enabled
        # How many recent messages to retain in the live context
        self.max_messages = max_messages
        # When the number of messages exceeds this threshold, begin summarizing
        self.summarize_after = summarize_after
        # Maximum size of the rolling summary buffer
        self.max_summary_chars = max_summary_chars
        # Hard cap on total characters retained across the live context
        self.max_chars = max_chars

        self._store: Dict[str, Deque[Dict[str, Any]]] = {}
        self._summaries: Dict[str, str] = {}
        self._locks: Dict[str, threading.Lock] = {}

    def _get_lock(self, key: str) -> threading.Lock:
        if key not in self._locks:
            self._locks[key] = threading.Lock()
        return self._locks[key]

    def _get_context(self, key: str) -> Deque[Dict[str, Any]]:
        if key not in self._store:
            self._store[key] = deque()
        return self._store[key]

    def _get_summary(self, key: str) -> str:
        return self._summaries.get(key, "")

    def _set_summary(self, key: str, text: str) -> None:
        # Keep only the last max_summary_chars to prioritize recent summaries
        if len(text) > self.max_summary_chars:
            text = text[-self.max_summary_chars :]
        self._summaries[key] = text

    def add_message(self, key: str, role: str, content: str) -> None:
        if not self.enabled:
            return
        lock = self._get_lock(key)
        with lock:
            ctx = self._get_context(key)
            ctx.append({"role": role, "content": content})

            # Enforce hard cap on total characters
            total_chars = sum(len(m.get("content", "")) for m in ctx) + len(
                self._get_summary(key)
            )
            while total_chars > self.max_chars and len(ctx) > 1:
                removed = ctx.popleft()
                self._append_to_summary(key, [removed])
                total_chars = sum(len(m.get("content", "")) for m in ctx) + len(
                    self._get_summary(key)
                )

            # Summarize older messages when over thresholds
            self._summarize_if_needed(key)

    def _append_to_summary(self, key: str, messages: List[Dict[str, Any]]) -> None:
        if not messages:
            return
        summary = self._get_summary(key)
        parts: List[str] = []
        for m in messages:
            role = m.get("role") or "unknown"
            content = m.get("content") or ""
            parts.append(f"{role.capitalize()}: {content}\n")
        new_summary = (
            summary + ("" if summary.endswith("\n") else "") + "".join(parts)
        ).strip()
        self._set_summary(key, new_summary)

    def _summarize_if_needed(self, key: str) -> None:
        ctx = self._get_context(key)
        # Summarize when exceeding either threshold; always cap to max_messages
        if len(ctx) > self.summarize_after or len(ctx) > self.max_messages:
            to_summarize = max(0, len(ctx) - self.max_messages)
            if to_summarize > 0:
                old_msgs: List[Dict[str, Any]] = []
                for _ in range(to_summarize):
                    old_msgs.append(ctx.popleft())
                self._append_to_summary(key, old_msgs)

    def compose_prompt(self, key: str, latest_prompt: str) -> str:
        """
        Compose a model-friendly prompt from rolling summary + recent messages + latest user input.
        """
        lock = self._get_lock(key)
        with lock:
            summary = self._get_summary(key)
            ctx = list(self._get_context(key))
        parts: List[str] = []
        if summary:
            parts.append(f"Conversation Summary:\n{summary}\n---\n")
        if ctx:
            for m in ctx:
                role = m.get("role") or "unknown"
                content = m.get("content") or ""
                parts.append(f"{role.capitalize()}: {content}\n")
        parts.append(f"User: {latest_prompt}\n")
        return "".join(parts)

    def inspect(self, key: str) -> Dict[str, Any]:
        """
        Return diagnostic information about the context for debugging.
        """
        lock = self._get_lock(key)
        with lock:
            ctx = self._get_context(key)
            summary = self._get_summary(key)
            content_chars = sum(len(m.get("content", "")) for m in ctx)
            info = {
                "messages_count": len(ctx),
                "summary_chars": len(summary),
                "summary_preview": summary[:160] if summary else "",
                "content_chars": content_chars,
            }
            return info

    def get_context(self, key: str) -> List[Dict[str, Any]]:
        lock = self._get_lock(key)
        with lock:
            return list(self._get_context(key))

    def clear_context(self, key: str) -> None:
        lock = self._get_lock(key)
        with lock:
            if key in self._store:
                self._store[key].clear()
            self._summaries.pop(key, None)

    def get_stats(self, key: str) -> Dict[str, Any]:
        """
        Basic stats for analytics: counts and a rough token estimate.
        """
        lock = self._get_lock(key)
        with lock:
            ctx = self._get_context(key)
            summary = self._get_summary(key)
            content_chars = sum(len(m.get("content", "")) for m in ctx)
            summary_chars = len(summary)
            # Crude token estimate: ~4 chars per token
            tokens_estimated = int(round((content_chars + summary_chars) / 4))
            return {
                "messages_count": len(ctx),
                "content_chars": content_chars,
                "summary_chars": summary_chars,
                "tokens_estimated": tokens_estimated,
            }


__all__ = ["ContextManager"]
