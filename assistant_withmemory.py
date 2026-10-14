"""Compatibility entry point. Original tutorial: examples/legacy/."""
import sys
from personal_agent.cli import main

if __name__ == "__main__":
    raise SystemExit(main([*sys.argv[1:]]))
