"""Load .env relative to the project, never relative to the terminal directory."""
from dataclasses import dataclass, field
import os
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import dotenv_values

from .security import Guard

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Config:
    root: Path
    workspace: Path
    model: str
    base_url: str
    api_key: str = field(repr=False)
    guard: Guard = field(repr=False)
    timeout: float = 60
    max_rounds: int = 30
    history_turns: int = 10
    max_output_tokens: int = 8192

    @classmethod
    def load(cls, root=ROOT, workspace=None):
        values = {**dotenv_values(root / ".env"), **os.environ}
        base = values.get("OLLAMA_BASE_URL", "https://ollama.com/v1").rstrip("/")
        parsed = urlsplit(base)
        cloud = base == "https://ollama.com/v1"
        local = (parsed.scheme == "http" and parsed.hostname in
                 {"localhost", "127.0.0.1", "::1"} and parsed.path == "/v1"
                 and not parsed.username and not parsed.password and not parsed.query
                 and not parsed.fragment)
        if not cloud and not local:
            raise ValueError("OLLAMA_BASE_URL must be Ollama cloud or a loopback /v1 server.")
        key = values.get("OLLAMA_API_KEY") or values.get("OLLAMA_FREE_API_KEY") or ""
        if cloud and not key:
            raise ValueError("Set OLLAMA_API_KEY (or OLLAMA_FREE_API_KEY) in .env.")
        timeout = float(values.get("AGENT_TIMEOUT", "60"))
        if not 1 <= timeout <= 300:
            raise ValueError("AGENT_TIMEOUT must be between 1 and 300 seconds.")
        rounds = int(values.get("AGENT_MAX_ROUNDS", "30"))
        output_tokens = int(values.get("AGENT_MAX_OUTPUT_TOKENS", "8192"))
        if not 1 <= rounds <= 100:
            raise ValueError("AGENT_MAX_ROUNDS must be between 1 and 100.")
        if not 256 <= output_tokens <= 32768:
            raise ValueError("AGENT_MAX_OUTPUT_TOKENS must be between 256 and 32768.")
        secrets = [v for k, v in values.items() if any(
            s in k.lower() for s in ("key", "token", "password", "secret")) and v]
        return cls(root.resolve(), Path(workspace or root).resolve(),
                   values.get("OLLAMA_MODEL") or "gemma4:31b", base,
                   key if cloud else "ollama", Guard(secrets), timeout,
                   max_rounds=rounds, max_output_tokens=output_tokens)
