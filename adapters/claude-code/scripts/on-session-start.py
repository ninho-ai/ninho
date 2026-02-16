#!/usr/bin/env python3
"""
SessionStart hook for Ninho.

Injects relevant PRD context at the beginning of each session.
Helps Claude understand project decisions and requirements from the start.

Also handles post-compaction context re-injection when source == "compact".
"""

import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add core library to path
SCRIPT_DIR = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(SCRIPT_DIR / "packages" / "core" / "src"))

from common import get_cwd
from prd import PRD
from storage import Storage, ProjectStorage
from summary import SummaryManager


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MEMORY_PREAMBLE = """\
## Ninho - Your Persistent Memory

This is your memory from past sessions. You do NOT start from scratch.

**Rules:**
- Before implementing a feature, check if a PRD exists below with requirements/decisions
- When asked about prior discussions, search prompt history: `/ninho:search <query>`
- Before making architectural decisions, check existing decisions in the relevant PRD
- Do not contradict decisions listed below without explicit user discussion
- For full memory status: `/ninho:status` | To search: `/ninho:search`
- To read a specific PRD: `read .ninho/prds/<name>.md`
"""

# Token-budget caps (in characters; ~4 chars/token)
MAX_FULL_PRD_CHARS = 2000
MAX_FULL_PRDS = 3
FULL_PRD_BUDGET = 6400
MAX_RECENT_PROMPTS = 15
MAX_WEEKLY_SUMMARY_CHARS = 800


# ---------------------------------------------------------------------------
# Helpers - PRD content extraction
# ---------------------------------------------------------------------------

def get_full_prd_content(prd_manager: PRD, prd_name: str) -> dict | None:
    """
    Read a PRD and extract actionable sections only.

    Extracts: Overview, Requirements, last 5 Decisions, Constraints,
    Open Questions.  Omits Session Log and Related Files (too verbose).

    Returns:
        {"name", "content", "char_count"} or None.
    """
    raw = prd_manager.read(prd_name)
    if not raw:
        return None

    sections = []

    # Overview
    m = re.search(r"## Overview\n(.*?)(?=\n## )", raw, re.DOTALL)
    if m and m.group(1).strip():
        sections.append(f"### Overview\n{m.group(1).strip()}")

    # Requirements
    m = re.search(r"## Requirements\n(.*?)(?=\n## )", raw, re.DOTALL)
    if m and m.group(1).strip():
        sections.append(f"### Requirements\n{m.group(1).strip()}")

    # Decisions (last 5 rows)
    decision_rows = re.findall(
        r"\| (\d{4}-\d{2}-\d{2}) \| ([^|]+) \| ([^|]+) \|", raw
    )
    if decision_rows:
        last5 = decision_rows[-5:]
        table = "| Date | Decision | Rationale |\n|------|----------|-----------|"
        for date, dec, rat in last5:
            table += f"\n| {date} | {dec.strip()} | {rat.strip()} |"
        sections.append(f"### Decisions (latest)\n{table}")

    # Constraints
    m = re.search(r"## Constraints\n(.*?)(?=\n## )", raw, re.DOTALL)
    if m:
        text = m.group(1).strip()
        if text and "(No constraints defined yet)" not in text:
            sections.append(f"### Constraints\n{text}")

    # Open Questions
    m = re.search(r"## Open Questions\n(.*?)(?=\n## )", raw, re.DOTALL)
    if m:
        text = m.group(1).strip()
        if text and "(No open questions)" not in text:
            sections.append(f"### Open Questions\n{text}")

    if not sections:
        return None

    content = "\n\n".join(sections)
    if len(content) > MAX_FULL_PRD_CHARS:
        content = content[:MAX_FULL_PRD_CHARS] + "\n...(truncated)"

    return {
        "name": prd_name,
        "content": content,
        "char_count": len(content),
    }


# ---------------------------------------------------------------------------
# Helpers - PRD summary (existing logic, kept intact)
# ---------------------------------------------------------------------------

