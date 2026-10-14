"""Opt-in live test. Uses only synthetic data in a temporary workspace."""
import argparse
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from personal_agent.config import Config
from personal_agent.storage import Store
from personal_agent.tools import Toolbox
from personal_agent.agent import Agent


def main():
    parser = argparse.ArgumentParser(description="Synthetic Ollama integration test (consumes API quota)")
    parser.add_argument("--live", action="store_true", required=True)
    parser.add_argument("--portfolio", action="store_true", help="Run just the three-file continuous task test")
    args = parser.parse_args()
    if not args.live:
        return 1
    with tempfile.TemporaryDirectory(prefix="personal-agent-smoke-") as directory:
        root = Path(directory)
        config = Config.load(workspace=root)
        store = Store(root / "data", config.guard)
        toolbox = Toolbox(config, store, confirm=lambda _: True)
        trace = []
        agent = Agent(config, toolbox, progress=trace.append)
        if args.portfolio:
            answer = agent.ask(
                "Please create a myportfolio folder here and in it create a detailed portfolio website. "
                "Create exactly index.html, style.css and script.js, all in myportfolio. "
                "Use vanilla HTML/CSS/JS and static demo content, with local CSS and JS links. "
                "Complete all three files and review their references before finishing."
            )
            from bs4 import BeautifulSoup
            paths = [root / "myportfolio" / name for name in ("index.html", "style.css", "script.js")]
            files_ok = all(path.is_file() and path.stat().st_size > 0 for path in paths)
            links_ok = False
            if files_ok:
                soup = BeautifulSoup(paths[0].read_text(encoding="utf-8"), "html.parser")
                links_ok = (any(str(tag.get("href", "")).removeprefix("./") == "style.css"
                                for tag in soup.find_all("link")) and
                            any(str(tag.get("src", "")).removeprefix("./") == "script.js"
                                for tag in soup.find_all("script")))
            print("cloud_portfolio_files:", "PASS" if files_ok else "FAIL")
            print("cloud_portfolio_references:", "PASS" if links_ok else "FAIL")
            print("cloud_task_completion:", "PASS" if toolbox.work.finished else "FAIL")
            print("tools_used:", ", ".join(trace))
            if not toolbox.work.finished:
                print(config.guard.redact(answer))
            print("Only temporary synthetic files were used; the user's portfolio was not changed.")
            return 0 if files_ok and links_ok and toolbox.work.finished else 1
        answer = agent.ask("Say hello in one short sentence. Do not call any tools.")
        ok = bool(answer) and not answer.startswith(("Authentication", "Cannot connect", "Ollama",
                                                   "Model returned", "Task paused"))
        print("cloud_chat:", "PASS" if ok else "FAIL: " + answer)
        if not ok:
            return 1
        agent.ask("Use create_task to create exactly one task titled 'synthetic smoke task'.")
        task_ok = any(t["title"] == "synthetic smoke task" for t in store.load("tasks")["tasks"])
        print("cloud_tool_roundtrip:", "PASS" if task_ok else "FAIL (model did not create task)")
        (root / "demo.py").write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
        agent.ask("Read demo.py with read_file. Fix add so it adds the two arguments. "
                  "Use write_file to save the corrected complete file. No other file changes.")
        code_ok = "return a + b" in (root / "demo.py").read_text(encoding="utf-8")
        print("cloud_code_edit:", "PASS" if code_ok else "FAIL (expected change missing)")
        print("tools_used:", ", ".join(trace))
        print("User memory/tasks and project code were not modified by this test.")
        return 0 if task_ok and code_ok else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        print("Live test failed. Check config/connection; credentials and response bodies are suppressed.")
        raise SystemExit(1)
