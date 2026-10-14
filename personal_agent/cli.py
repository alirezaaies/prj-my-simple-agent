"""Direct commands work offline; natural-language chat is lazy-initialized."""
import argparse
import json
from pathlib import Path
import sys

from .config import Config, ROOT
from .storage import Store
from .tools import Toolbox
from .agent import Agent

HELP = """Direct commands (no model API usage):
/help                      Show command help
/status                    Show model, paths and saved item counts
/plan                      Show the current request's checklist
/memory                    Show saved facts
/remember TEXT             Save a fact
/update OLD | NEW          Replace an exact saved fact
/forget TEXT               Delete a fact after confirmation
/forget-all                Clear saved facts after confirmation
/tasks                     List all tasks and their IDs
/task TITLE                Create a task
/done ID                   Mark a task completed
/delete-task ID            Delete a task after confirmation
/files                     List supported workspace files
/read PATH                 Read a workspace file
/search QUERY              Search the web (requires internet)
/open HTTPS_URL            Read a public webpage
/reset                     Clear this conversation's history
/exit                      Exit
Write a normal request for conversation, coding help or research.
Replies default to English. Explicitly ask for another language when needed.
Model-proposed changes are previewed and saved only after you type YES.
"""


def confirm(preview):
    print("\n" + preview)
    return input("Type YES to apply this change (Enter = cancel): ").strip() == "YES"


def local_command(text, toolbox, agent=None):
    name, _, arg = text.partition(" ")
    arg = arg.strip()
    if name == "/help":
        return HELP + ("\nSaved memory and task tools are disabled in this session.\n"
                       if "show_memory" not in toolbox.registry else "")
    if name == "/status":
        c = toolbox.config
        return (f"Model: {c.model}\nEndpoint: {c.base_url}\nWorkspace: {c.workspace}\n"
                f"State: {toolbox.store.directory}\nFacts: {len(toolbox.store.load('memory')['facts'])}\n"
                f"Tasks: {len(toolbox.store.load('tasks')['tasks'])}\n"
                f"Saved memory/task tools: {'enabled' if 'show_memory' in toolbox.registry else 'disabled'}\n"
                f"Task round limit: {c.max_rounds}; output token limit: {c.max_output_tokens}\n"
                "Cloud chat and selected file content are sent to Ollama. API key is hidden.")
    if name == "/plan":
        return toolbox.work.status()
    if name == "/reset":
        if agent:
            agent.reset()
        return "Conversation cleared. Saved facts/tasks remain."
    if name == "/forget-all":
        if "show_memory" not in toolbox.registry:
            return "Memory tools disabled."
        if toolbox.confirm("Delete ALL saved facts? Tasks are preserved."):
            return toolbox.store.change("memory", lambda data: (data.update(facts=[]), "Memory cleared.")[1])
        return "Cancelled."
    mapping = {
        "/memory": ("show_memory", {}), "/remember": ("remember_fact", {"fact": arg}),
        "/forget": ("forget_fact", {"fact": arg}), "/tasks": ("list_tasks", {}),
        "/task": ("create_task", {"title": arg}), "/files": ("list_files", {}),
        "/read": ("read_file", {"path": arg}), "/search": ("web_search", {"query": arg}),
        "/open": ("read_webpage", {"url": arg}),
    }
    if name == "/update":
        old, sep, new = arg.partition("|")
        if not sep:
            return "Usage: /update OLD | NEW"
        mapping[name] = ("update_fact", {"old_fact": old.strip(), "new_fact": new.strip()})
    if name in ("/done", "/delete-task"):
        try:
            number = int(arg)
        except ValueError:
            return "Use a numeric task ID from /tasks."
        mapping[name] = ("complete_task" if name == "/done" else "delete_task", {"task_id": number})
    if name not in mapping:
        return "Unknown command. Use /help."
    tool, arguments = mapping[name]
    return toolbox.execute(tool, arguments, local=name not in ("/forget", "/delete-task"))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Personal coding and research agent")
    parser.add_argument("--workspace", type=Path, help="Folder the file tools may access")
    parser.add_argument("--no-memory", action="store_true", help="Disable saved facts/task tools")
    parser.add_argument("--check", action="store_true", help="Check local config without any API request")
    parser.add_argument("--ask", help="One request or local command; proposed changes default to cancelled")
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr, sys.stdin):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    guard = None
    try:
        config = Config.load(workspace=args.workspace)
        guard = config.guard
        if not config.workspace.is_dir():
            raise ValueError("Workspace folder does not exist.")
        store = Store(ROOT / "data", guard)
        if not args.no_memory:
            store.migrate(ROOT)
        toolbox = Toolbox(config, store, confirm=(lambda preview: False) if args.ask else confirm,
                          memory=not args.no_memory)
        if args.check:
            print(local_command("/status", toolbox))
            print("Local configuration OK. API connectivity has not been tested.")
            return 0
        agent = None
        def respond(text):
            nonlocal agent
            guard.check(text)
            if text.startswith("/"):
                return local_command(text, toolbox, agent)
            if agent is None:
                agent = Agent(config, toolbox, progress=lambda name: print(f"[tool] {name}"),
                              update=lambda text: print(f"[progress] {text}"),
                              memory=not args.no_memory)
            return agent.ask(text)
        if args.ask:
            print(respond(args.ask))
            return 0
        print("Personal Agent is ready. Type /help for commands or /exit to quit.")
        print("In cloud mode, chat and selected file content are sent to Ollama.")
        print("Multi-step tasks continue automatically. Ctrl+C stops the current run.")
        while True:
            try:
                text = input("\nYou > ").strip()
                if text.lower() in ("exit", "quit", "/exit"):
                    break
                if text:
                    print("\nAssistant > " + respond(text))
            except (EOFError, KeyboardInterrupt):
                break
            except ValueError as error:
                print("Error: " + guard.redact(error))
            except Exception:
                print("Unexpected error. No successful action confirmed; check /memory, /tasks and git diff.")
        return 0
    except (EOFError, KeyboardInterrupt):
        return 130
    except ValueError as error:
        print("Error: " + (guard.redact(error) if guard else "Configuration invalid. Check .env names, URL and timeout."))
        return 1
    except Exception:
        print("Startup failed. Check dependencies, data files and folder permissions. No credentials shown.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