def get_prd_summary(prd_manager: PRD, prd_name: str) -> dict | None:
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
    decision_pattern = r"\| (\d{4}-\d{2}-\d{2}) \| ([^|]+) \|"
    decisions = re.findall(decision_pattern, content)
    latest_decision = None
    if decisions:
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


# ---------------------------------------------------------------------------
# Helpers - recent learnings (existing logic, kept intact)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Helpers - recent prompt summaries (NEW)
# ---------------------------------------------------------------------------

def get_recent_prompt_summaries(project_storage: ProjectStorage, days: int = 3) -> list:
    """
    Read recent prompt files and extract summaries.

    Parses the format:
        ## HH:MM [feature]
        > prompt text
        <- response summary

    Returns:
        List of {"date", "time", "feature", "prompt_preview", "response_summary"}.
        Capped at MAX_RECENT_PROMPTS entries.
    """
    results = []
    today = datetime.now()

    for i in range(days):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        prompt_file = project_storage.prompts_path / f"{date_str}.md"

        if not prompt_file.exists():
            continue

        content = prompt_file.read_text()

        # Match prompt entries: ## HH:MM [feature]\n> prompt text
        # Optionally followed by: <- response summary
        pattern = (
            r"## (\d{2}:\d{2}) \[([^\]]+)\]\n"
            r"> (.+?)(?:\n\u2190 (.+?))?(?=\n## |\Z)"
        )
        for m in re.finditer(pattern, content, re.DOTALL):
            time_str = m.group(1)
            feature = m.group(2)
            prompt_text = m.group(3).strip()
            response_summary = m.group(4).strip() if m.group(4) else None

            # Truncate prompt to preview length
            preview = prompt_text[:60]
            if len(prompt_text) > 60:
                preview += "..."

            results.append({
                "date": date_str,
                "time": time_str,
                "feature": feature,
                "prompt_preview": preview,
                "response_summary": response_summary,
            })

    return results[:MAX_RECENT_PROMPTS]


# ---------------------------------------------------------------------------
# Helpers - latest weekly summary (NEW)
# ---------------------------------------------------------------------------

def get_latest_weekly_summary(project_storage: ProjectStorage) -> str | None:
    """
    Read the most recent weekly summary and extract Overview + Decisions sections.

    Returns:
        Extracted text (capped at MAX_WEEKLY_SUMMARY_CHARS) or None.
    """
    weeks = project_storage.list_summaries("weekly")
    if not weeks:
        return None

    latest_week = weeks[-1]  # list_summaries returns sorted
    summary_path = project_storage.get_summary_file("weekly", latest_week)
    if not summary_path.exists():
        return None

    content = summary_path.read_text()
    sections = []

    # Extract Overview
    m = re.search(r"## Overview\n(.*?)(?=\n## |\Z)", content, re.DOTALL)
    if m:
        sections.append(f"**{latest_week} Overview**\n{m.group(1).strip()}")

    # Extract Decisions Made
    m = re.search(r"## Decisions Made\n(.*?)(?=\n## |\Z)", content, re.DOTALL)
    if m:
        sections.append(f"**Key Decisions**\n{m.group(1).strip()}")

    if not sections:
        return None

    result = "\n\n".join(sections)
    if len(result) > MAX_WEEKLY_SUMMARY_CHARS:
        result = result[:MAX_WEEKLY_SUMMARY_CHARS] + "\n...(truncated)"

    return result


# ---------------------------------------------------------------------------
# Formatting - full context (startup / resume / clear)
# ---------------------------------------------------------------------------

