"""Deterministic regression tests. No real credentials, network, or user state."""
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from personal_agent.agent import Agent
from personal_agent.cli import local_command
from personal_agent.config import Config
from personal_agent.files import ProjectFiles
from personal_agent.security import Guard
from personal_agent.storage import Store, StateError
from personal_agent.tools import Toolbox
from personal_agent.web import public_target, read_webpage


def message(content="answer", calls=None, finish_reason="stop"):
    data = {"role": "assistant", "content": content}
    if calls:
        data["tool_calls"] = [{"id": c.id, "type": "function", "function": {
            "name": c.function.name, "arguments": c.function.arguments}} for c in calls]
    return SimpleNamespace(content=content, tool_calls=calls, finish_reason=finish_reason,
                           model_dump=lambda **kw: data)


def call(name, args, number="call_1"):
    return SimpleNamespace(id=number, function=SimpleNamespace(name=name, arguments=args))


class FakeClient:
    def __init__(self, messages):
        self.responses = iter(messages)
        self.requests = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        self.requests.append(kwargs)
        result = next(self.responses)
        if isinstance(result, Exception):
            raise result
        return SimpleNamespace(choices=[SimpleNamespace(message=result, finish_reason=result.finish_reason)])


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.guard = Guard(["fake-sensitive-value-12345"])
        self.config = Config(self.root, self.root, "test", "https://ollama.com/v1",
                             "fake-sensitive-value-12345", self.guard)
        self.store = Store(self.root / "data", self.guard)
        self.tools = Toolbox(self.config, self.store, lambda preview: True)

    def run_tool(self, name, **args):
        return self.tools.execute(name, args, local=True)

    def test_config_alias_and_not_repr(self):
        (self.root / ".env").write_text("OLLAMA_FREE_API_KEY=fake-sensitive-value-12345\n")
        with patch.dict("os.environ", {}, clear=True):
            c = Config.load(self.root)
        self.assertEqual(c.api_key, "fake-sensitive-value-12345")
        self.assertNotIn(c.api_key, repr(c))

    def test_config_local_without_key(self):
        (self.root / ".env").write_text("OLLAMA_BASE_URL=http://localhost:11434/v1\n")
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(Config.load(self.root).api_key, "ollama")

    def test_config_arbitrary_server_rejected(self):
        (self.root / ".env").write_text("OLLAMA_BASE_URL=https://example.com/v1\n")
        with patch.dict("os.environ", {}, clear=True), self.assertRaises(ValueError):
            Config.load(self.root)

    def test_local_never_receives_cloud_key(self):
        (self.root / ".env").write_text("OLLAMA_API_KEY=fake-sensitive-value-12345\n"
                                       "OLLAMA_BASE_URL=http://127.0.0.1:11434/v1\n")
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(Config.load(self.root).api_key, "ollama")

    def test_resolved_path_escape_logic(self):
        files = self.tools.files
        with patch.object(Path, "resolve", return_value=Path(self.root.anchor) / "outside.py"):
            with self.assertRaises(ValueError):
                files.path("inside.py")

    def test_failed_api_preserves_confirmed_tool(self):
        from openai import APIConnectionError
        fake = FakeClient([message(None, [call("create_task", '{"title":"already saved"}')]),
                           APIConnectionError(request=None), message("followup")])
        agent = Agent(self.config, self.tools, fake)
        self.assertIn("Cannot connect", agent.ask("create task"))
        self.assertEqual(self.store.load("tasks")["tasks"][0]["title"], "already saved")
        self.assertEqual(agent.ask("what happened?"), "followup")
        self.assertTrue(any(m["role"] == "tool" for m in fake.requests[-1]["messages"]))

    def test_guard_known_and_labeled(self):
        for text in ("fake-sensitive-value-12345", '"api_key": "unknown-value"', "password=unknown"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.guard.check(text)

    def test_memory_duplicate_and_update(self):
        self.run_tool("remember_fact", fact="I learn Python")
        self.run_tool("remember_fact", fact="i learn python")
        self.assertEqual(len(self.store.load("memory")["facts"]), 1)
        self.run_tool("update_fact", old_fact="I learn Python", new_fact="I learn Rust")
        self.assertEqual(self.store.load("memory")["facts"], ["I learn Rust"])

    def test_memory_secret_not_saved(self):
        self.assertIn("Error", self.run_tool("remember_fact", fact="fake-sensitive-value-12345"))
        self.assertEqual(self.store.load("memory")["facts"], [])

    def test_memory_forget(self):
        self.run_tool("remember_fact", fact="a")
        self.run_tool("forget_fact", fact="a")
        self.assertEqual(self.store.load("memory")["facts"], [])

    def test_missing_fact_does_not_overwrite(self):
        self.run_tool("remember_fact", fact="a")
        self.assertIn("Error", self.run_tool("update_fact", old_fact="b", new_fact="c"))
        self.assertEqual(self.store.load("memory")["facts"], ["a"])

    def test_task_lifecycle_monotonic_ids(self):
        self.run_tool("create_task", title="one")
        self.run_tool("complete_task", task_id=1)
        self.assertTrue(self.store.load("tasks")["tasks"][0]["completed"])
        self.run_tool("delete_task", task_id=1)
        self.run_tool("create_task", title="two")
        self.assertEqual(self.store.load("tasks")["tasks"][0]["id"], 2)

    def test_tool_invalid_types_and_extra(self):
        for name, args in [("complete_task", {"task_id": True}), ("create_task", {"title": 9}),
                           ("web_search", {"query": "x", "extra": "x"}), ("show_memory", {"x": 1}),
                           ("not_allowed", {}), ("complete_task", {"task_id": -1})]:
            self.assertIn("Error", self.tools.execute(name, args))

    def test_model_mutation_cancelled(self):
        t = Toolbox(self.config, self.store)
        self.assertIn("Cancelled", t.execute("create_task", {"title": "no"}))
        self.assertEqual(self.store.load("tasks")["tasks"], [])

    def test_backup(self):
        self.run_tool("remember_fact", fact="a")
        self.run_tool("remember_fact", fact="b")
        previous = json.loads((self.store.directory / "memory.json.bak").read_text())
        self.assertEqual(previous["facts"], ["a"])

    def test_corruption_preserved(self):
        self.store.directory.mkdir()
        path = self.store.directory / "memory.json"
        path.write_text("{corrupt")
        self.assertIn("Invalid", self.run_tool("remember_fact", fact="x"))
        self.assertEqual(path.read_text(), "{corrupt")

    def test_invalid_task_schema(self):
        for data in ({"tasks": [{"id": True}]}, {"tasks": [], "next_id": 0}):
            with self.assertRaises((StateError, KeyError)):
                self.store.validate("tasks", data)

    def test_lock_rejects_concurrent_write(self):
        with self.store.lock():
            self.assertIn("busy", self.run_tool("create_task", title="x"))
        self.assertFalse((self.store.directory / ".lock").exists())

    def test_migration_original_preserved(self):
        original = '{"facts": ["learn Python"]}'
        (self.root / "memory.json").write_text(original)
        self.store.migrate(self.root)
        self.store.migrate(self.root)
        self.assertEqual((self.root / "memory.json").read_text(), original)
        self.assertEqual(self.store.load("memory")["facts"], ["learn Python"])

    def test_file_paths_blocked(self):
        files = self.tools.files
        for path in (".env", "../x.py", ".git/config", "data/memory.json", "memory.json",
                     "C:/x.py", "node_modules/a.js", "credentials.txt", "x.pem"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                files.path(path)

    def test_read_redacts_known_secret(self):
        (self.root / "code.py").write_text('value="fake-sensitive-value-12345"')
        result = self.run_tool("read_file", path="code.py")
        self.assertNotIn("fake-sensitive-value-12345", result)
        self.assertIn("REDACTED", result)

    def test_file_write_approved_cancelled_and_secret(self):
        self.run_tool("write_file", path="demo.py", content="print('ok')\n")
        self.assertEqual((self.root / "demo.py").read_text(), "print('ok')\n")
        denied = Toolbox(self.config, self.store)
        self.assertIn("Cancelled", denied.execute("write_file", {"path": "demo.py", "content": "x"}))
        self.assertIn("Error", self.run_tool("write_file", path="bad.py", content="fake-sensitive-value-12345"))
        self.assertFalse((self.root / "bad.py").exists())

    def test_file_concurrent_edit_not_overwritten(self):
        p = self.root / "a.py"
        p.write_text("old")
        def approve(preview):
            p.write_text("new external edit")
            return True
        with self.assertRaises(ValueError):
            self.tools.files.write("a.py", "model edit", approve)
        self.assertEqual(p.read_text(), "new external edit")

    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "a.py"
            target.write_text("private")
            try:
                (self.root / "link.py").symlink_to(target)
            except OSError:
                self.skipTest("Windows symlink privilege unavailable")
            with self.assertRaises(ValueError):
                self.tools.files.read("link.py")

    def test_large_file_blocked(self):
        (self.root / "large.py").write_text("x" * 64001)
        self.assertIn("64 KB", self.run_tool("read_file", path="large.py"))

    def test_direct_commands(self):
        local_command("/task learn", self.tools)
        local_command("/done 1", self.tools)
        self.assertIn("done", local_command("/tasks", self.tools))
        self.assertIn("Unknown", local_command("/whatever", self.tools))
        self.assertIn("Usage", local_command("/update incorrect", self.tools))

    def test_no_memory_registry(self):
        toolbox = Toolbox(self.config, self.store, memory=False)
        self.assertNotIn("show_memory", toolbox.registry)
        self.assertIn("disabled", local_command("/forget-all", toolbox))

    def test_simple_chat(self):
        fake = FakeClient([message("Hello")])
        agent = Agent(self.config, self.tools, fake)
        self.assertEqual(agent.ask("hello"), "Hello")
        self.assertNotIn("fake-sensitive-value-12345", json.dumps(fake.requests))

    def test_chat_tool_result_roundtrip(self):
        fake = FakeClient([message(None, [call("create_task", '{"title":"learn"}')]), message("saved")])
        agent = Agent(self.config, self.tools, fake)
        self.assertEqual(agent.ask("create task"), "saved")
        self.assertEqual(self.store.load("tasks")["tasks"][0]["title"], "learn")
        self.assertIn("Created task", fake.requests[1]["messages"][-1]["content"])

    def test_empty_response_recovers_without_new_user_prompt(self):
        fake = FakeClient([message(None), message("Hello")])
        self.assertEqual(Agent(self.config, self.tools, fake).ask("Hello"), "Hello")
        self.assertEqual(len(fake.requests), 2)

    def test_truncated_text_response_recovers(self):
        fake = FakeClient([message("A truncated answer", finish_reason="length"), message("A complete answer")])
        self.assertEqual(Agent(self.config, self.tools, fake).ask("Explain a function"), "A complete answer")

    def test_portfolio_continues_after_html_empty_and_partial_replies(self):
        paths = ["myportfolio/index.html", "myportfolio/style.css", "myportfolio/script.js"]
        steps = ["Create HTML", "Create CSS", "Create JS", "Review all files"]
        replies = [
            message(None, [call("plan_work", json.dumps({"steps": steps, "files": paths}))]),
            message(None, [call("write_file", json.dumps({"path": paths[0], "content": "<html>demo</html>"}))]),
            message(None),
            message("The HTML is ready."),
            message(None, [call("write_file", json.dumps({"path": paths[1], "content": "body { color: blue; }"}))]),
            message(None, [call("write_file", json.dumps({"path": paths[2], "content": "console.log('ready');"}))]),
            message(None, [call("complete_step", json.dumps({"step_id": i}), str(i)) for i in range(1, 5)]),
            message(None, [call("finish_work", '{"summary":"All three portfolio files are ready."}')]),
        ]
        fake = FakeClient(replies)
        answer = Agent(self.config, self.tools, fake).ask("Create an HTML/CSS/JS portfolio in myportfolio.")
        self.assertEqual(answer, "All three portfolio files are ready.")
        self.assertTrue(all((self.root / path).is_file() for path in paths))
        self.assertTrue(self.tools.work.finished)
        self.assertGreater(len(fake.requests), 5)

    def test_finish_rejects_missing_files_despite_completed_steps(self):
        self.run_tool("plan_work", steps=["Create files"], files=["index.html", "style.css", "script.js"])
        self.run_tool("complete_step", step_id=1)
        (self.root / "index.html").write_text("<html></html>")
        result = self.run_tool("finish_work", summary="Done")
        self.assertIn("style.css", result)
        self.assertIn("script.js", result)
        self.assertFalse(self.tools.work.finished)

    def test_finish_rejects_pending_step_and_empty_file(self):
        self.run_tool("plan_work", steps=["Create", "Review"], files=["index.html"])
        (self.root / "index.html").write_text("")
        self.run_tool("complete_step", step_id=1)
        self.assertIn("Unfinished steps", self.run_tool("finish_work", summary="Done"))
        self.run_tool("complete_step", step_id=2)
        self.assertIn("empty", self.run_tool("finish_work", summary="Done"))
        self.assertFalse(self.tools.work.finished)

    def test_plan_validation_and_cannot_drop_obligations(self):
        self.assertIn("Error", self.run_tool("plan_work", steps=[3], files=[]))
        self.assertIn("Error", self.run_tool("plan_work", steps=["Create"], files=[".env"]))
        self.run_tool("plan_work", steps=["Create", "Review"], files=["index.html", "style.css"])
        self.assertIn("Error", self.run_tool("plan_work", steps=["Create"], files=["index.html"]))
        self.assertEqual(len(self.tools.work.steps), 2)

    def test_declined_write_stops_and_skips_later_batch_actions(self):
        tools = Toolbox(self.config, self.store, confirm=lambda preview: "index.html" in preview)
        fake = FakeClient([
            message(None, [call("plan_work", '{"steps":["Create files"],"files":["index.html","style.css","script.js"]}')]),
            message(None, [call("write_file", '{"path":"index.html","content":"<html></html>"}')]),
            message(None, [call("write_file", '{"path":"style.css","content":"body {}"}'),
                           call("write_file", '{"path":"script.js","content":"console.log(1);"}', "call_2")]),
        ])
        answer = Agent(self.config, tools, fake).ask("Create three files")
        self.assertIn("declined", answer)
        self.assertTrue((self.root / "index.html").exists())
        self.assertFalse((self.root / "style.css").exists())
        self.assertFalse((self.root / "script.js").exists())

    def test_plan_budget_exhaustion_is_not_reported_complete(self):
        self.config.max_rounds = 1
        fake = FakeClient([
            message(None, [call("plan_work", '{"steps":["Create"],"files":["index.html"]}')]),
            message("All done."),
        ])
        answer = Agent(self.config, self.tools, fake).ask("Create a file")
        self.assertTrue(answer.startswith("Task paused: request budget reached."))
        self.assertFalse(self.tools.work.finished)
        self.assertIn("pending", answer)

    def test_no_progress_replies_stop_bounded(self):
        fake = FakeClient([message(None), message(""), message(" ")])
        self.assertIn("three responses", Agent(self.config, self.tools, fake).ask("Hello"))
        self.assertEqual(len(fake.requests), 3)

    def test_write_without_plan_is_not_executed(self):
        fake = FakeClient([
            message(None, [call("write_file", '{"path":"index.html","content":"<html></html>"}')]),
            message(None, [call("pause_work", '{"reason":"Cannot establish the requested plan."}')]),
        ])
        self.assertIn("Task paused", Agent(self.config, self.tools, fake).ask("Create a file"))
        self.assertFalse((self.root / "index.html").exists())

    def test_truncated_tool_json_can_be_repaired_and_finished(self):
        fake = FakeClient([
            message(None, [call("plan_work", '{"steps":[')], finish_reason="length"),
            message("I am still planning."),
            message(None, [call("plan_work", '{"steps":["Create file"],"files":["index.html"]}')]),
            message(None, [call("write_file", '{"path":"index.html","content":"cut off')], finish_reason="length"),
            message(None, [call("write_file", '{"path":"index.html","content":"<html>ready</html>"}'),
                           call("complete_step", '{"step_id":1}', "call_2"),
                           call("finish_work", '{"summary":"Done"}', "call_3")]),
        ])
        self.assertEqual(Agent(self.config, self.tools, fake).ask("Create a file"), "Done")
        self.assertEqual((self.root / "index.html").read_text(), "<html>ready</html>")

    def test_work_budget_configurable_and_validated(self):
        (self.root / ".env").write_text("OLLAMA_API_KEY=fake-sensitive-value-12345\n"
                                       "AGENT_MAX_ROUNDS=40\nAGENT_MAX_OUTPUT_TOKENS=10000\n")
        with patch.dict("os.environ", {}, clear=True):
            config = Config.load(self.root)
        self.assertEqual(config.max_rounds, 40)
        self.assertEqual(config.max_output_tokens, 10000)
        with patch.dict("os.environ", {"AGENT_MAX_ROUNDS": "0"}, clear=True), self.assertRaises(ValueError):
            Config.load(self.root)

    def test_equivalent_planned_path_and_actions_after_finish(self):
        fake = FakeClient([
            message(None, [call("plan_work", '{"steps":["Create"],"files":["./index.html"]}')]),
            message(None, [call("write_file", '{"path":"index.html","content":"<html></html>"}'),
                           call("complete_step", '{"step_id":1}', "call_2"),
                           call("finish_work", '{"summary":"Done"}', "call_3"),
                           call("write_file", '{"path":"extra.js","content":"alert(1);"}', "call_4")]),
        ])
        agent = Agent(self.config, self.tools, fake)
        self.assertEqual(agent.ask("Create index.html"), "Done")
        self.assertTrue((self.root / "index.html").exists())
        self.assertFalse((self.root / "extra.js").exists())
        self.assertEqual(agent.turns[-1][-1], {"role": "assistant", "content": "Done"})

    def test_invalid_tool_json(self):
        fake = FakeClient([message(None, [call("create_task", "{bad")]), message("failed")])
        agent = Agent(self.config, self.tools, fake)
        agent.ask("task")
        self.assertEqual(self.store.load("tasks")["tasks"], [])
        self.assertIn("Invalid JSON", fake.requests[1]["messages"][-1]["content"])

    def test_history_trim_complete_turns(self):
        fake = FakeClient([message() for _ in range(4)])
        self.config.history_turns = 2
        agent = Agent(self.config, self.tools, fake)
        for _ in range(4):
            agent.ask("hi")
        self.assertEqual(len(agent.turns), 2)
        self.assertTrue(all(t[0]["role"] == "user" and t[-1]["role"] == "assistant" for t in agent.turns))

    def test_tool_budget_forces_final_without_tools(self):
        self.config.max_rounds = 1
        fake = FakeClient([message(None, [call("show_memory", "{}")]), message("summary")])
        self.assertEqual(Agent(self.config, self.tools, fake).ask("memory?"), "summary")
        self.assertNotIn("tools", fake.requests[-1])

    def test_input_secret_never_sent(self):
        fake = FakeClient([])
        with self.assertRaises(ValueError):
            Agent(self.config, self.tools, fake).ask("fake-sensitive-value-12345")
        self.assertEqual(fake.requests, [])

    def test_output_secret_redacted(self):
        fake = FakeClient([message("fake-sensitive-value-12345")])
        self.assertEqual(Agent(self.config, self.tools, fake).ask("hi"), "[REDACTED]")

    def test_web_private_addresses(self):
        for address in ("127.0.0.1", "192.168.1.4", "169.254.169.254", "::1"):
            with patch("socket.getaddrinfo", return_value=[(0, 0, 0, "", (address, 443))]):
                with self.assertRaises(ValueError):
                    public_target("https://example.com/")

    def test_web_invalid_urls(self):
        for url in ("http://example.com", "https://user:pass@example.com", "https://example.com:444",
                    "file:///etc/passwd", "https://example.com:bad"):
            with self.assertRaises(ValueError):
                public_target(url)

    def test_web_public_ip_pinned(self):
        with patch("socket.getaddrinfo", return_value=[(0, 0, 0, "", ("93.184.216.34", 443))]):
            self.assertEqual(public_target("https://example.com/docs?q=x")[:2],
                             ("example.com", "93.184.216.34"))

    def test_web_redirect_to_private_rejected(self):
        response = SimpleNamespace(status=302, headers={"Location": "https://127.0.0.1/"}, close=lambda: None)
        pool = SimpleNamespace(urlopen=lambda *a, **kw: response, close=lambda: None)
        def addresses(host, *a, **kw):
            return [(0, 0, 0, "", ("127.0.0.1" if host == "127.0.0.1" else "93.184.216.34", 443))]
        with patch("socket.getaddrinfo", side_effect=addresses), patch("personal_agent.web.HTTPSConnectionPool", return_value=pool):
            with self.assertRaises(ValueError):
                read_webpage("https://example.com")


if __name__ == "__main__":
    unittest.main()
