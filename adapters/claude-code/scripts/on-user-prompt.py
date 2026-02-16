#!/usr/bin/env python3
"""
UserPromptSubmit hook for Ninho.

Captures every user prompt immediately as it's submitted.
Runs synchronously to ensure prompt is saved before processing.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add core library to path
SCRIPT_DIR = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(SCRIPT_DIR / "packages" / "core" / "src"))

from prd import PRD
from prd_capture import PRDCapture
from storage import ProjectStorage


def main():
    """Main entry point for UserPromptSubmit hook."""
    # Read hook input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("Error: Invalid JSON input", file=sys.stderr)
        return 1

    prompt = input_data.get("prompt", "")
    if not prompt:
        return 0

    cwd = input_data.get("cwd", os.getcwd())

    # Initialize components
    project_storage = ProjectStorage(cwd)
    prd_capture = PRDCapture(project_storage)
    prd_manager = PRD(project_storage)

    # Skip if duplicate
    if prd_capture._is_duplicate(prompt):
        return 0

    # Detect feature context from prompt
    feature = _detect_feature(prompt) or "general"

    # Save prompt immediately
    timestamp = datetime.now().isoformat()
    project_storage.append_prompt(prompt, feature, timestamp)
    prd_capture._mark_as_seen(prompt)

    # Extract PRD items from this single prompt
    prd_items = prd_capture.extract_prd_items([{"text": prompt, "timestamp": timestamp}])
    if prd_items:
        # Create PRD if it doesn't exist
        if not prd_manager.exists(feature):
            prd_manager.create(feature)

        prompt_date = datetime.now().strftime("%Y-%m-%d")
        prompt_ref = f"prompts/{prompt_date}.md"

        for item in prd_items:
            item_type = item.get("type")
            text = item.get("text", "")
            summary = item.get("summary", text[:80])

            if item_type == "requirement" or item_type == "bug":
                prd_manager.add_requirement(feature, summary)
                prd_manager.add_session_log(feature, f"Added requirement: {summary[:50]}...", prompt_ref)

            elif item_type == "decision":
                rationale = item.get("rationale", "See discussion")
                prd_manager.add_decision(feature, summary, rationale)
                prd_manager.add_session_log(feature, f"Decided: {summary[:50]}...", prompt_ref)

            elif item_type == "constraint":
                prd_manager.add_constraint(feature, summary)
                prd_manager.add_session_log(feature, f"Added constraint: {summary[:50]}...", prompt_ref)

            elif item_type == "question":
                prd_manager.add_question(feature, summary)
                prd_manager.add_session_log(feature, f"Open question: {summary[:50]}...", prompt_ref)

    return 0


def _detect_feature(prompt: str) -> str:
    """Detect feature context from prompt text."""
    import re

    prompt_lower = prompt.lower()

    # Check for explicit feature mentions
    feature_patterns = [
        r"working on (\w+)",
        r"for the (\w+) feature",
        r"in (\w+) module",
        r"(\w+) component",
    ]

    for pattern in feature_patterns:
        match = re.search(pattern, prompt_lower)
        if match:
            return match.group(1)

    return "general"


if __name__ == "__main__":
    sys.exit(main())
