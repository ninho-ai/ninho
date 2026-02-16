#!/usr/bin/env python3
"""
Stop hook for Ninho.

Monitors conversation for PRD-worthy updates after each Claude response.
Runs asynchronously to avoid blocking the user's workflow.
"""

import json
import os
import sys
import time
from pathlib import Path

# Add core library to path
SCRIPT_DIR = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(SCRIPT_DIR / "packages" / "core" / "src"))

from capture import Capture
from prd import PRD
from storage import Storage, ProjectStorage

# Throttle settings
THROTTLE_SECONDS = 30
LAST_UPDATE_FILE = Path.home() / ".ninho" / "last_prd_update"


def should_throttle() -> bool:
    """Check if we should skip this update due to throttling."""
    if not LAST_UPDATE_FILE.exists():
        return False

    try:
        last_update = float(LAST_UPDATE_FILE.read_text())
        return (time.time() - last_update) < THROTTLE_SECONDS
    except (ValueError, OSError):
        return False


def update_throttle():
    """Update the throttle timestamp."""
    LAST_UPDATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    LAST_UPDATE_FILE.write_text(str(time.time()))


def detect_prd_signals(text: str) -> dict:
    """
    Detect PRD-worthy signals in text.

    Returns:
        Dictionary with detected signals.
    """
    import re

    signals = {
        "requirement": False,
        "decision": False,
        "constraint": False,
        "question": False,
    }

    text_lower = text.lower()

    # Requirement signals
    req_patterns = [
        r"\bneed\s+to\b",
        r"\bshould\s+have\b",
        r"\bmust\s+support\b",
        r"\brequire[sd]?\b",
        r"\bfeature\b",
    ]
    for pattern in req_patterns:
        if re.search(pattern, text_lower):
            signals["requirement"] = True
            break

    # Decision signals
    dec_patterns = [
        r"\blet's\s+(use|go with)\b",
        r"\bwe('ll| will)\s+use\b",
        r"\bdecided\s+(to|on)\b",
        r"\bchose\b",
        r"\bprefer\b",
    ]
    for pattern in dec_patterns:
        if re.search(pattern, text_lower):
            signals["decision"] = True
            break

    # Constraint signals
    con_patterns = [
        r"\bmust\s+be\b",
        r"\bcannot\b",
        r"\blimit(ed)?\s+to\b",
        r"\bmaximum\b",
        r"\bminimum\b",
    ]
    for pattern in con_patterns:
        if re.search(pattern, text_lower):
            signals["constraint"] = True
            break

    # Question signals
    if "?" in text:
        signals["question"] = True

    return signals


def main():
    """Main entry point for Stop hook."""
    # Check throttle
    if should_throttle():
        return 0

    # Read hook input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 1

    transcript_path = input_data.get("transcript_path")
    cwd = input_data.get("cwd", os.getcwd())

    if not transcript_path:
        return 1

    # Initialize components
    capture = Capture(transcript_path)

    # Get recent prompts
    recent_prompts = capture.get_recent_prompts(3)
    if not recent_prompts:
        return 0

    # Check for PRD-worthy signals
    has_signals = False
    for prompt in recent_prompts:
        signals = detect_prd_signals(prompt.get("text", ""))
        if any(signals.values()):
            has_signals = True
            break

    if not has_signals:
        return 0

    # Detect feature context
    feature = capture.detect_feature_context()
    if not feature:
        # Try to use a generic name based on modified files
        modified = capture.get_modified_files()
        if modified:
            # Use first directory as feature name
            first_file = Path(modified[0])
            parts = first_file.parts
            if len(parts) > 1:
                feature = parts[1] if parts[0] == "src" else parts[0]
            else:
                feature = "general"
        else:
            feature = "general"

    # Initialize project storage
    project_storage = ProjectStorage(cwd)
    prd_manager = PRD(project_storage)

    # Create PRD if it doesn't exist
    if not prd_manager.exists(feature):
        prd_manager.create(feature)
        print(f"Created new PRD: {feature}")

    # Add modified files
    modified_files = capture.get_modified_files()
    for file_path in modified_files:
        prd_manager.add_file(feature, file_path)

    # Update throttle
    update_throttle()

    return 0


if __name__ == "__main__":
    sys.exit(main())