def format_context(
    prds_full: list,
    prds_summary: list,
    learnings: list,
    recent_prompts: list,
    weekly_summary: str | None,
) -> str:
    """
    Format the full context block for session start injection.

    Rendering order:
    1. <ninho-context> + MEMORY_PREAMBLE
    2. Active PRDs (detailed)
    3. Active PRDs (overview)
    4. Stale Questions
    5. Recent Conversations
    6. Weekly Summary
    7. Recent Learnings
    8. </ninho-context>
    """
    lines = ["<ninho-context>", MEMORY_PREAMBLE]

    # --- Full PRDs (detailed) ---
    if prds_full:
        lines.append("## Active PRDs (detailed)")
        lines.append("")
        for prd in prds_full:
            title = prd["name"].replace("-", " ").title()
            lines.append(f"### {title}")
            lines.append(prd["content"])
            lines.append("")

    # --- Summary PRDs (overview) ---
    # Collect all stale questions across summary PRDs
    all_stale = []
    for prd in prds_summary:
        for q in prd.get("stale_questions", []):
            all_stale.append({"prd": prd["name"], **q})

    if prds_summary:
        lines.append("## Active PRDs (overview)")
        lines.append("")

        for prd in prds_summary:
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

    if not prds_full and not prds_summary:
        lines.append("## Active PRDs")
        lines.append("")
        lines.append("No PRDs found. Ninho will create them as you discuss features.")
        lines.append("")

    # --- Stale Questions ---
    # Also collect stale questions from full PRDs (if any exist in the summary data)
    if all_stale:
        lines.append("### Stale Questions (need attention)")
        for sq in all_stale[:5]:
            lines.append(f"- **{sq['prd']}**: {sq['text']} ({sq['days_old']} days old)")
        lines.append("")

    # --- Recent Conversations ---
    if recent_prompts:
        lines.append("## Recent Conversations")
        lines.append("")
        current_date = None
        for p in recent_prompts:
            if p["date"] != current_date:
                current_date = p["date"]
                lines.append(f"### {current_date}")
            summary_part = ""
            if p.get("response_summary"):
                summary_part = f" -> {p['response_summary']}"
            lines.append(f"- {p['time']} [{p['feature']}] {p['prompt_preview']}{summary_part}")
        lines.append("")

    # --- Weekly Summary ---
    if weekly_summary:
        lines.append("## Weekly Summary")
        lines.append("")
        lines.append(weekly_summary)
        lines.append("")

    # --- Recent Learnings ---
    if learnings:
        lines.append("## Recent Learnings")
        lines.append("")

        current_date = None
        for learning in learnings:
            if learning["date"] != current_date:
                current_date = learning["date"]
                lines.append(f"### {current_date}")

            text = learning["text"]
            if len(text) > 100:
                text = text[:100] + "..."

            lines.append(f"- [{learning['type']}] {text}")

        lines.append("")

    lines.append("</ninho-context>")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Formatting - compact re-injection (post-compaction)
# ---------------------------------------------------------------------------

def format_compact_context(
    prds_summary: list,
    snapshot: dict | None = None,
) -> str:
    """
    Format a lighter context block for post-compaction re-injection.

    Contains:
    - One-line reminder about compaction
    - PRD names with latest 2 decisions and open counts (top 5)
    - Active feature from session snapshot if available
    - Pointers to /ninho:search and PRD files
    """
    lines = [
        "<ninho-context-restored>",
        "Context was compacted. Your persistent memory is in `.ninho/`.",
        "",
    ]

    if snapshot and snapshot.get("active_feature"):
        lines.append(f"**Active feature**: {snapshot['active_feature']}")
        lines.append("")

    if snapshot and snapshot.get("modified_files"):
        files = snapshot["modified_files"][:5]
        lines.append(f"**Recently modified**: {', '.join(Path(f).name for f in files)}")
        lines.append("")

    if prds_summary:
        lines.append("## PRD Status")
        lines.append("")
        for prd in prds_summary[:5]:
            name = prd["name"].replace("-", " ").title()
            parts = []
            if prd["open_requirements"] > 0:
                parts.append(f"{prd['open_requirements']} open reqs")
            if prd["open_questions"] > 0:
                parts.append(f"{prd['open_questions']} questions")
            status = f" ({', '.join(parts)})" if parts else ""

            # Show latest decision inline
            decisions_text = ""
            if prd.get("latest_decision"):
                decisions_text = f" | Latest: {prd['latest_decision']['text'][:60]}"

            lines.append(f"- **{name}**{status}{decisions_text}")
        lines.append("")

    lines.append("Use `/ninho:search <query>` to find past discussions.")
    lines.append("Read full PRDs: `read .ninho/prds/<name>.md`")
    lines.append("</ninho-context-restored>")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Session snapshot management
