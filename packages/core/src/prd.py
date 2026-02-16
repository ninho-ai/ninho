"""
PRD module for Ninho.

Handles creation and maintenance of Product Requirements Documents.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from .storage import ProjectStorage


class PRD:
    """Manage Product Requirements Documents."""

    TEMPLATE = """# {title}

## Overview
{overview}

## Requirements
{requirements}

## Decisions
| Date | Decision | Rationale |
|------|----------|-----------|
{decisions}

## Constraints
{constraints}

## Open Questions
{questions}

## Related Files
{files}

## Session Log
{session_log}
"""

    def __init__(self, project_storage: ProjectStorage):
        """
        Initialize PRD manager.

        Args:
            project_storage: ProjectStorage instance.
        """
        self.storage = project_storage

    def create(
        self,
        name: str,
        title: Optional[str] = None,
        overview: str = "",
    ) -> Path:
        """
        Create a new PRD file.

        Args:
            name: PRD name (used for filename).
            title: Display title. Defaults to formatted name.
            overview: Overview description.

        Returns:
            Path to created PRD file.
        """
        if title is None:
            title = name.replace("-", " ").replace("_", " ").title()

        content = self.TEMPLATE.format(
            title=title,
            overview=overview or f"Documentation for {title}.",
            requirements="- [ ] Initial requirement",
            decisions="",
            constraints="- (No constraints defined yet)",
            questions="- (No open questions)",
            files="- (No files tracked yet)",
            session_log=f"### {datetime.now().strftime('%Y-%m-%d')}\n- PRD created",
        )

        file_path = self.storage.get_prd_file(name)
        self.storage.write_file(file_path, content)
        return file_path

    def exists(self, name: str) -> bool:
        """Check if a PRD exists."""
        return self.storage.get_prd_file(name).exists()

    def read(self, name: str) -> Optional[str]:
        """Read PRD content."""
        return self.storage.read_file(self.storage.get_prd_file(name))

    def add_requirement(self, name: str, requirement: str) -> None:
        """
        Add a requirement to a PRD.

        Args:
            name: PRD name.
            requirement: Requirement text.
        """
        content = self.read(name)
        if not content:
            return

        # Find requirements section and add new requirement
        pattern = r"(## Requirements\n)(.*?)(\n## )"
        match = re.search(pattern, content, re.DOTALL)

        if match:
            requirements = match.group(2)
            new_requirement = f"- [ ] {requirement}\n"

            # Check if requirement already exists
            if requirement.lower() in requirements.lower():
                return

            new_content = content[:match.end(1)] + requirements + new_requirement + content[match.start(3):]
            self.storage.write_file(self.storage.get_prd_file(name), new_content)

    def add_decision(
        self,
        name: str,
        decision: str,
        rationale: str,
        date: Optional[datetime] = None,
    ) -> None:
        """
        Add a decision to a PRD.

        Args:
            name: PRD name.
            decision: Decision text.
            rationale: Rationale for the decision.
            date: Date of decision. Defaults to today.
        """
        content = self.read(name)
        if not content:
            return

        if date is None:
            date = datetime.now()
        date_str = date.strftime("%Y-%m-%d")

        # Find decisions table and add new row
        pattern = r"(\| Date \| Decision \| Rationale \|\n\|------\|----------\|-----------\|\n)(.*?)(\n\n## )"
        match = re.search(pattern, content, re.DOTALL)

        if match:
            existing = match.group(2)
            new_row = f"| {date_str} | {decision} | {rationale} |\n"

            # Check if decision already exists
            if decision.lower() in existing.lower():
                return

            new_content = (
                content[:match.end(1)]
                + existing
                + new_row
                + content[match.start(3):]
            )
            self.storage.write_file(self.storage.get_prd_file(name), new_content)

    def add_constraint(self, name: str, constraint: str) -> None:
        """
        Add a constraint to a PRD.

        Args:
            name: PRD name.
            constraint: Constraint text.
        """
        content = self.read(name)
        if not content:
            return

        # Find constraints section
        pattern = r"(## Constraints\n)(.*?)(\n## )"
        match = re.search(pattern, content, re.DOTALL)

        if match:
            constraints = match.group(2)

            # Remove placeholder if present
            if "(No constraints defined yet)" in constraints:
                constraints = ""

            new_constraint = f"- {constraint}\n"

            # Check if constraint already exists
            if constraint.lower() in constraints.lower():
                return

            new_content = (
                content[:match.end(1)]
                + constraints
                + new_constraint
                + content[match.start(3):]
            )
            self.storage.write_file(self.storage.get_prd_file(name), new_content)

    def add_question(self, name: str, question: str) -> None:
        """
        Add an open question to a PRD.

        Args:
            name: PRD name.
            question: Question text.
        """
        content = self.read(name)
        if not content:
            return

        pattern = r"(## Open Questions\n)(.*?)(\n## )"
        match = re.search(pattern, content, re.DOTALL)

        if match:
            questions = match.group(2)

            # Remove placeholder if present
            if "(No open questions)" in questions:
                questions = ""

            date_str = datetime.now().strftime("%Y-%m-%d")
            new_question = f"- {question} *(asked {date_str})*\n"

            # Check if question already exists
            if question.lower() in questions.lower():
                return

            new_content = (
                content[:match.end(1)]
                + questions
                + new_question
                + content[match.start(3):]
            )
            self.storage.write_file(self.storage.get_prd_file(name), new_content)

    def remove_question(self, name: str, question_substring: str) -> None:
        """
        Remove an answered question from a PRD.

        Args:
            name: PRD name.
            question_substring: Part of the question to match.
        """
        content = self.read(name)
        if not content:
            return

        pattern = r"(## Open Questions\n)(.*?)(\n## )"
        match = re.search(pattern, content, re.DOTALL)

        if match:
            questions = match.group(2)
            lines = questions.split("\n")
            new_lines = [
                line for line in lines
                if question_substring.lower() not in line.lower()
            ]

            if not new_lines or all(not line.strip() for line in new_lines):
                new_lines = ["- (No open questions)"]

            new_content = (
                content[:match.end(1)]
                + "\n".join(new_lines)
                + "\n"
                + content[match.start(3):]
            )
            self.storage.write_file(self.storage.get_prd_file(name), new_content)

    def add_file(self, name: str, file_path: str) -> None:
        """
        Add a related file to a PRD.

        Args:
            name: PRD name.
            file_path: Path to the related file.
        """
        content = self.read(name)
        if not content:
            return

        pattern = r"(## Related Files\n)(.*?)(\n## )"
        match = re.search(pattern, content, re.DOTALL)

        if match:
            files = match.group(2)

            # Remove placeholder if present
            if "(No files tracked yet)" in files:
                files = ""

            new_file = f"- `{file_path}`\n"

            # Check if file already exists
            if file_path in files:
                return

            new_content = (
                content[:match.end(1)]
                + files
                + new_file
                + content[match.start(3):]
            )
            self.storage.write_file(self.storage.get_prd_file(name), new_content)

    def add_session_log(
        self,
        name: str,
        entry: str,
        prompt_ref: Optional[str] = None,
    ) -> None:
        """
        Add an entry to the session log.

        Args:
            name: PRD name.
            entry: Log entry text.
            prompt_ref: Optional reference to prompt file.
        """
        content = self.read(name)
        if not content:
            return

        date_str = datetime.now().strftime("%Y-%m-%d")

        # Format entry
        if prompt_ref:
            log_entry = f"- {entry} ([prompt]({prompt_ref}))\n"
        else:
            log_entry = f"- {entry}\n"

        # Check if today's section exists
        today_header = f"### {date_str}"

        if today_header in content:
            # Add to existing day section
            pattern = rf"({re.escape(today_header)}\n)(.*?)(\n### |\Z)"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                existing = match.group(2)
                new_content = (
                    content[:match.end(1)]
                    + existing
                    + log_entry
                    + content[match.start(3):]
                )
                self.storage.write_file(self.storage.get_prd_file(name), new_content)
        else:
            # Add new day section
            pattern = r"(## Session Log\n)"
            match = re.search(pattern, content)
            if match:
                new_section = f"{today_header}\n{log_entry}"
                new_content = (
                    content[:match.end(1)]
                    + new_section
                    + content[match.end(1):]
                )
                self.storage.write_file(self.storage.get_prd_file(name), new_content)

    def get_summary(self, name: str) -> dict:
        """
        Get a summary of a PRD.

        Args:
            name: PRD name.

        Returns:
            Dictionary with summary information.
        """
        content = self.read(name)
        if not content:
            return {}

        # Count requirements
        req_pattern = r"- \[([ x])\]"
        requirements = re.findall(req_pattern, content)
        open_reqs = requirements.count(" ")
        completed_reqs = requirements.count("x")

        # Count open questions
        questions_pattern = r"## Open Questions\n(.*?)\n## "
        questions_match = re.search(questions_pattern, content, re.DOTALL)
        open_questions = 0
        if questions_match:
            questions = questions_match.group(1)
            if "(No open questions)" not in questions:
                open_questions = len([
                    line for line in questions.split("\n")
                    if line.strip().startswith("-")
                ])

        # Get latest decision
        decisions_pattern = r"\| (\d{4}-\d{2}-\d{2}) \| ([^|]+) \|"
        decisions = re.findall(decisions_pattern, content)
        latest_decision = decisions[-1] if decisions else None

        return {
            "name": name,
            "open_requirements": open_reqs,
            "completed_requirements": completed_reqs,
            "open_questions": open_questions,
            "latest_decision": latest_decision,
            "total_decisions": len(decisions),
        }
