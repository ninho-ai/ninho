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


def get_cwd(input_data: dict) -> str:
    """
    Get current working directory from input or environment.

    Args:
        input_data: Hook input dictionary.

    Returns:
        Current working directory path.
    """
    return input_data.get("cwd", os.getcwd())


def get_transcript_path(input_data: dict) -> str:
    """
    Get transcript path from input.

    Args:
        input_data: Hook input dictionary.

    Returns:
        Transcript file path or None.
    """
    return input_data.get("transcript_path")


def ensure_ninho_dirs(cwd: str):
    """
    Ensure Ninho directories exist.

    Args:
        cwd: Current working directory.
    """
    # Global storage
    global_path = Path.home() / ".ninho"
    global_path.mkdir(parents=True, exist_ok=True)
    (global_path / "daily").mkdir(exist_ok=True)

    # Project storage
    project_path = Path(cwd) / ".ninho"
    project_path.mkdir(parents=True, exist_ok=True)
    (project_path / "prds").mkdir(exist_ok=True)
    (project_path / "prompts").mkdir(exist_ok=True)