# ---------------------------------------------------------------------------

def read_session_snapshot(project_storage: ProjectStorage) -> dict | None:
    """Read the session snapshot written by PreCompact."""
    snapshot_path = project_storage.ninho_path / ".session-snapshot.json"
    if not snapshot_path.exists():
        return None
    try:
        return json.loads(snapshot_path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def cleanup_session_files(project_storage: ProjectStorage) -> None:
    """Remove transient session files on fresh startup."""
    for name in (".session-snapshot.json", ".last-compact-seen"):
        path = project_storage.ninho_path / name
        if path.exists():
            try:
                path.unlink()
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Main entry point for SessionStart hook."""
    # Read hook input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 1

    cwd = get_cwd(input_data)
    source = input_data.get("source", "startup")

    # Initialize storage
    storage = Storage()
    project_storage = ProjectStorage(cwd)

    # Check if .ninho directory exists
    if not project_storage.ninho_path.exists():
        return 0

    # ------------------------------------------------------------------
    # Fresh session: cleanup transient files
    # ------------------------------------------------------------------
    if source in ("startup", "clear"):
        cleanup_session_files(project_storage)

    # ------------------------------------------------------------------
    # Auto-generate pending summaries (all sources)
    # ------------------------------------------------------------------
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
        print(f"Warning: Summary generation failed: {e}", file=sys.stderr)

    # ------------------------------------------------------------------
    # Build PRD data (shared across both paths)
    # ------------------------------------------------------------------
    prd_manager = PRD(project_storage)
    prd_names = prd_manager.list_prds()

    all_summaries = []
    for name in prd_names:
        summary = get_prd_summary(prd_manager, name)
        if summary:
            all_summaries.append(summary)

    # Sort by last updated (most recent first)
    all_summaries.sort(key=lambda x: x["days_since_update"])

    # ------------------------------------------------------------------
    # COMPACT path: lighter re-injection
    # ------------------------------------------------------------------
    if source == "compact":
        snapshot = read_session_snapshot(project_storage)
        context = format_compact_context(all_summaries, snapshot)
        print(context)
        return 0

    # ------------------------------------------------------------------
    # FULL path: startup / resume / clear
    # ------------------------------------------------------------------

    # Smart PRD selection: full content for recent, summaries for older
    prds_full = []
    prds_summary = []
    full_char_budget = FULL_PRD_BUDGET

    for prd_data in all_summaries:
        if (
            prd_data["days_since_update"] <= 7
            and len(prds_full) < MAX_FULL_PRDS
            and full_char_budget > 0
        ):
            full = get_full_prd_content(prd_manager, prd_data["name"])
            if full and full["char_count"] <= full_char_budget:
                prds_full.append(full)
                full_char_budget -= full["char_count"]
                continue
        # Falls through: use summary
        prds_summary.append(prd_data)

    # Get recent learnings
    learnings = get_recent_learnings(storage)

    # Get recent prompt summaries
    recent_prompts = get_recent_prompt_summaries(project_storage)

    # Get latest weekly summary
    weekly_summary = get_latest_weekly_summary(project_storage)

    # Only output if there's something to show
    if prds_full or prds_summary or learnings or recent_prompts or weekly_summary:
        context = format_context(
            prds_full, prds_summary, learnings, recent_prompts, weekly_summary
        )
        print(context)

    return 0


if __name__ == "__main__":
    sys.exit(main())
