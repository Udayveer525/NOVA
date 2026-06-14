"""Central configuration for NOVA."""

import os

# Gemini model used across all agents and grounding tools
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Per-key daily request limit (free tier)
RPD_LIMIT = int(os.getenv("RPD_LIMIT", "20"))

# Max API keys to load from environment
MAX_API_KEYS = int(os.getenv("MAX_API_KEYS", "10"))

# Agent execution limits
MAX_AGENT_ITERATIONS = int(os.getenv("MAX_AGENT_ITERATIONS", "15"))
MEMORY_CONTEXT_LIMIT = int(os.getenv("MEMORY_CONTEXT_LIMIT", "20"))

# Database
DB_PATH = os.getenv("NOVA_DB_PATH", "nova_memory.db")
