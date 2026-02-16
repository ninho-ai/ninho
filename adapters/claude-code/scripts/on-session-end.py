#!/usr/bin/env python3
"""
SessionEnd hook for Ninho.

Extracts learnings and PRD content from the completed session.
Runs asynchronously after the user exits.
"""

import json
import os
import sys
from pathlib import Path

# Add core library to path
SCRIPT_DIR = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(SCRIPT_DIR / "packages" / "core" / "src"))

from capture import Capture
from learnings import Learnings
from prd import PRD
from prd_capture import PRDCapture
from storage import ProjectStorage, Storage


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

    cwd = input_data.get("cwd", os.getcwd())

    # Initialize components
    storage = Storage()
    project_storage = ProjectStorage(cwd)
    capture = Capture(transcript_path)
    learnings_manager = Learnings(storage)
    prd_capture = PRDCapture(project_storage)
    prd_manager = PRD(project_storage)

    # Consume any pending response summary from the last exchange
    project_storage.consume_pending_summary()

    # Extract prompts
    prompts = capture.get_user_prompts()
    if not prompts:
        print("No prompts found in transcript")
        return 0

    # Detect feature context for tagging
    feature = capture.detect_feature_context() or "general"

    # Final sweep: Save ALL prompts that weren't captured by PreCompact
    saved_prompt_count = 0
    for prompt in prompts:
        text = prompt.get("text", "")
        timestamp = prompt.get("timestamp")
        if text and not prd_capture._is_duplicate(text):
            project_storage.append_prompt(text, feature, timestamp)
            prd_capture._mark_as_seen(text)
            saved_prompt_count += 1

    if saved_prompt_count > 0:
        print(f"SessionEnd: Saved {saved_prompt_count} prompts for summarization")

    # Extract and save learnings
    learnings = learnings_manager.extract_learnings(prompts)
    if learnings:
        saved_count = learnings_manager.save_learnings(learnings)
        print(f"Saved {saved_count} new learnings to daily log")

    # Extract and save PRD items (final sweep for anything missed by PreCompact)
    prd_items = prd_capture.extract_prd_items(prompts)
    if prd_items:
        # Create PRD if it doesn't exist
        if not prd_manager.exists(feature):
            prd_manager.create(feature)

        # Add modified files to PRD
        modified_files = capture.get_modified_files()
        for file_path in modified_files:
            prd_manager.add_file(feature, file_path)

        # Process each captured item
        for item in prd_items:
            item_type = item.get("type")
            text = item.get("text", "")
            summary = item.get("summary", text[:80])

            # Generate prompt reference (prompt already saved above)
            from datetime import datetime
            prompt_date = datetime.now().strftime("%Y-%m-%d")
            prompt_ref = f"prompts/{prompt_date}.md"

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

        print(f"SessionEnd: Captured {len(prd_items)} PRD items for '{feature}'")

    return 0


if __name__ == "__main__":
    sys.exit(main())
