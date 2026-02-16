#!/usr/bin/env python3
"""
SessionStart hook for Ninho.

Injects relevant PRD context at the beginning of each session.
Helps Claude understand project decisions and requirements from the start.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add core library to path
SCRIPT_DIR = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(SCRIPT_DIR / "packages" / "core" / "src"))

from prd import PRD
from storage import Storage, ProjectStorage
from summary import SummaryManager


def get_prd_summary(prd_manager: PRD, prd_name: str) -> dict:
    """
    Get a summary of a PRD for context injection.

    Returns:
        Dictionary with PRD summary info.
    """
    prd_path = prd_manager.storage.get_prd_file(prd_name)
    if not prd_path.exists():
        return None

    content = prd_path.read_text()

    # Count requirements
    open_reqs = content.count("- [ ]")
    done_reqs = content.count("- [x]")

    # Count open questions
    open_questions = 0
    in_questions_section = False
    for line in content.split("\n"):
        if line.startswith("## Open Questions"):
            in_questions_section = True
        elif line.startswith("## ") and in_questions_section:
            in_questions_section = False
        elif in_questions_section and line.strip().startswith("- "):
            open_questions += 1

    # Get latest decision
    import re
    decision_pattern = r"\| (\d{4}-\d{2}-\d{2}) \| ([^|]+) \|"
    decisions = re.findall(decision_pattern, content)
    latest_decision = None
    if decisions:
        # Sort by date descending
        decisions.sort(key=lambda x: x[0], reverse=True)
        latest_decision = {
            "date": decisions[0][0],
            "text": decisions[0][1].strip(),
        }

    # Get last modified time
    mtime = prd_path.stat().st_mtime
    last_modified = datetime.fromtimestamp(mtime)
    days_ago = (datetime.now() - last_modified).days

    # Get stale questions
    stale_questions = prd_manager.get_stale_questions(prd_name, days_threshold=7)

    return {
        "name": prd_name,
        "open_requirements": open_reqs,
        "done_requirements": done_reqs,
        "open_questions": open_questions,
        "stale_questions": stale_questions,
        "latest_decision": latest_decision,
        "days_since_update": days_ago,
    }


def get_recent_learnings(storage: Storage, days: int = 3) -> list:
    """
    Get recent learnings from the last N days.

    Returns:
        List of learning entries.
    """
    learnings = []
    today = datetime.now()

    for i in range(days):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        daily_file = storage.daily_path / f"{date_str}.md"

        if daily_file.exists():
            content = daily_file.read_text()
            # Extract learning entries
            import re
            pattern = r"## \[(\w+)\] (\d{2}:\d{2}:\d{2})\n\n> (.+?)(?=\n\n\*\*Signal|\n\n## |\Z)"
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                learnings.append({
                    "type": match[0],
                    "date": date_str,
                    "time": match[1],
                    "text": match[2].strip(),
                })

    return learnings[:10]  # Limit to 10 most recent


def format_context(prds: list, learnings: list) -> str:
    """
    Format PRD and learnings context for injection.

    Returns:
        Formatted markdown context string.
    """
    lines = ["<ninho-context>", "## Active PRDs for this project", ""]

    # Collect all stale questions across PRDs
    all_stale = []
    for prd in prds:
        for q in prd.get("stale_questions", []):
            all_stale.append({"prd": prd["name"], **q})

    # Show stale questions prominently if any
    if all_stale:
        lines.append("### Stale Questions (need attention)")
        for sq in all_stale[:5]:  # Limit to 5
            lines.append(f"- **{sq['prd']}**: {sq['text']} ({sq['days_old']} days old)")
        lines.append("")

    if not prds:
        lines.append("No PRDs found. Ninho will create them as you discuss features.")
        lines.append("")
    else:
        for prd in prds:
            status = []
            if prd["open_requirements"] > 0:
                status.append(f"{prd['open_requirements']} open")
            if prd["done_requirements"] > 0:
                status.append(f"{prd['done_requirements']} done")
            if prd["open_questions"] > 0:
                status.append(f"{prd['open_questions']} questions")

            freshness = ""
            if prd["days_since_update"] == 0:
                freshness = "today"
            elif prd["days_since_update"] == 1:
                freshness = "yesterday"
            else:
                freshness = f"{prd['days_since_update']} days ago"

            lines.append(f"### {prd['name'].replace('-', ' ').title()}")
            lines.append(f"- Status: {', '.join(status) if status else 'No requirements'}")
            lines.append(f"- Last updated: {freshness}")

            if prd["latest_decision"]:
                lines.append(f"- Latest decision: {prd['latest_decision']['text']} ({prd['latest_decision']['date']})")

            if prd["open_questions"] > 0 and not prd.get("stale_questions"):
                lines.append(f"- Has {prd['open_questions']} open question(s)")

            lines.append("")

    if learnings:
        lines.append("## Recent Learnings")
        lines.append("")

        current_date = None
        for learning in learnings:
            if learning["date"] != current_date:
                current_date = learning["date"]
                lines.append(f"### {current_date}")

            # Truncate long learnings
            text = learning["text"]
            if len(text) > 100:
                text = text[:100] + "..."

            lines.append(f"- [{learning['type']}] {text}")

        lines.append("")

    lines.append("</ninho-context>")

    return "\n".join(lines)


def main():
    """Main entry point for SessionStart hook."""
    # Read hook input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 1

    cwd = input_data.get("cwd", os.getcwd())

    # Initialize storage
    storage = Storage()
    project_storage = ProjectStorage(cwd)

    # Check if .ninho directory exists
    if not project_storage.ninho_path.exists():
        # No Ninho data for this project yet
        return 0

    # Check for pending summaries at period boundaries
    try:
        summary_manager = SummaryManager(project_storage, storage)
        pending = summary_manager.check_pending_summaries()

        for period_type, period in pending:
            if period_type == SummaryManager.WEEKLY:
                summary_manager.generate_weekly_summary(period)
                print(f"Generated weekly summary for {period}", file=sys.stderr)
            elif period_type == SummaryManager.MONTHLY:
                summary_manager.generate_monthly_summary(period)
                print(f"Generated monthly summary for {period}", file=sys.stderr)
            elif period_type == SummaryManager.YEARLY:
                summary_manager.generate_yearly_summary(period)
                print(f"Generated yearly summary for {period}", file=sys.stderr)
    except Exception as e:
        # Don't fail session start if summary generation fails
        print(f"Warning: Summary generation failed: {e}", file=sys.stderr)

    # Get all PRDs
    prd_manager = PRD(project_storage)
    prd_names = prd_manager.list_prds()

    prds = []
    for name in prd_names:
        summary = get_prd_summary(prd_manager, name)
        if summary:
            prds.append(summary)

    # Sort by last updated (most recent first)
    prds.sort(key=lambda x: x["days_since_update"])

    # Get recent learnings
    learnings = get_recent_learnings(storage)

    # Only output if there's something to show
    if prds or learnings:
        context = format_context(prds, learnings)
        print(context)

    return 0


if __name__ == "__main__":
    sys.exit(main())
