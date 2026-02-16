#!/usr/bin/env python3
"""
Ninho CLI - Command-line interface for AI coding context management.

Usage:
    ninho status          Show project status
    ninho prds            List all PRDs
    ninho search <query>  Search PRDs and prompts
    ninho digest          Generate weekly digest
    ninho update          Update Ninho to latest version
    ninho doctor          Check installation health
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add core library to path for development
SCRIPT_DIR = Path(__file__).parent.parent.parent
CORE_PATH = SCRIPT_DIR / "core" / "src"
if CORE_PATH.exists():
    sys.path.insert(0, str(CORE_PATH))

try:
    from storage import Storage, ProjectStorage
    from prd import PRD
    from pr_integration import PRIntegration
except ImportError:
    # Fall back to installed package
    from ninho_core import Storage, ProjectStorage, PRD, PRIntegration


def cmd_status(args):
    """Show project status."""
    cwd = os.getcwd()
    project_storage = ProjectStorage(cwd)

    if not project_storage.ninho_path.exists():
        print("Ninho Status")
        print()
        print("No Ninho data found for this project.")
        print()
        print("Ninho works automatically in the background:")
        print("- PRDs created when you discuss requirements and decisions")
        print("- Learnings captured when you make corrections")
        print("- PRs linked when you run `gh pr create`")
        print()
        print("Just keep coding with Claude Code!")
        return 0

    prd_manager = PRD(project_storage)
    pr_integration = PRIntegration(project_storage)

    print("Ninho Status")
    print()

    # Get PRD summaries
    prd_names = prd_manager.list_prds()

    # Collect stale questions
    all_stale = []
    for name in prd_names:
        stale = prd_manager.get_stale_questions(name)
        for q in stale:
            all_stale.append({"prd": name, **q})

    if all_stale:
        print("## Attention Needed")
        print()
        print("### Stale Questions (>7 days old)")
        for sq in all_stale[:5]:
            print(f"- **{sq['prd']}**: {sq['text']} ({sq['days_old']} days)")
        print()

    # PRD table
    print("## Project PRDs")
    print()
    print("| PRD | Open | Done | Questions | Latest Decision |")
    print("|-----|------|------|-----------|-----------------|")

    for name in prd_names:
        summary = prd_manager.get_summary(name)
        latest = summary.get("latest_decision")
        latest_str = f"{latest[1][:20]}... ({latest[0]})" if latest else "-"
        print(
            f"| {name} | {summary['open_requirements']} | "
            f"{summary['completed_requirements']} | {summary['open_questions']} | "
            f"{latest_str} |"
        )

    print()

    # PR mappings
    mappings = pr_integration._load_mappings()
    active_branches = [b for b, m in mappings.items() if not m.get("merged")]

    if active_branches:
        print("## Active Branches")
        print()
        print("| Branch | Linked PRD | Requirements |")
        print("|--------|------------|--------------|")
        for branch in active_branches[:5]:
            mapping = mappings[branch]
            reqs = ", ".join(mapping["requirements"][:2])
            if len(mapping["requirements"]) > 2:
                reqs += "..."
            print(f"| {branch} | {mapping['prd']} | {reqs} |")
        print()

    # Stats
    print("---")
    print(f"PRDs: {len(prd_names)} | Branches tracked: {len(active_branches)}")

    return 0


def cmd_prds(args):
    """List all PRDs."""
    cwd = os.getcwd()
    project_storage = ProjectStorage(cwd)
    prd_manager = PRD(project_storage)

    prd_names = prd_manager.list_prds()

    if not prd_names:
        print("No PRDs found in this project.")
        print()
        print("PRDs are created automatically when you discuss features.")
        return 0

    print(f"Found {len(prd_names)} PRDs:")
    print()

    for i, name in enumerate(prd_names, 1):
        summary = prd_manager.get_summary(name)
        prd_path = project_storage.get_prd_file(name)

        total_reqs = summary["open_requirements"] + summary["completed_requirements"]
        pct = (
            int(summary["completed_requirements"] / total_reqs * 100)
            if total_reqs > 0
            else 0
        )

        print(f"## {i}. {name.replace('-', ' ').title()}")
        print(f"   File: .ninho/prds/{name}.md")
        print()
        print(
            f"   Requirements: {summary['open_requirements']} open / "
            f"{summary['completed_requirements']} completed ({pct}% done)"
        )
        print(f"   Decisions: {summary['total_decisions']} made")
        print(f"   Questions: {summary['open_questions']} open")
        print()
        print("---")
        print()

    return 0


def cmd_search(args):
    """Search PRDs and prompts."""
    query = args.query
    cwd = os.getcwd()
    project_storage = ProjectStorage(cwd)

    results = []

    # Search PRDs
    prds_path = project_storage.prds_path
    if prds_path.exists():
        for prd_file in prds_path.glob("*.md"):
            content = prd_file.read_text()
            if query.lower() in content.lower():
                # Find matching lines
                for i, line in enumerate(content.split("\n"), 1):
                    if query.lower() in line.lower():
                        results.append({
                            "source": f"{prd_file.stem} (PRD)",
                            "line": i,
                            "text": line.strip()[:80],
                        })

    # Search prompts
    prompts_path = project_storage.prompts_path
    if prompts_path.exists():
        for prompt_file in prompts_path.glob("*.md"):
            content = prompt_file.read_text()
            if query.lower() in content.lower():
                for i, line in enumerate(content.split("\n"), 1):
                    if query.lower() in line.lower():
                        results.append({
                            "source": f"{prompt_file.stem} (prompts)",
                            "line": i,
                            "text": line.strip()[:80],
                        })

    if not results:
        print(f'No results found for "{query}"')
        return 0

    print(f'Found {len(results)} results for "{query}":')
    print()

    for r in results[:20]:
        print(f"## {r['source']}:{r['line']}")
        print(f"   {r['text']}")
        print()

    if len(results) > 20:
        print(f"... and {len(results) - 20} more results")

    return 0


def cmd_digest(args):
    """Generate weekly digest."""
    days = args.days or 7
    cwd = os.getcwd()
    project_storage = ProjectStorage(cwd)
    prd_manager = PRD(project_storage)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    print(f"# Digest: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print()

    # Collect decisions from PRDs
    all_decisions = []
    prd_names = prd_manager.list_prds()

    for name in prd_names:
        content = prd_manager.read(name)
        if not content:
            continue

        import re
        pattern = r"\| (\d{4}-\d{2}-\d{2}) \| ([^|]+) \| ([^|]+) \|"
        for match in re.finditer(pattern, content):
            date_str = match.group(1)
            try:
                decision_date = datetime.strptime(date_str, "%Y-%m-%d")
                if start_date <= decision_date <= end_date:
                    all_decisions.append({
                        "prd": name,
                        "date": date_str,
                        "decision": match.group(2).strip(),
                        "rationale": match.group(3).strip(),
                    })
            except ValueError:
                continue

    if all_decisions:
        print(f"## Decisions Made ({len(all_decisions)})")
        print()
        current_prd = None
        for d in sorted(all_decisions, key=lambda x: x["prd"]):
            if d["prd"] != current_prd:
                current_prd = d["prd"]
                print(f"### {current_prd.replace('-', ' ').title()}")
            print(f"- **{d['decision']}** - {d['rationale']} ({d['date']})")
        print()

    print("---")
    print(f"Generated by Ninho CLI")

    return 0


def cmd_update(args):
    """Update Ninho to latest version."""
    print("Updating Ninho...")

    ninho_path = Path.home() / ".ninho-plugin"
    if ninho_path.exists():
        result = subprocess.run(
            ["git", "pull", "origin", "main"],
            cwd=str(ninho_path),
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("Ninho updated successfully!")
            print(result.stdout)
        else:
            print("Update failed:")
            print(result.stderr)
            return 1
    else:
        print("Ninho installation not found at ~/.ninho-plugin")
        print("Please reinstall using the install script.")
        return 1

    return 0


def cmd_doctor(args):
    """Check installation health."""
    print("Ninho Doctor")
    print()

    checks = []

    # Check global storage
    global_path = Path.home() / ".ninho"
    checks.append(("Global storage (~/.ninho)", global_path.exists()))

    # Check daily directory
    daily_path = global_path / "daily"
    checks.append(("Daily learnings directory", daily_path.exists()))

    # Check project storage
    cwd = os.getcwd()
    project_path = Path(cwd) / ".ninho"
    checks.append(("Project storage (.ninho)", project_path.exists()))

    # Check plugin installation
    plugin_path = Path.home() / ".ninho-plugin"
    checks.append(("Plugin installation", plugin_path.exists()))

    # Check Claude settings
    claude_settings = Path.home() / ".claude" / "settings.json"
    checks.append(("Claude settings file", claude_settings.exists()))

    print("Health Checks:")
    print()
    all_ok = True
    for name, status in checks:
        icon = "OK" if status else "MISSING"
        print(f"  [{icon}] {name}")
        if not status:
            all_ok = False

    print()
    if all_ok:
        print("All checks passed! Ninho is ready to use.")
    else:
        print("Some checks failed. Run `ninho update` or reinstall.")

    return 0 if all_ok else 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="ninho",
        description="CLI for AI coding context management",
    )
    parser.add_argument(
        "--version", action="version", version="%(prog)s 1.0.0"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # status
    subparsers.add_parser("status", help="Show project status")

    # prds
    subparsers.add_parser("prds", help="List all PRDs")

    # search
    search_parser = subparsers.add_parser("search", help="Search PRDs and prompts")
    search_parser.add_argument("query", help="Search query")

    # digest
    digest_parser = subparsers.add_parser("digest", help="Generate weekly digest")
    digest_parser.add_argument(
        "--days", type=int, default=7, help="Number of days to include"
    )

    # update
    subparsers.add_parser("update", help="Update Ninho to latest version")

    # doctor
    subparsers.add_parser("doctor", help="Check installation health")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    commands = {
        "status": cmd_status,
        "prds": cmd_prds,
        "search": cmd_search,
        "digest": cmd_digest,
        "update": cmd_update,
        "doctor": cmd_doctor,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
