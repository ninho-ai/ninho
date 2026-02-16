#!/usr/bin/env python3
"""
PreCompact hook for Ninho.

Captures learnings and PRD content before context is compacted.
Runs synchronously to ensure capture before data is lost.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add core library to path
SCRIPT_DIR = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(SCRIPT_DIR / "packages" / "core" / "src"))

from capture import Capture
from common import get_cwd
from learnings import Learnings
from prd import PRD
from prd_capture import PRDCapture
from storage import ProjectStorage, Storage


def main():
    """Main entry point for PreCompact hook."""
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

    cwd = get_cwd(input_data)

    # Initialize components
    storage = Storage()
    project_storage = ProjectStorage(cwd)
    capture = Capture(transcript_path)
    learnings_manager = Learnings(storage)
    prd_capture = PRDCapture(project_storage)
    prd_manager = PRD(project_storage)

    # Extract prompts
    prompts = capture.get_user_prompts()
    if not prompts:
        # Still write snapshot even if no new prompts - compaction happened
        write_session_snapshot(project_storage, prd_manager, capture)
        return 0

    # Detect feature context for tagging
    feature = capture.detect_feature_context() or "general"

    # Save ALL prompts (not just PRD-worthy ones) for summarization
    saved_prompt_count = 0
    for prompt in prompts:
        text = prompt.get("text", "")
        timestamp = prompt.get("timestamp")
        if text and not prd_capture._is_duplicate(text):
            project_storage.append_prompt(text, feature, timestamp)
            prd_capture._mark_as_seen(text)
            saved_prompt_count += 1

    if saved_prompt_count > 0:
        print(f"Pre-compact: Saved {saved_prompt_count} prompts for summarization")

    # Extract and save learnings
    learnings = learnings_manager.extract_learnings(prompts)
    if learnings:
        saved_count = learnings_manager.save_learnings(learnings)
        if saved_count > 0:
            print(f"Pre-compact: Saved {saved_count} learnings before context loss")

    # Extract and save PRD items
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

        print(f"Pre-compact: Captured {len(prd_items)} PRD items for '{feature}'")

    # Write session snapshot for post-compaction context re-injection
    write_session_snapshot(project_storage, prd_manager, capture)

    return 0


def _get_compaction_count(project_storage: ProjectStorage) -> int:
    """Read compaction count from existing session snapshot, or 0."""
    snapshot_path = project_storage.ninho_path / ".session-snapshot.json"
    if not snapshot_path.exists():
        return 0
    try:
        data = json.loads(snapshot_path.read_text())
        return data.get("compaction_count", 0)
    except (json.JSONDecodeError, OSError):
        return 0


def write_session_snapshot(
    project_storage: ProjectStorage,
    prd_manager: PRD,
    capture: Capture,
) -> None:
    """Write a session snapshot for post-compaction context re-injection."""
    try:
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "active_feature": capture.detect_feature_context(),
            "modified_files": capture.get_modified_files()[:10],
            "prd_names": prd_manager.list_prds(),
            "compaction_count": _get_compaction_count(project_storage) + 1,
        }
        snapshot_path = project_storage.ninho_path / ".session-snapshot.json"
        project_storage.write_file(snapshot_path, json.dumps(snapshot, indent=2))
        print("Pre-compact: Wrote session snapshot for context restoration")
    except Exception as e:
        print(f"Warning: Failed to write session snapshot: {e}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
