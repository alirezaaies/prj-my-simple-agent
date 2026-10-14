"""A temporary checklist for one user request, separate from personal tasks."""


class WorkPlan:
    def __init__(self, files):
        self.files = files
        self.reset()

    def reset(self):
        self.steps = []
        self.required_files = []
        self.completed = set()
        self.finished = False
        self.summary = ""
        self.pause_reason = ""

    @property
    def active(self):
        return bool(self.steps)

    def plan(self, steps, files):
        steps = [step.strip() for step in steps]
        files = list(dict.fromkeys(name.strip() for name in files))
        if not 1 <= len(steps) <= 30 or any(not s or len(s) > 300 for s in steps):
            raise ValueError("Plan must contain 1-30 short, non-empty steps.")
        for name in files:
            self.files.path(name)
        if self.active:
            # A repair may extend a plan, but cannot erase unfinished obligations.
            if steps[:len(self.steps)] != self.steps or not set(self.required_files) <= set(files):
                raise ValueError("An active plan may be extended, not shortened or replaced.")
        self.steps, self.required_files = steps, files
        return "Work plan recorded.\n" + self.status()

    def complete(self, step_id):
        if not self.active or step_id > len(self.steps):
            raise ValueError("Step ID is not in the current work plan.")
        self.completed.add(step_id)
        return f"Step {step_id} recorded as completed.\n" + self.status()

    def allows_file(self, name):
        if not isinstance(name, str):
            return False
        try:
            path = self.files.path(name)
            return any(path == self.files.path(required) for required in self.required_files)
        except (OSError, ValueError):
            return False

    def finish(self, summary):
        if not self.active:
            raise ValueError("Record a work plan before finishing a tool-driven task.")
        pending = [str(i) for i in range(1, len(self.steps) + 1) if i not in self.completed]
        if pending:
            raise ValueError("Unfinished steps: " + ", ".join(pending) + ". Continue the task.")
        missing = self.missing_files()
        if missing:
            raise ValueError("Required files missing, empty or inaccessible: " + ", ".join(missing))
        self.finished, self.summary = True, summary.strip()
        return "Work completed. Required file existence/size checks passed."

    def missing_files(self):
        missing = []
        for name in self.required_files:
            try:
                path = self.files.path(name)
                valid = path.is_file() and path.stat().st_size > 0
            except (OSError, ValueError):
                valid = False
            if not valid:
                missing.append(name)
        return missing

    def pause(self, reason):
        self.pause_reason = reason.strip()
        return "Work paused: " + self.pause_reason

    def status(self):
        if not self.active:
            return "No work plan recorded yet."
        missing = self.missing_files()
        return "\n".join(f"{i}. [{'done' if i in self.completed else 'pending'}] {step}"
                         for i, step in enumerate(self.steps, 1)) + (
            "\nRequired files: " + ", ".join(self.required_files) if self.required_files else "") + (
            "\nMissing/empty/inaccessible files: " + ", ".join(missing) if missing else "")
