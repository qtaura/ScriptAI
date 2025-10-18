from __future__ import annotations

from typing import Dict, List, Optional, Any
import os
from collections import deque


def _env_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


class ContextManager:
    """
    In-memory conversational context manager.

    - Keeps a rolling window of recent messages per context key
    - Summarizes older history into a compact string when thresholds are exceeded
    - Composes a final prompt that includes summary + recent messages + current input

    Context key strategy (in order):
    - Explicit conversation_id (header `X-Conversation-Id` or JSON field)
    - Authenticated user id (`g.user_id`) when available
    - Client IP address

    Settings (env overrides):
    - CONTEXT_ENABLED: enable/disable context management (default: true)
    - CONTEXT_MAX_MESSAGES: keep this many recent messages (default: 10)
    - CONTEXT_SUMMARIZE_AFTER: summarize when messages exceed this count (default: 20)
    - CONTEXT_MAX_SUMMARY_CHARS: cap summary length (default: 2000)
    """

    def __init__(
        self,
        *,
        enabled: Optional[bool] = None,
        max_messages: int = 10,
        summarize_after: int = 20,
        max_summary_chars: int = 2000,
    ) -> None:
        self.enabled = (
            _env_bool("CONTEXT_ENABLED", True) if enabled is None else bool(enabled)
        )
        try:
            self.max_messages = int(
                os.getenv("CONTEXT_MAX_MESSAGES", str(max_messages))
            )
        except Exception:
            self.max_messages = max_messages
        try:
            self.summarize_after = int(
                os.getenv("CONTEXT_SUMMARIZE_AFTER", str(summarize_after))
            )
        except Exception:
            self.summarize_after = summarize_after
        try:
            self.max_summary_chars = int(
                os.getenv("CONTEXT_MAX_SUMMARY_CHARS", str(max_summary_chars))
            )
        except Exception:
            self.max_summary_chars = max_summary_chars

        # Per key state: { key: {"messages": deque[(role, content)], "summary": str} }
        self._store: Dict[str, Dict[str, Any]] = {}

    def _ensure_key(self, key: str) -> Dict[str, Any]:
        state = self._store.get(key)
        if state is None:
            state = {
                "messages": deque(
                    maxlen=max(1, max(self.max_messages, self.summarize_after))
                ),
                "summary": "",
            }
            self._store[key] = state
        return state

    def _maybe_summarize(self, key: str) -> None:
        st = self._ensure_key(key)
        msgs: deque = st["messages"]
        if len(msgs) < self.summarize_after:
            return
        # Summarize older half of messages, keep the newer half
        half = max(1, len(msgs) // 2)
        older: List[str] = []
        # Consume older messages from the left
        for _ in range(half):
            try:
                role, text = msgs.popleft()
            except IndexError:
                break
            older.append(f"[{role}] {text}")
        # Create/append summary
        addition = self._simple_summarize(older)
        st["summary"] = st.get("summary") or ""
        if st["summary"]:
            st["summary"] += "\n"
        st["summary"] += addition
        # Cap summary length
        if len(st["summary"]) > self.max_summary_chars:
            st["summary"] = st["summary"][: self.max_summary_chars] + "\n…"
        # Enforce recent message window after summarization
        while len(msgs) > self.max_messages:
            try:
                msgs.popleft()
            except IndexError:
                break

    def add_message(self, key: str, role: str, content: str) -> None:
        if not self.enabled:
            return
        st = self._ensure_key(key)
        # Normalize role
        r = role if role in ("user", "assistant", "system") else "user"
        # Trim overly long content for storage safety
        safe = content.strip()
        if len(safe) > 5000:
            safe = safe[:5000] + "\n…"
        st["messages"].append((r, safe))
        # Summarize if necessary when message count exceeds threshold
        self._maybe_summarize(key)

    @staticmethod
    def _simple_summarize(lines: List[str]) -> str:
        """
        Lightweight on-device summarizer:
        - Extract first sentence or first ~140 chars of each line
        - Join with bullets
        """
        bullets: List[str] = []
        for ln in lines:
            s = ln.replace("\n", " ")
            # Find sentence end
            cut = max(s.find(". "), s.find("? "), s.find("! "))
            if cut == -1 or cut < 40:
                cut = 140
            snippet = s[:cut].strip()
            if len(snippet) > 140:
                snippet = snippet[:140] + "…"
            bullets.append(f"- {snippet}")
        return "Previous context summary:\n" + "\n".join(bullets)

    def compose_prompt(self, key: str, current_input: str) -> str:
        if not self.enabled:
            return current_input
        st = self._ensure_key(key)
        # Build a compact prefix from summary + last few messages
        parts: List[str] = []
        if st.get("summary"):
            parts.append(st["summary"])
        if st["messages"]:
            # Include recent messages as brief quotes
            recent = list(st["messages"])[-self.max_messages :]
            quotes = []
            for role, text in recent:
                snippet = text[:200].replace("\n", " ")
                quotes.append(f"[{role}] {snippet}")
            if quotes:
                parts.append("Recent exchanges:\n" + "\n".join(quotes))
        parts.append("Current task:\n" + current_input)
        composed = "\n\n".join(parts)
        # Keep composed under a reasonable length
        if len(composed) > 8000:
            composed = composed[-8000:]
        return composed

    def inspect(self, key: str) -> Dict[str, Any]:
        """Return debug info for a given key (safe for exposure when debug=1)."""
        st = self._ensure_key(key)
        return {
            "key": key,
            "enabled": self.enabled,
            "summary_chars": len(st.get("summary") or ""),
            "messages_count": len(st["messages"]),
            "max_messages": self.max_messages,
            "summarize_after": self.summarize_after,
            "summary_preview": (st.get("summary") or "")[:200],
        }

    def get_stats(self, key: str) -> Dict[str, Any]:
        """
        Analytics-friendly stats for a given context key.
        Returns:
            - messages_count: number of messages currently kept for the key
            - content_chars: total chars across kept messages + summary
        """
        st = self._ensure_key(key)
        msgs: deque = st["messages"]
        total_chars = len(st.get("summary") or "")
        for _, text in list(msgs):
            try:
                total_chars += len(text or "")
            except Exception:
                pass
        return {
            "messages_count": len(msgs),
            "content_chars": total_chars,
        }


__all__ = ["ContextManager"]