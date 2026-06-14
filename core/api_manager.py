"""API Manager - Multi-key rotation and Gemini client factory."""

import os
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI

from core.config import GEMINI_MODEL, MAX_API_KEYS, RPD_LIMIT


class APIManager:
    """Manages Gemini API keys with rotation and shared request cycles."""

    def __init__(self):
        self.api_keys = self._load_keys()
        self.current_key_index = 0
        self._active_key = None  # Reserved key for current agent execution cycle

        print(f"🔑 Loaded {len(self.api_keys)} API key(s)")
        print(f"📊 Total daily capacity: {len(self.api_keys) * RPD_LIMIT} requests")
        print(f"🤖 Model: {GEMINI_MODEL}")

    def _load_keys(self) -> list[dict]:
        keys = []
        for i in range(1, MAX_API_KEYS + 1):
            key = os.getenv(f"GOOGLE_API_KEY_{i}")
            if key:
                keys.append(self._make_key_entry(key, f"Key {i}"))

        if not keys:
            single_key = os.getenv("GOOGLE_API_KEY")
            if single_key:
                keys.append(self._make_key_entry(single_key, "Key 1"))

        if not keys:
            raise ValueError(
                "No API keys found. Set GOOGLE_API_KEY or GOOGLE_API_KEY_1 in your .env file."
            )

        return keys

    @staticmethod
    def _make_key_entry(key: str, name: str) -> dict:
        return {
            "key": key,
            "requests_today": 0,
            "last_reset": datetime.now(),
            "name": name,
        }

    def begin_request_cycle(self) -> dict | None:
        """Reserve one key for an agent execution (LLM + tools share it)."""
        if self._active_key is not None:
            return self._active_key

        key_info = self._acquire_key()
        if key_info:
            self._active_key = key_info
        return key_info

    def end_request_cycle(self):
        """Release the reserved key after agent execution completes."""
        self._active_key = None

    def get_active_key(self) -> dict | None:
        """Get the key reserved for the current request cycle."""
        return self._active_key

    def get_llm(self, temperature: float = 0.7) -> ChatGoogleGenerativeAI:
        """Get a LangChain LLM using the active or next available key."""
        key_info = self._active_key or self._acquire_key()
        if not key_info:
            raise RuntimeError("All API keys exhausted for today. Please try again tomorrow.")

        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            temperature=temperature,
            google_api_key=key_info["key"],
        )

    def get_genai_client(self):
        """Get a google.genai Client using the active or next available key."""
        key_info = self._active_key or self._acquire_key()
        if not key_info:
            raise RuntimeError("All API keys exhausted for today. Please try again tomorrow.")

        from google import genai

        return genai.Client(api_key=key_info["key"])

    def _acquire_key(self) -> dict | None:
        """Find and consume quota from an available API key."""
        now = datetime.now()

        for key_info in self.api_keys:
            if now.date() > key_info["last_reset"].date():
                key_info["requests_today"] = 0
                key_info["last_reset"] = now

        for i in range(len(self.api_keys)):
            idx = (self.current_key_index + i) % len(self.api_keys)
            key_info = self.api_keys[idx]

            if key_info["requests_today"] < RPD_LIMIT:
                key_info["requests_today"] += 1
                self.current_key_index = idx

                if key_info["requests_today"] % 5 == 0:
                    print(
                        f"📊 {key_info['name']}: "
                        f"{key_info['requests_today']}/{RPD_LIMIT} used"
                    )

                return key_info

        return None

    def mark_current_key_exhausted(self):
        """Mark the active key as fully used (e.g. after a 429)."""
        if self._active_key:
            self._active_key["requests_today"] = RPD_LIMIT
        elif self.api_keys:
            self.api_keys[self.current_key_index]["requests_today"] = RPD_LIMIT

    def get_usage_stats(self) -> str:
        """Return formatted usage statistics."""
        total_used = sum(k["requests_today"] for k in self.api_keys)
        total_limit = len(self.api_keys) * RPD_LIMIT

        lines = ["📊 API Usage:"]
        for key_info in self.api_keys:
            lines.append(
                f"   {key_info['name']}: "
                f"{key_info['requests_today']}/{RPD_LIMIT}"
            )

        pct = (total_used / total_limit * 100) if total_limit else 0
        lines.append(f"   Total: {total_used}/{total_limit} ({pct:.1f}%)")
        lines.append(f"   Model: {GEMINI_MODEL}")
        return "\n".join(lines)
