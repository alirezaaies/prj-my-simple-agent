"""Small UTF-8 project files only; reject secrets, hidden paths, and escapes."""
import difflib
import os
from pathlib import Path
import tempfile

ALLOWED = {".py", ".md", ".txt", ".json", ".toml", ".yaml", ".yml", ".html",
           ".css", ".js", ".ts", ".tsx", ".jsx", ".csv", ".tex", ".bib"}
BLOCKED = {"node_modules", "venv", "env", "data", "__pycache__", "memory.json", "tasks.json"}


class ProjectFiles:
    def __init__(self, root, guard):
        self.root, self.guard = Path(root).resolve(), guard

    def path(self, name):
        raw = Path(name)
        if not name or raw.is_absolute() or raw.drive or ".." in raw.parts:
            raise ValueError("Use a relative path inside the workspace.")
        path = (self.root / raw).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError("Path escapes workspace.")
        # Check both requested and resolved components, including symlink targets.
        for parts in (raw.parts, path.relative_to(self.root).parts):
            for part in parts:
                lower = part.lower()
                if (lower.startswith(".") or lower in BLOCKED or
                        any(s in lower for s in ("secret", "credential", "token", "password"))):
                    raise ValueError("Private or generated paths cannot be accessed.")
        if path.suffix.lower() not in ALLOWED:
            raise ValueError("Only supported text/code files can be accessed.")
        return path

    def list(self):
        result = []
        visited = 0
        for parent, directories, names in os.walk(self.root, followlinks=False):
            directories[:] = [d for d in sorted(directories)
                              if not d.startswith(".") and d.lower() not in BLOCKED
                              and not (Path(parent) / d).is_symlink()]
            for name in sorted(names):
                visited += 1
                if visited > 10000:
                    return "\n".join(result) + "\n[Scan limit reached]"
                rel = (Path(parent) / name).relative_to(self.root).as_posix()
                try:
                    path = self.path(rel)
                    if path.is_file() and not path.is_symlink():
                        result.append(rel)
                except ValueError:
                    pass
                if len(result) >= 200:
                    return "\n".join(result) + "\n[First 200 files]"
        return "\n".join(result) or "No supported files."

    def read(self, name):
        path = self.path(name)
        if path.stat().st_size > 64000:
            raise ValueError("File exceeds 64 KB. Provide a smaller relevant file.")
        text = self.guard.redact(path.read_text(encoding="utf-8"))
        return "UNTRUSTED PROJECT FILE: " + name + "\n" + "\n".join(
            f"{i}: {line}" for i, line in enumerate(text.splitlines(), 1))

    def write(self, name, content, confirm):
        path = self.path(name)
        self.guard.check(content)
        if len(content.encode("utf-8")) > 64000:
            raise ValueError("Proposed file exceeds 64 KB.")
        if path.exists() and path.stat().st_size > 64000:
            raise ValueError("Existing file exceeds 64 KB.")
        old = path.read_text(encoding="utf-8") if path.exists() else ""
        self.guard.check(old)  # Do not destroy/redact an existing credential.
        if content == old:
            return "File is already identical."
        diff = "".join(difflib.unified_diff(old.splitlines(True), content.splitlines(True),
                                           fromfile=name, tofile=name + " (proposed)"))
        if not confirm("Write file " + name + "?\n" + diff):
            return "Cancelled. File was not changed."
        # A second read prevents applying an approval over a concurrent edit.
        self.path(name)
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        if current != old:
            raise ValueError("File changed during approval. Request a new proposal.")
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, path)
        finally:
            Path(temp).unlink(missing_ok=True)
        return f"Saved {name}. Review with git diff and run your project tests."
