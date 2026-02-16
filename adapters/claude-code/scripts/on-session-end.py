#!/usr/bin/env python3
"""
SessionEnd hook for Ninho.

Extracts learnings from the completed session and saves them to daily log.
Runs asynchronously after the user exits.
"""

import json
import sys
from pathlib import Path

# Add core library to path
SCRIPT_DIR = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(SCRIPT_DIR / "packages" / "core" / "src"))

from capture import Capture
from learnings import Learnings
from storage import Storage


def main():
    """Main entry point for SessionEnd hook."""
    # Read hook input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("Error: Invalid JSON input", file=sys.stderr)
        return 1

    transcript_path = input_data.get("transcript_path")
    if not transcript_path:
        print("Error: No transcript_path provided", file=sys.stderr)
        return 1

    # Initialize components
    storage = Storage()
    capture = Capture(transcript_path)
    learnings_manager = Learnings(storage)

    # Extract prompts
    prompts = capture.get_user_prompts()
    if not prompts:
        print("No prompts found in transcript")
        return 0

    # Extract learnings
    learnings = learnings_manager.extract_learnings(prompts)
    if not learnings:
        print("No learnings detected in session")
        return 0

    # Save learnings
    saved_count = learnings_manager.save_learnings(learnings)
    print(f"Saved {saved_count} new learnings to daily log")

    return 0


if __name__ == "__main__":
    sys.exit(main())
