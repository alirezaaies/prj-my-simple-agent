"""One registry defines both model schemas and runtime validation."""
import json

from .files import ProjectFiles
from .web import web_search, read_webpage
from .work import WorkPlan


class Toolbox:
    def __init__(self, config, store, confirm=lambda preview: False, memory=True):
        self.config, self.store, self.confirm = config, store, confirm
        self.files = ProjectFiles(config.workspace, config.guard)
        self.work = WorkPlan(self.files)
        self.registry = {}
        self.add("plan_work", "Plan the FULL user task before writing files. List every step and ALL "
                 "required output files (relative paths). This is temporary, not saved personal tasks.",
                 {"steps": "string_list", "files": "string_list"}, self.work.plan)
        self.add("complete_step", "Record a plan step complete only after its actions succeeded.",
                 {"step_id": "integer"}, self.work.complete)
        self.add("finish_work", "Finish only after ALL requested work and review are done. Checks pending "
                 "steps and required file existence. Include outcomes, limits and usage in the summary.",
                 {"summary": "string"}, self.work.finish)
        self.add("pause_work", "Pause only for a real blocker, missing essential user information or "
                 "declined change. Explain what remains and what is needed; do not label it finished.",
                 {"reason": "string"}, self.work.pause)
        self.add("web_search", "Search current information; results are snippets, not proof.",
                 {"query": "string"}, web_search)
        self.add("read_webpage", "Read a public HTTPS page. Cite its actual content and URL.",
                 {"url": "string"}, read_webpage)
        self.add("list_files", "List accessible code/text files in the workspace.", {}, self.files.list)
        self.add("read_file", "Read a workspace file, with line numbers and secret redaction.",
                 {"path": "string"}, lambda path: self.files.read(path))
        self.add("write_file", "Propose a complete UTF-8 file. A diff needs user approval to save.",
                 {"path": "string", "content": "string"},
                 lambda path, content: self.files.write(path, content, self.confirm))
        if memory:
            self.add("show_memory", "Show explicitly saved user facts.", {}, self.show_memory)
            self.add("remember_fact", "Save a fact only when user explicitly asks. No secrets.",
                     {"fact": "string"}, self.remember_fact, True)
            self.add("update_fact", "Replace an exact saved fact after an explicit correction.",
                     {"old_fact": "string", "new_fact": "string"}, self.update_fact, True)
            self.add("forget_fact", "Remove an exact saved fact when explicitly requested.",
                     {"fact": "string"}, self.forget_fact, True)
            self.add("create_task", "Create a task when user explicitly requests it.",
                     {"title": "string"}, self.create_task, True)
            self.add("list_tasks", "List all tasks with ID and completion status.", {}, self.list_tasks)
            self.add("complete_task", "Mark an existing task completed by ID.",
                     {"task_id": "integer"}, self.complete_task, True)
            self.add("delete_task", "Delete an existing task when explicitly requested.",
                     {"task_id": "integer"}, self.delete_task, True)

    def add(self, name, description, fields, function, approval=False):
        self.registry[name] = (description, fields, function, approval)

    @property
    def schemas(self):
        return [{"type": "function", "function": {
            "name": name, "description": spec[0], "parameters": {
                "type": "object", "properties": {k: ({"type": "array", "items": {"type": "string"},
                    "maxItems": 30} if v == "string_list" else {"type": v}) for k, v in spec[1].items()},
                "required": list(spec[1]), "additionalProperties": False}}}
                for name, spec in self.registry.items()]

    def execute(self, name, arguments, local=False):
        try:
            if name not in self.registry:
                raise ValueError("Tool is not permitted.")
            _, fields, fn, approval = self.registry[name]
            if not isinstance(arguments, dict) or set(arguments) != set(fields):
                raise ValueError("Unexpected or missing tool arguments.")
            for key, expected in fields.items():
                value = arguments[key]
                if expected == "string_list":
                    if (not isinstance(value, list) or len(value) > 30 or any(
                        not isinstance(item, str) or not item.strip() or len(item) > 500 for item in value
                    )):
                        raise ValueError("Expected an array of up to 30 short, non-empty strings.")
                elif expected == "integer":
                    if type(value) is not int or value < 1:
                        raise ValueError("ID must be a positive integer.")
                elif not isinstance(value, str) or (key != "content" and not value.strip()):
                    raise ValueError("Expected non-empty text.")
                elif len(value) > (64000 if key == "content" else 12000 if key == "summary" else 2000):
                    raise ValueError("Tool argument too long.")
            self.config.guard.check(json.dumps(arguments, ensure_ascii=False))
            if approval and not local and not self.confirm(
                    f"{name}\n" + json.dumps(arguments, ensure_ascii=False, indent=2)):
                return "Cancelled. No change was made."
            return self.config.guard.redact(fn(**arguments))
        except (KeyboardInterrupt, EOFError):
            raise
        except ValueError as error:
            return "Error: " + self.config.guard.redact(error)
        except Exception:
            # Network libraries can include request URLs/headers in their exceptions.
            return "Error: Tool failed. No successful result confirmed. Check connection/file permissions."

    def show_memory(self):
        return "\n".join(self.store.load("memory")["facts"]) or "Memory is empty."

    def remember_fact(self, fact):
        fact = fact.strip()
        if len(fact) > 1000:
            raise ValueError("Fact exceeds 1000 characters.")
        def add(data):
            if fact.casefold() in {f.casefold() for f in data["facts"]}:
                return "Already saved."
            data["facts"].append(fact)
            return "Saved fact: " + fact
        return self.store.change("memory", add)

    def update_fact(self, old_fact, new_fact):
        if len(new_fact.strip()) > 1000:
            raise ValueError("Fact exceeds 1000 characters.")
        def update(data):
            facts = data["facts"]
            index = next((i for i, f in enumerate(facts) if f.casefold() == old_fact.strip().casefold()), None)
            if index is None:
                raise ValueError("Exact old fact not found.")
            if any(f.casefold() == new_fact.strip().casefold() for i, f in enumerate(facts) if i != index):
                raise ValueError("Replacement already exists.")
            facts[index] = new_fact.strip()
            return "Updated fact: " + new_fact.strip()
        return self.store.change("memory", update)

    def forget_fact(self, fact):
        def remove(data):
            old = len(data["facts"])
            data["facts"] = [f for f in data["facts"] if f.casefold() != fact.strip().casefold()]
            if len(data["facts"]) == old:
                raise ValueError("Exact fact not found.")
            return "Fact removed."
        return self.store.change("memory", remove)

    def create_task(self, title):
        title = title.strip()
        if len(title) > 300:
            raise ValueError("Task title exceeds 300 characters.")
        def add(data):
            number = data["next_id"]
            data["next_id"] += 1
            data["tasks"].append({"id": number, "title": title, "completed": False})
            return f"Created task #{number}: {title}"
        return self.store.change("tasks", add)

    def list_tasks(self):
        return "\n".join(f"#{t['id']} [{'done' if t['completed'] else 'pending'}] {t['title']}"
                         for t in self.store.load("tasks")["tasks"]) or "No tasks."

    def complete_task(self, task_id):
        def complete(data):
            task = next((t for t in data["tasks"] if t["id"] == task_id), None)
            if task is None:
                raise ValueError("Task not found.")
            task["completed"] = True
            return f"Completed task #{task_id}."
        return self.store.change("tasks", complete)

    def delete_task(self, task_id):
        def delete(data):
            tasks = data["tasks"]
            task = next((t for t in tasks if t["id"] == task_id), None)
            if task is None:
                raise ValueError("Task not found.")
            tasks.remove(task)
            return f"Deleted task #{task_id}."
        return self.store.change("tasks", delete)
