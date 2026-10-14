"""Validated JSON state with atomic replacement. Never reset corrupt data silently."""
from contextlib import contextmanager
from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile


class StateError(ValueError):
    pass


class Store:
    def __init__(self, directory, guard):
        self.directory = Path(directory)
        self.guard = guard

    @contextmanager
    def lock(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        lock = self.directory / ".lock"
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise StateError("State is busy. Close the other agent; see docs for stale locks.") from None
        try:
            os.close(fd)
            yield
        finally:
            lock.unlink(missing_ok=True)

    def load(self, kind):
        path = self.directory / f"{kind}.json"
        if not path.exists():
            return {"facts": []} if kind == "memory" else {"tasks": [], "next_id": 1}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            self.validate(kind, data)
            return data
        except (OSError, ValueError, TypeError, KeyError):
            raise StateError(f"Invalid {kind}.json. Restore a backup; original was not changed.") from None

    def validate(self, kind, data):
        if not isinstance(data, dict):
            raise StateError("State must be an object.")
        if kind == "memory":
            facts = data["facts"]
            if not isinstance(facts, list) or not all(
                isinstance(f, str) and 0 < len(f) <= 1000 for f in facts
            ):
                raise StateError("Invalid memory schema.")
        else:
            tasks = data["tasks"]
            if not isinstance(tasks, list):
                raise StateError("Invalid tasks schema.")
            ids = []
            for t in tasks:
                if (not isinstance(t, dict) or type(t.get("id")) is not int
                        or t["id"] < 1 or not isinstance(t.get("title"), str)
                        or not 0 < len(t["title"]) <= 300
                        or type(t.get("completed")) is not bool):
                    raise StateError("Invalid task.")
                ids.append(t["id"])
            if len(ids) != len(set(ids)):
                raise StateError("Duplicate task ID.")
            data.setdefault("next_id", max(ids, default=0) + 1)
            if type(data["next_id"]) is not int or data["next_id"] <= max(ids, default=0):
                raise StateError("Invalid next_id.")

    def save(self, kind, data):
        self.validate(kind, data)
        text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        self.guard.check(text)
        self.directory.mkdir(parents=True, exist_ok=True)
        target = self.directory / f"{kind}.json"
        fd, name = tempfile.mkstemp(dir=self.directory, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(text)
                stream.flush()
                os.fsync(stream.fileno())
            # Previous valid state remains available locally.
            if target.exists():
                old = self.load(kind)
                backup = json.dumps(old, ensure_ascii=False, indent=2)
                self.guard.check(backup)
                target.with_suffix(".json.bak").write_text(backup, encoding="utf-8")
            os.replace(name, target)
        finally:
            Path(name).unlink(missing_ok=True)

    def migrate(self, root):
        """Copy old root JSON files once, preserving original files."""
        with self.lock():
            for kind in ("memory", "tasks"):
                old = root / f"{kind}.json"
                if old.exists() and not (self.directory / old.name).exists():
                    try:
                        data = json.loads(old.read_text(encoding="utf-8"))
                        self.save(kind, data)
                    except (OSError, ValueError, TypeError, KeyError):
                        raise StateError(f"Cannot migrate {kind}.json. Original preserved.") from None

    def change(self, kind, operation):
        with self.lock():
            data = deepcopy(self.load(kind))
            result = operation(data)
            self.save(kind, data)
            return result
