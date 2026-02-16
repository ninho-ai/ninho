#!/usr/bin/env python3
"""
Stop hook for Ninho.

Monitors conversation for PRD-worthy updates after each Claude response.
Also detects PR-related activities for automatic linking.
Runs asynchronously to avoid blocking the user's workflow.
"""

import json
import os
import re
import sys
import time
from pathlib import Path

# Add core library to path
SCRIPT_DIR = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(SCRIPT_DIR / "packages" / "core" / "src"))

from capture import Capture
from prd import PRD
from pr_integration import PRIntegration
from storage import ProjectStorage, Storage

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


def detect_pr_commands(transcript_path: str) -> dict:
    """
    Detect PR-related commands in the transcript.

    Returns:
        Dictionary with PR command info or None.
    """
    try:
        with open(transcript_path, "r") as f:
            lines = f.readlines()

        # Check recent entries for PR commands
        for line in reversed(lines[-50:]):  # Check last 50 entries
            try:
                entry = json.loads(line)
                # Look for tool_use events with bash commands
                if entry.get("type") == "assistant":
                    content = entry.get("message", {}).get("content", [])
                    for block in content:
                        if block.get("type") == "tool_use" and block.get("name") == "Bash":
                            command = block.get("input", {}).get("command", "")

                            # Detect gh pr create
                            if "gh pr create" in command:
                                return {"type": "pr_create", "command": command}

                            # Detect gh pr merge
                            if "gh pr merge" in command:
                                return {"type": "pr_merge", "command": command}

                            # Detect git push (often precedes PR creation)
                            if re.search(r"git push.*-u", command):
                                return {"type": "branch_push", "command": command}

            except json.JSONDecodeError:
                continue

    except (OSError, IOError):
        pass

    return None


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


def handle_pr_creation(pr_integration: PRIntegration, capture: Capture, prd_manager: PRD) -> bool:
    """
    Handle automatic PR-to-PRD linking when PR is being created.

    Returns:
        True if PR was linked, False otherwise.
    """
    branch = pr_integration.get_current_branch()
    if not branch or branch in ("main", "master"):
        return False

    # Check if already linked
    existing = pr_integration.get_branch_mapping(branch)
    if existing:
        return False

    # Detect PRD from branch name or modified files
    prd_name = pr_integration.detect_prd_from_branch(branch)
    if not prd_name:
        prd_name = pr_integration.detect_prd_from_files()

    if not prd_name:
        # Try to detect from capture's feature context
        prd_name = capture.detect_feature_context()

    if not prd_name or not prd_manager.exists(prd_name):
        return False

    # Get incomplete requirements from PRD
    requirements = pr_integration.get_prd_requirements(prd_name)
    incomplete = [r["text"] for r in requirements if not r["completed"]]

    if not incomplete:
        return False

    # Auto-link to all incomplete requirements (user can adjust later via command)
    pr_integration.link_branch_to_requirements(branch, prd_name, incomplete)

    print(f"🪺 Auto-linked branch '{branch}' to PRD '{prd_name}'")
    print(f"   Requirements tracked: {len(incomplete)}")

    # Check if PR exists and add to PRD
    pr_info = pr_integration.get_pr_info()
    if pr_info:
        pr_integration.add_pr_to_prd(
            prd_name,
            pr_info["number"],
            pr_info["url"],
            branch,
            incomplete[:3],  # Show first 3
            pr_info.get("state", "Open"),
        )
        print(f"   PR #{pr_info['number']} added to PRD")

    return True


def surface_file_context(prd_manager: PRD, modified_files: list) -> bool:
    """
    Surface relevant PRD context when files are edited.

    Returns:
        True if context was surfaced, False otherwise.
    """
    if not modified_files:
        return False

    # Map files to PRDs
    prd_names = prd_manager.list_prds()
    if not prd_names:
        return False

    surfaced = []
    for prd_name in prd_names:
        prd_path = prd_manager.storage.get_prd_file(prd_name)
        if not prd_path.exists():
            continue

        content = prd_path.read_text()

        # Check if any modified files are in this PRD's Related Files
        for file_path in modified_files:
            if file_path in content:
                # Extract relevant decisions
                decisions = []
                decision_pattern = r"\| (\d{4}-\d{2}-\d{2}) \| ([^|]+) \| ([^|]+) \|"
                for match in re.finditer(decision_pattern, content):
                    decisions.append({
                        "date": match.group(1),
                        "decision": match.group(2).strip(),
                        "rationale": match.group(3).strip(),
                    })

                # Extract open questions
                questions = []
                in_questions = False
                for line in content.split("\n"):
                    if line.startswith("## Open Questions"):
                        in_questions = True
                    elif line.startswith("## ") and in_questions:
                        in_questions = False
                    elif in_questions and line.strip().startswith("- "):
                        questions.append(line.strip()[2:])

                if decisions or questions:
                    surfaced.append({
                        "prd": prd_name,
                        "file": file_path,
                        "decisions": decisions[-3:],  # Last 3 decisions
                        "questions": questions[:2],  # First 2 questions
                    })
                break  # One match per PRD is enough

    if not surfaced:
        return False

    # Output context (will be captured by Claude)
    print("\n<ninho-file-context>")
    for ctx in surfaced[:2]:  # Limit to 2 PRDs
        print(f"## Editing files related to: {ctx['prd'].replace('-', ' ').title()}")

        if ctx["decisions"]:
            print("\nRecent decisions:")
            for d in ctx["decisions"]:
                print(f"- {d['decision']} ({d['date']})")

        if ctx["questions"]:
            print("\nOpen questions:")
            for q in ctx["questions"]:
                print(f"- {q}")

    print("</ninho-file-context>\n")
    return True


def handle_pr_merge(pr_integration: PRIntegration) -> bool:
    """
    Handle automatic requirement completion when PR is merged.

    Returns:
        True if requirements were marked complete, False otherwise.
    """
    branch = pr_integration.get_current_branch()
    if not branch:
        return False

    count = pr_integration.mark_requirements_complete(branch)
    if count > 0:
        print(f"🪺 Auto-completed {count} requirement(s) in PRD")
        return True

    return False


def main():
    """Main entry point for Stop hook."""
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
    project_storage = ProjectStorage(cwd)
    prd_manager = PRD(project_storage)
    pr_integration = PRIntegration(project_storage)

    # Append response summary to today's prompt file (always, no throttle)
    response_summary = capture.get_last_assistant_summary()
    if response_summary:
        project_storage.append_response_summary(response_summary)

    # Check for PR-related commands (high priority, no throttle)
    pr_command = detect_pr_commands(transcript_path)
    if pr_command:
        if pr_command["type"] == "pr_create":
            handle_pr_creation(pr_integration, capture, prd_manager)
            return 0
        elif pr_command["type"] == "pr_merge":
            handle_pr_merge(pr_integration)
            return 0
        elif pr_command["type"] == "branch_push":
            # Pre-emptively link branch when pushing
            handle_pr_creation(pr_integration, capture, prd_manager)
            return 0

    # Check throttle for regular PRD updates
    if should_throttle():
        return 0

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

    # Create PRD if it doesn't exist
    if not prd_manager.exists(feature):
        prd_manager.create(feature)
        print(f"Created new PRD: {feature}")

    # Add modified files
    modified_files = capture.get_modified_files()
    for file_path in modified_files:
        prd_manager.add_file(feature, file_path)

    # Surface file-related context
    surface_file_context(prd_manager, modified_files)

    # Update throttle
    update_throttle()

    return 0


if __name__ == "__main__":
    sys.exit(main())
