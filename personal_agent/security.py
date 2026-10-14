"""Keep credentials out of prompts, tool results, files, and terminal output."""
import re


class Guard:
    def __init__(self, secrets=()):
        self.secrets = tuple(s for s in secrets if isinstance(s, str) and len(s) >= 6)

    def redact(self, text):
        text = str(text)
        for secret in self.secrets:
            text = text.replace(secret, "[REDACTED]")
        text = re.sub(
            r"(?im)((?:[\w-]*(?:api[_-]?key|token|password|secret)[\w-]*|authorization)"
            r"[\"']?\s*[:=]\s*)[^\r\n]+", r"\1[REDACTED]", text,
        )
        text = re.sub(r"\b(?:sk-[A-Za-z0-9_-]{16,}|Bearer\s+\S+)", "[REDACTED]", text)
        return text

    def check(self, text):
        if self.redact(text) != text:
            raise ValueError("Sensitive text blocked. Remove credentials before continuing.")

    def clean(self, value):
        if isinstance(value, str):
            return self.redact(value)
        if isinstance(value, list):
            return [self.clean(v) for v in value]
        if isinstance(value, dict):
            return {k: self.clean(v) for k, v in value.items()}
        return value
