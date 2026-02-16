"""
Common utilities for Ninho hook scripts.

Provides error handling, logging, and shared functionality.
"""

import json
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

# Ninho log file
LOG_FILE = Path.home() / ".ninho" / "ninho.log"


def setup_logging():
    """Ensure log directory exists."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def log(level: str, message: str, context: dict = None):
    """
    Log a message to the Ninho log file.

    Args:
        level: Log level (INFO, WARN, ERROR)
        message: Log message
        context: Optional context dictionary
    """
    try:
        setup_logging()
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message,
        }
        if context:
            log_entry["context"] = context

        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception:
        # Silently fail - logging should never break the main flow
        pass


def log_info(message: str, context: dict = None):
    """Log an info message."""
    log("INFO", message, context)


def log_warn(message: str, context: dict = None):
    """Log a warning message."""
    log("WARN", message, context)


def log_error(message: str, context: dict = None):
    """Log an error message."""
    log("ERROR", message, context)


def safe_read_stdin() -> dict:
    """
    Safely read JSON input from stdin.

    Returns:
        Parsed JSON dict or empty dict on error.
    """
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError as e:
        log_error("Failed to parse stdin JSON", {"error": str(e)})
        return {}
    except Exception as e:
        log_error("Failed to read stdin", {"error": str(e)})
        return {}


def safe_run(func):
    """
    Decorator to wrap main functions with error handling.

    Catches all exceptions and logs them without crashing.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_error(
                f"Unhandled exception in {func.__name__}",
                {
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                }
            )
            # Return success to not block Claude Code
            return 0
    return wrapper


def find_project_root(start_dir: str) -> str:
    """
    Walk up from start_dir looking for project root markers.

    Searches by priority: .claude/ first (full walk), then .git/,
    then CLAUDE.md. Higher-priority markers at any ancestor take
    precedence over lower-priority markers closer to start_dir.
    Falls back to start_dir if no marker found.

    Args:
        start_dir: Directory to start searching from.

    Returns:
        Project root directory path.
    """
    markers = [".claude", ".git", "CLAUDE.md"]

    for marker in markers:
        current = Path(start_dir).resolve()
        while True:
            if (current / marker).exists():
                return str(current)
            parent = current.parent
            if parent == current:
                break
            current = parent

    return start_dir


def get_cwd(input_data: dict) -> str:
    """
    Get project root directory from input or environment.

    Resolves the true project root by walking up from the raw cwd
    to find project markers (.claude/, .git/, CLAUDE.md).

    Args:
        input_data: Hook input dictionary.

    Returns:
        Project root directory path.
    """
    raw_cwd = input_data.get("cwd", os.getcwd())
    return find_project_root(raw_cwd)


def get_transcript_path(input_data: dict) -> str:
    """
    Get transcript path from input.

    Args:
        input_data: Hook input dictionary.

    Returns:
        Transcript file path or None.
    """
    return input_data.get("transcript_path")


def ensure_ninho_dirs(input_data: dict = None):
    """
    Ensure Ninho directories exist.

    Args:
        input_data: Hook input dictionary (optional). Used to resolve project root.
    """
    cwd = get_cwd(input_data or {})

    # Global storage
    global_path = Path.home() / ".ninho"
    global_path.mkdir(parents=True, exist_ok=True)
    (global_path / "daily").mkdir(exist_ok=True)

    # Project storage
    project_path = Path(cwd) / ".ninho"
    project_path.mkdir(parents=True, exist_ok=True)
    (project_path / "prds").mkdir(exist_ok=True)
    (project_path / "prompts").mkdir(exist_ok=True)
