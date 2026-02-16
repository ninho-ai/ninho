"""
PR Integration module for Ninho.

Handles linking PRs to PRD requirements and generating PR context.
"""

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from .storage import ProjectStorage
except ImportError:
    from storage import ProjectStorage


class PRIntegration:
    """Manage PR-to-PRD linking and context generation."""

    def __init__(self, project_storage: ProjectStorage):
        """
        Initialize PR integration.

        Args:
            project_storage: ProjectStorage instance.
        """
        self.storage = project_storage
        self.mappings_file = self.storage.ninho_path / "pr-mappings.json"

    def _load_mappings(self) -> dict:
        """Load PR-to-requirements mappings."""
        if self.mappings_file.exists():
            try:
                return json.loads(self.mappings_file.read_text())
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_mappings(self, mappings: dict) -> None:
        """Save PR-to-requirements mappings."""
        self.mappings_file.parent.mkdir(parents=True, exist_ok=True)
        self.mappings_file.write_text(json.dumps(mappings, indent=2))

    def get_current_branch(self) -> Optional[str]:
        """Get the current git branch name."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=str(self.storage.project_path),
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def detect_prd_from_branch(self, branch: str) -> Optional[str]:
        """
        Detect PRD name from branch name.

        Args:
            branch: Git branch name.

        Returns:
            PRD name or None if not detected.
        """
        # Common branch patterns
        patterns = [
            (r"^(?:feat|fix|feature)/auth[-_]", "auth-system"),
            (r"^(?:feat|fix|feature)/api[-_]", "api-integration"),
            (r"^(?:feat|fix|feature)/dashboard[-_]", "user-dashboard"),
            (r"^(?:feat|fix|feature)/user[-_]", "user-management"),
            (r"^(?:feat|fix|feature)/payment[-_]", "payments"),
            (r"^(?:feat|fix|feature)/notification[-_]", "notifications"),
        ]

        for pattern, prd_name in patterns:
            if re.match(pattern, branch, re.IGNORECASE):
                return prd_name

        # Try to extract feature name from branch
        match = re.match(r"^(?:feat|fix|feature)/([a-z0-9-]+)", branch, re.IGNORECASE)
        if match:
            return match.group(1)

        return None

    def detect_prd_from_files(self) -> Optional[str]:
        """Detect PRD from modified files in current branch."""
        try:
            # Get files changed compared to main/master
            for base in ["main", "master"]:
                result = subprocess.run(
                    ["git", "diff", base, "--name-only"],
                    capture_output=True,
                    text=True,
                    cwd=str(self.storage.project_path),
                )
                if result.returncode == 0 and result.stdout.strip():
                    files = result.stdout.strip().split("\n")
                    return self._infer_prd_from_files(files)
        except Exception:
            pass
        return None

    def _infer_prd_from_files(self, files: list[str]) -> Optional[str]:
        """Infer PRD name from list of file paths."""
        # Count directory occurrences
        dir_counts = {}
        for file_path in files:
            parts = Path(file_path).parts
            if len(parts) > 1:
                # Use second directory if first is 'src'
                key = parts[1] if parts[0] == "src" and len(parts) > 1 else parts[0]
                dir_counts[key] = dir_counts.get(key, 0) + 1

        if dir_counts:
            # Return most common directory
            most_common = max(dir_counts, key=dir_counts.get)
            return most_common.replace("_", "-")

        return None

    def get_prd_requirements(self, prd_name: str) -> list[dict]:
        """
        Get requirements from a PRD.

        Args:
            prd_name: Name of the PRD.

        Returns:
            List of requirement dictionaries with 'text' and 'completed' keys.
        """
        prd_path = self.storage.get_prd_file(prd_name)
        if not prd_path.exists():
            return []

        content = prd_path.read_text()
        requirements = []

        # Find requirements section
        req_pattern = r"## Requirements\n(.*?)(?:\n## |\Z)"
        match = re.search(req_pattern, content, re.DOTALL)

        if match:
            req_section = match.group(1)
            for line in req_section.split("\n"):
                # Match checkbox items
                checkbox_match = re.match(r"- \[([ x])\] (.+)", line)
                if checkbox_match:
                    requirements.append({
                        "text": checkbox_match.group(2).strip(),
                        "completed": checkbox_match.group(1) == "x",
                    })

        return requirements

    def link_branch_to_requirements(
        self,
        branch: str,
        prd_name: str,
        requirements: list[str],
    ) -> None:
        """
        Link a branch to PRD requirements.

        Args:
            branch: Git branch name.
            prd_name: PRD name.
            requirements: List of requirement texts to link.
        """
        mappings = self._load_mappings()
        mappings[branch] = {
            "prd": prd_name,
            "requirements": requirements,
            "created": datetime.now().isoformat(),
            "merged": False,
        }
        self._save_mappings(mappings)

    def get_branch_mapping(self, branch: str) -> Optional[dict]:
        """Get the mapping for a branch."""
        mappings = self._load_mappings()
        return mappings.get(branch)

    def get_pr_info(self) -> Optional[dict]:
        """Get PR info for current branch using gh CLI."""
        try:
            result = subprocess.run(
                ["gh", "pr", "view", "--json", "number,url,title,state"],
                capture_output=True,
                text=True,
                cwd=str(self.storage.project_path),
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception:
            pass
        return None

    def generate_pr_context(self, branch: str) -> Optional[str]:
        """
        Generate PR context markdown from linked PRD.

        Args:
            branch: Git branch name.

        Returns:
            Markdown context string or None if no mapping.
        """
        mapping = self.get_branch_mapping(branch)
        if not mapping:
            return None

        prd_name = mapping["prd"]
        linked_requirements = mapping["requirements"]

        prd_path = self.storage.get_prd_file(prd_name)
        if not prd_path.exists():
            return None

        content = prd_path.read_text()

        # Build context
        lines = [
            "## Context from PRD",
            "",
            f"**Feature**: {prd_name.replace('-', ' ').title()} ([PRD](.ninho/prds/{prd_name}.md))",
            "",
        ]

        # Requirements addressed
        lines.append("### Requirements Addressed")
        for req in linked_requirements:
            lines.append(f"- [x] {req}")
        lines.append("")

        # Extract decisions
        decisions = self._extract_decisions(content)
        if decisions:
            lines.append("### Decisions Made")
            lines.append("| Decision | Rationale |")
            lines.append("|----------|-----------|")
            for decision in decisions[:5]:  # Limit to 5 most recent
                lines.append(f"| {decision['decision']} | {decision['rationale']} |")
            lines.append("")

        # Extract constraints
        constraints = self._extract_constraints(content)
        if constraints:
            lines.append("### Constraints Considered")
            for constraint in constraints[:3]:  # Limit to 3
                lines.append(f"- {constraint}")
            lines.append("")

        lines.append("---")
        lines.append("*Generated by [Ninho](https://ninho.ai) - AI coding context management*")

        return "\n".join(lines)

    def _extract_decisions(self, content: str) -> list[dict]:
        """Extract decisions from PRD content."""
        decisions = []
        pattern = r"\| (\d{4}-\d{2}-\d{2}) \| ([^|]+) \| ([^|]+) \|"
        for match in re.finditer(pattern, content):
            decisions.append({
                "date": match.group(1),
                "decision": match.group(2).strip(),
                "rationale": match.group(3).strip(),
            })
        return decisions

    def _extract_constraints(self, content: str) -> list[str]:
        """Extract constraints from PRD content."""
        constraints = []
        pattern = r"## Constraints\n(.*?)(?:\n## |\Z)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            for line in match.group(1).split("\n"):
                if line.strip().startswith("- ") and "No constraints" not in line:
                    constraints.append(line.strip()[2:])
        return constraints

    def mark_requirements_complete(self, branch: str) -> int:
        """
        Mark linked requirements as complete in the PRD.

        Args:
            branch: Git branch name.

        Returns:
            Number of requirements marked complete.
        """
        mapping = self.get_branch_mapping(branch)
        if not mapping or mapping.get("merged"):
            return 0

        prd_name = mapping["prd"]
        requirements = mapping["requirements"]

        prd_path = self.storage.get_prd_file(prd_name)
        if not prd_path.exists():
            return 0

        content = prd_path.read_text()
        count = 0

        for req in requirements:
            # Escape special regex characters in requirement
            escaped_req = re.escape(req)
            pattern = rf"- \[ \] {escaped_req}"
            replacement = f"- [x] {req}"
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                count += 1

        if count > 0:
            prd_path.write_text(content)

            # Mark as merged in mappings
            mappings = self._load_mappings()
            if branch in mappings:
                mappings[branch]["merged"] = True
                mappings[branch]["merged_at"] = datetime.now().isoformat()
                self._save_mappings(mappings)

        return count

    def add_pr_to_prd(
        self,
        prd_name: str,
        pr_number: int,
        pr_url: str,
        branch: str,
        requirements: list[str],
        status: str = "Open",
    ) -> None:
        """
        Add PR to the PRD's Pull Requests table.

        Args:
            prd_name: PRD name.
            pr_number: PR number.
            pr_url: PR URL.
            branch: Branch name.
            requirements: List of requirements addressed.
            status: PR status (Open, Merged, Closed).
        """
        prd_path = self.storage.get_prd_file(prd_name)
        if not prd_path.exists():
            return

        content = prd_path.read_text()

        # Format status emoji
        status_emoji = {"Open": "🔄", "Merged": "✅", "Closed": "❌"}.get(status, "🔄")

        # Format requirements list
        req_text = ", ".join(requirements[:2])
        if len(requirements) > 2:
            req_text += f" (+{len(requirements) - 2} more)"

        new_row = f"| [#{pr_number}]({pr_url}) | `{branch}` | {status_emoji} {status} | {req_text} |\n"

        # Find Pull Requests table
        pattern = r"(\| PR \| Branch \| Status \| Requirements Addressed \|\n\|----\|--------\|--------\|------------------------\|\n)"
        match = re.search(pattern, content)

        if match:
            # Check if PR already in table
            if f"[#{pr_number}]" in content:
                # Update existing row
                old_row_pattern = rf"\| \[#{pr_number}\][^\n]+\n"
                content = re.sub(old_row_pattern, new_row, content)
            else:
                # Add new row
                insert_pos = match.end()
                content = content[:insert_pos] + new_row + content[insert_pos:]

            prd_path.write_text(content)
