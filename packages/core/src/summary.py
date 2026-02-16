"""
Summary module for Ninho.

Handles hierarchical summary generation (weekly, monthly, yearly)
with breadcrumb references to original prompts.
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

try:
    from .storage import Storage, ProjectStorage
except ImportError:
    from storage import Storage, ProjectStorage


class SummaryManager:
    """Manages hierarchical summary generation."""

    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

    def __init__(
        self,
        project_storage: ProjectStorage,
        global_storage: Optional[Storage] = None,
    ):
        """
        Initialize summary manager.

        Args:
            project_storage: ProjectStorage instance for project data.
            global_storage: Storage instance for global data (learnings).
        """
        self.project_storage = project_storage
        self.global_storage = global_storage or Storage()
        self._state: Optional[dict] = None

    # ==================== Period Detection ====================

    def get_current_week(self, date: Optional[datetime] = None) -> str:
        """Get ISO week string for a date (e.g., '2026-W07')."""
        if date is None:
            date = datetime.now()
        return f"{date.isocalendar()[0]}-W{date.isocalendar()[1]:02d}"

    def get_current_month(self, date: Optional[datetime] = None) -> str:
        """Get month string for a date (e.g., '2026-02')."""
        if date is None:
            date = datetime.now()
        return date.strftime("%Y-%m")

    def get_current_year(self, date: Optional[datetime] = None) -> str:
        """Get year string for a date (e.g., '2026')."""
        if date is None:
            date = datetime.now()
        return date.strftime("%Y")

    def get_previous_week(self, date: Optional[datetime] = None) -> str:
        """Get previous week's ISO week string."""
        if date is None:
            date = datetime.now()
        prev = date - timedelta(days=7)
        return self.get_current_week(prev)

    def get_previous_month(self, date: Optional[datetime] = None) -> str:
        """Get previous month's string."""
        if date is None:
            date = datetime.now()
        first_of_month = date.replace(day=1)
        prev = first_of_month - timedelta(days=1)
        return self.get_current_month(prev)

    def get_previous_year(self, date: Optional[datetime] = None) -> str:
        """Get previous year's string."""
        if date is None:
            date = datetime.now()
        return str(date.year - 1)

    # ==================== Boundary Detection ====================

    def is_week_boundary(self, date: Optional[datetime] = None) -> bool:
        """Check if date is start of a new week (Monday)."""
        if date is None:
            date = datetime.now()
        return date.weekday() == 0  # Monday

    def is_month_boundary(self, date: Optional[datetime] = None) -> bool:
        """Check if date is start of a new month (1st)."""
        if date is None:
            date = datetime.now()
        return date.day == 1

    def is_year_boundary(self, date: Optional[datetime] = None) -> bool:
        """Check if date is start of a new year (Jan 1st)."""
        if date is None:
            date = datetime.now()
        return date.month == 1 and date.day == 1

    # ==================== State Management ====================

    def _load_state(self) -> dict:
        """Load summary state from file."""
        if self._state is not None:
            return self._state

        state_path = self.project_storage.get_summary_state_path()
        if state_path.exists():
            try:
                self._state = json.loads(state_path.read_text())
            except json.JSONDecodeError:
                self._state = {}
        else:
            self._state = {}
        return self._state

    def _save_state(self) -> None:
        """Save summary state to file."""
        if self._state is not None:
            state_path = self.project_storage.get_summary_state_path()
            state_path.write_text(json.dumps(self._state, indent=2))

    def summary_exists(self, period_type: str, period: str) -> bool:
        """Check if a summary already exists."""
        summary_path = self.project_storage.get_summary_file(period_type, period)
        return summary_path.exists()

    def mark_summary_generated(self, period_type: str, period: str) -> None:
        """Mark a summary as generated in state."""
        state = self._load_state()
        state[f"last_{period_type}"] = period
        state.setdefault("generation_history", []).append({
            "type": period_type,
            "period": period,
            "generated_at": datetime.now().isoformat(),
        })
        # Keep only last 100 history entries
        if len(state["generation_history"]) > 100:
            state["generation_history"] = state["generation_history"][-100:]
        self._save_state()

    # ==================== Date Range Helpers ====================

    def get_week_date_range(self, week_str: str) -> tuple[datetime, datetime]:
        """
        Get start and end dates for a week string.

        Args:
            week_str: ISO week string (e.g., '2026-W07').

        Returns:
            Tuple of (start_date, end_date) for the week.
        """
        year, week = week_str.split("-W")
        year = int(year)
        week = int(week)

        # ISO week 1 is the week containing the first Thursday
        jan4 = datetime(year, 1, 4)
        start_of_week1 = jan4 - timedelta(days=jan4.weekday())
        start = start_of_week1 + timedelta(weeks=week - 1)
        end = start + timedelta(days=6)

        return start, end

    def get_month_date_range(self, month_str: str) -> tuple[datetime, datetime]:
        """
        Get start and end dates for a month string.

        Args:
            month_str: Month string (e.g., '2026-02').

        Returns:
            Tuple of (start_date, end_date) for the month.
        """
        year, month = month_str.split("-")
        year = int(year)
        month = int(month)

        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end = datetime(year, month + 1, 1) - timedelta(days=1)

        return start, end

    def get_weeks_in_month(self, month_str: str) -> list[str]:
        """Get all week strings that overlap with a month."""
        start, end = self.get_month_date_range(month_str)
        weeks = set()

        current = start
        while current <= end:
            weeks.add(self.get_current_week(current))
            current += timedelta(days=1)

        return sorted(weeks)

    def get_months_in_year(self, year_str: str) -> list[str]:
        """Get all month strings in a year."""
        year = int(year_str)
        return [f"{year}-{m:02d}" for m in range(1, 13)]

    # ==================== Data Collection ====================

    def collect_week_data(self, week_str: str) -> dict:
        """
        Collect data for a weekly summary from raw sources.

        Args:
            week_str: ISO week string (e.g., '2026-W07').

        Returns:
            Dictionary with prompts, decisions, requirements, learnings, etc.
        """
        start, end = self.get_week_date_range(week_str)

        data = {
            "period": week_str,
            "start_date": start.strftime("%Y-%m-%d"),
            "end_date": end.strftime("%Y-%m-%d"),
            "prompts": [],
            "decisions": [],
            "requirements_completed": [],
            "requirements_open": [],
            "learnings": [],
            "questions": [],
            "prd_updates": {},
        }

        # Collect prompts from daily files
        current = start
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            prompt_file = self.project_storage.prompts_path / f"{date_str}.md"

            if prompt_file.exists():
                content = prompt_file.read_text()
                prompts = self._parse_prompts_file(content, date_str)
                data["prompts"].extend(prompts)

            current += timedelta(days=1)

        # Collect from PRDs (filter by date)
        for prd_name in self.project_storage.list_prds():
            prd_path = self.project_storage.get_prd_file(prd_name)
            if prd_path.exists():
                content = prd_path.read_text()
                prd_data = self._parse_prd_for_period(content, prd_name, start, end)
                if prd_data["decisions"]:
                    data["decisions"].extend(prd_data["decisions"])
                if prd_data["requirements_completed"]:
                    data["requirements_completed"].extend(prd_data["requirements_completed"])
                if prd_data["questions"]:
                    data["questions"].extend(prd_data["questions"])
                if prd_data["has_updates"]:
                    data["prd_updates"][prd_name] = prd_data

        # Collect learnings
        current = start
        while current <= end:
            daily_file = self.global_storage.get_daily_file(current)
            if daily_file.exists():
                content = daily_file.read_text()
                learnings = self._parse_learnings_file(content, current.strftime("%Y-%m-%d"))
                data["learnings"].extend(learnings)
            current += timedelta(days=1)

        return data

    def collect_month_data(self, month_str: str) -> dict:
        """
        Collect data for a monthly summary from weekly summaries.

        Args:
            month_str: Month string (e.g., '2026-02').

        Returns:
            Dictionary with aggregated weekly data.
        """
        weeks = self.get_weeks_in_month(month_str)
        start, end = self.get_month_date_range(month_str)

        data = {
            "period": month_str,
            "start_date": start.strftime("%Y-%m-%d"),
            "end_date": end.strftime("%Y-%m-%d"),
            "weeks_included": [],
            "weeks_missing": [],
            "total_prompts": 0,
            "total_decisions": 0,
            "total_requirements_completed": 0,
            "total_learnings": 0,
            "weekly_summaries": [],
        }

        for week in weeks:
            summary_path = self.project_storage.get_summary_file(self.WEEKLY, week)
            if summary_path.exists():
                data["weeks_included"].append(week)
                weekly_data = self._parse_weekly_summary(summary_path.read_text())
                data["weekly_summaries"].append({"week": week, **weekly_data})
                data["total_prompts"] += weekly_data.get("prompt_count", 0)
                data["total_decisions"] += weekly_data.get("decision_count", 0)
                data["total_requirements_completed"] += weekly_data.get("requirements_completed", 0)
                data["total_learnings"] += weekly_data.get("learning_count", 0)
            else:
                data["weeks_missing"].append(week)

        return data

    def collect_year_data(self, year_str: str) -> dict:
        """
        Collect data for a yearly summary from monthly summaries.

        Args:
            year_str: Year string (e.g., '2026').

        Returns:
            Dictionary with aggregated monthly data.
        """
        months = self.get_months_in_year(year_str)

        data = {
            "period": year_str,
            "months_included": [],
            "months_missing": [],
            "total_prompts": 0,
            "total_decisions": 0,
            "total_requirements_completed": 0,
            "total_learnings": 0,
            "monthly_summaries": [],
        }

        for month in months:
            summary_path = self.project_storage.get_summary_file(self.MONTHLY, month)
            if summary_path.exists():
                data["months_included"].append(month)
                monthly_data = self._parse_monthly_summary(summary_path.read_text())
                data["monthly_summaries"].append({"month": month, **monthly_data})
                data["total_prompts"] += monthly_data.get("total_prompts", 0)
                data["total_decisions"] += monthly_data.get("total_decisions", 0)
                data["total_requirements_completed"] += monthly_data.get("total_requirements_completed", 0)
                data["total_learnings"] += monthly_data.get("total_learnings", 0)
            else:
                data["months_missing"].append(month)

        return data

    # ==================== Parsing Helpers ====================

    def _parse_prompts_file(self, content: str, date_str: str) -> list[dict]:
        """Parse prompts from a daily prompts file."""
        prompts = []
        # Pattern: ## [feature] HH:MM:SS\n\n> prompt text
        pattern = r"## \[([^\]]+)\] (\d{2}:\d{2}:\d{2})\n\n> (.+?)(?=\n\n---|\Z)"
        matches = re.findall(pattern, content, re.DOTALL)

        line_num = 1
        for feature, time, text in matches:
            # Find line number for this prompt
            idx = content.find(f"## [{feature}] {time}")
            if idx >= 0:
                line_num = content[:idx].count("\n") + 1

            prompts.append({
                "feature": feature,
                "time": time,
                "date": date_str,
                "text": text.strip(),
                "line": line_num,
                "ref": f"prompts/{date_str}.md#L{line_num}",
            })

        return prompts

    def _parse_prd_for_period(
        self, content: str, prd_name: str, start: datetime, end: datetime
    ) -> dict:
        """Parse PRD content for items within a date range."""
        data = {
            "prd_name": prd_name,
            "decisions": [],
            "requirements_completed": [],
            "questions": [],
            "has_updates": False,
        }

        # Parse decisions table: | YYYY-MM-DD | Decision | Rationale |
        decision_pattern = r"\| (\d{4}-\d{2}-\d{2}) \| ([^|]+) \| ([^|]+) \|"
        for match in re.finditer(decision_pattern, content):
            date_str = match.group(1)
            decision_date = datetime.strptime(date_str, "%Y-%m-%d")
            if start <= decision_date <= end:
                data["decisions"].append({
                    "prd": prd_name,
                    "date": date_str,
                    "decision": match.group(2).strip(),
                    "rationale": match.group(3).strip(),
                })
                data["has_updates"] = True

        # Parse session log for completed requirements
        # Pattern: ### YYYY-MM-DD\n- Completed: ... ([prompt](ref))
        session_pattern = r"### (\d{4}-\d{2}-\d{2})\n(.*?)(?=\n### |\n## |\Z)"
        for match in re.finditer(session_pattern, content, re.DOTALL):
            date_str = match.group(1)
            session_date = datetime.strptime(date_str, "%Y-%m-%d")
            if start <= session_date <= end:
                entries = match.group(2)
                # Look for completed items
                for line in entries.split("\n"):
                    if "completed" in line.lower() or "[x]" in line.lower():
                        # Extract prompt reference if present
                        ref_match = re.search(r"\[prompt\]\(([^)]+)\)", line)
                        ref = ref_match.group(1) if ref_match else None
                        data["requirements_completed"].append({
                            "prd": prd_name,
                            "date": date_str,
                            "text": line.strip("- ").strip(),
                            "ref": ref,
                        })
                        data["has_updates"] = True

        # Parse open questions
        questions_match = re.search(r"## Open Questions\n(.*?)(?=\n## |\Z)", content, re.DOTALL)
        if questions_match:
            questions_text = questions_match.group(1)
            question_pattern = r"- (.+?) \*\(asked (\d{4}-\d{2}-\d{2})\)\*"
            for match in re.finditer(question_pattern, questions_text):
                date_str = match.group(2)
                question_date = datetime.strptime(date_str, "%Y-%m-%d")
                if start <= question_date <= end:
                    data["questions"].append({
                        "prd": prd_name,
                        "date": date_str,
                        "text": match.group(1).strip(),
                    })

        return data

    def _parse_learnings_file(self, content: str, date_str: str) -> list[dict]:
        """Parse learnings from a daily learnings file."""
        learnings = []
        # Pattern: ## [Type] HH:MM:SS\n\n> text
        pattern = r"## \[(\w+)\] (\d{2}:\d{2}:\d{2})\n\n> (.+?)(?=\n\n\*\*Signal|\n\n## |\Z)"

        line_num = 1
        for match in re.finditer(pattern, content, re.DOTALL):
            learning_type = match.group(1)
            time = match.group(2)
            text = match.group(3).strip()

            # Find line number
            idx = content.find(f"## [{learning_type}] {time}")
            if idx >= 0:
                line_num = content[:idx].count("\n") + 1

            learnings.append({
                "type": learning_type,
                "time": time,
                "date": date_str,
                "text": text,
                "line": line_num,
                "ref": f"daily/{date_str}.md#L{line_num}",
            })

        return learnings

    def _parse_weekly_summary(self, content: str) -> dict:
        """Parse statistics from a weekly summary file."""
        data = {
            "prompt_count": 0,
            "decision_count": 0,
            "requirements_completed": 0,
            "learning_count": 0,
        }

        # Extract from Overview section
        overview_match = re.search(r"## Overview\n(.*?)(?=\n## |\Z)", content, re.DOTALL)
        if overview_match:
            overview = overview_match.group(1)
            for line in overview.split("\n"):
                if "Prompts analyzed" in line:
                    match = re.search(r"(\d+)", line)
                    if match:
                        data["prompt_count"] = int(match.group(1))
                elif "Decisions made" in line:
                    match = re.search(r"(\d+)", line)
                    if match:
                        data["decision_count"] = int(match.group(1))
                elif "Requirements completed" in line:
                    match = re.search(r"(\d+)", line)
                    if match:
                        data["requirements_completed"] = int(match.group(1))

        # Count learnings
        data["learning_count"] = content.count("## Learnings") and len(
            re.findall(r"^- ", content, re.MULTILINE)
        )

        return data

    def _parse_monthly_summary(self, content: str) -> dict:
        """Parse statistics from a monthly summary file."""
        data = {
            "total_prompts": 0,
            "total_decisions": 0,
            "total_requirements_completed": 0,
            "total_learnings": 0,
            "weeks_included": [],
        }

        # Extract from Overview section
        overview_match = re.search(r"## Overview\n(.*?)(?=\n## |\Z)", content, re.DOTALL)
        if overview_match:
            overview = overview_match.group(1)
            for line in overview.split("\n"):
                if "Total prompts" in line or "prompts" in line.lower():
                    match = re.search(r"(\d+)", line)
                    if match:
                        data["total_prompts"] = int(match.group(1))
                elif "Decisions" in line:
                    match = re.search(r"(\d+)", line)
                    if match:
                        data["total_decisions"] = int(match.group(1))
                elif "Requirements" in line:
                    match = re.search(r"(\d+)", line)
                    if match:
                        data["total_requirements_completed"] = int(match.group(1))
                elif "Weeks included" in line:
                    weeks_match = re.search(r"W\d+", line)
                    if weeks_match:
                        data["weeks_included"] = re.findall(r"W\d+", line)

        return data

    # ==================== Summary Generation ====================

    def generate_weekly_summary(self, week_str: str) -> str:
        """
        Generate a weekly summary.

        Args:
            week_str: ISO week string (e.g., '2026-W07').

        Returns:
            Markdown summary content.
        """
        data = self.collect_week_data(week_str)
        start, end = self.get_week_date_range(week_str)

        # Calculate statistics
        prompt_count = len(data["prompts"])
        decision_count = len(data["decisions"])
        req_completed = len(data["requirements_completed"])
        learning_count = len(data["learnings"])
        question_count = len(data["questions"])

        # Build summary
        lines = [
            f"# Week {week_str.split('-W')[1]} Summary ({start.strftime('%b %d')}-{end.strftime('%d, %Y')})",
            "",
            "## Overview",
            f"- **Prompts analyzed**: {prompt_count}",
            f"- **Requirements completed**: {req_completed}",
            f"- **Decisions made**: {decision_count}",
            f"- **Learnings captured**: {learning_count}",
            f"- **Questions raised**: {question_count}",
            "",
        ]

        # Decisions section
        if data["decisions"]:
            lines.append("## Decisions Made")
            lines.append("")
            current_prd = None
            for dec in sorted(data["decisions"], key=lambda x: (x["prd"], x["date"])):
                if dec["prd"] != current_prd:
                    current_prd = dec["prd"]
                    lines.append(f"### {current_prd.replace('-', ' ').title()}")
                lines.append(f"- **{dec['decision']}** - {dec['rationale']}")
                lines.append(f"  - Date: {dec['date']}")
            lines.append("")

        # Requirements completed section
        if data["requirements_completed"]:
            lines.append("## Requirements Completed")
            lines.append("")
            current_prd = None
            for req in sorted(data["requirements_completed"], key=lambda x: (x["prd"], x["date"])):
                if req["prd"] != current_prd:
                    current_prd = req["prd"]
                    lines.append(f"### {current_prd.replace('-', ' ').title()}")
                ref_link = f" ([prompt]({req['ref']}))" if req.get("ref") else ""
                lines.append(f"- [x] {req['text']}{ref_link}")
            lines.append("")

        # Learnings section
        if data["learnings"]:
            lines.append("## Learnings")
            lines.append("")
            by_type = {}
            for learning in data["learnings"]:
                lt = learning["type"]
                by_type.setdefault(lt, []).append(learning)

            for learning_type, items in sorted(by_type.items()):
                lines.append(f"### {learning_type.title()}s")
                for item in items[:5]:  # Limit to 5 per type
                    text = item["text"][:100] + "..." if len(item["text"]) > 100 else item["text"]
                    lines.append(f"- {text}")
                    lines.append(f"  - [Source](../{item['ref']})")
                lines.append("")

        # Questions section
        if data["questions"]:
            lines.append("## Open Questions")
            lines.append("")
            for q in data["questions"]:
                lines.append(f"- {q['text']} ({q['prd']}, asked {q['date']})")
            lines.append("")

        # Prompts reference section
        if data["prompts"]:
            lines.append("## Prompt References")
            lines.append("")
            # Group by date
            by_date = {}
            for p in data["prompts"]:
                by_date.setdefault(p["date"], []).append(p)

            for date in sorted(by_date.keys()):
                prompts = by_date[date]
                lines.append(f"- **{date}**: {len(prompts)} prompts ([view](../prompts/{date}.md))")
            lines.append("")

        # Footer
        lines.extend([
            "---",
            f"_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_",
            f"_Period: {data['start_date']} to {data['end_date']}_",
            f"_Days covered: {(end - start).days + 1}/7_",
        ])

        content = "\n".join(lines)

        # Save summary
        summary_path = self.project_storage.get_summary_file(self.WEEKLY, week_str)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(content)

        self.mark_summary_generated(self.WEEKLY, week_str)

        return content

    def generate_monthly_summary(self, month_str: str) -> str:
        """
        Generate a monthly summary from weekly summaries.

        Args:
            month_str: Month string (e.g., '2026-02').

        Returns:
            Markdown summary content.
        """
        data = self.collect_month_data(month_str)
        start, end = self.get_month_date_range(month_str)

        # Build summary
        month_name = start.strftime("%B %Y")
        lines = [
            f"# {month_name} Summary",
            "",
            "## Overview",
            f"- **Weeks included**: {', '.join(data['weeks_included']) or 'None'}",
            f"- **Weeks missing**: {', '.join(data['weeks_missing']) or 'None'}",
            f"- **Total prompts**: {data['total_prompts']}",
            f"- **Total decisions**: {data['total_decisions']}",
            f"- **Total requirements completed**: {data['total_requirements_completed']}",
            f"- **Total learnings**: {data['total_learnings']}",
            "",
        ]

        # Weekly breakdown
        if data["weekly_summaries"]:
            lines.append("## Weekly Breakdown")
            lines.append("")
            lines.append("| Week | Prompts | Decisions | Requirements | Learnings |")
            lines.append("|------|---------|-----------|--------------|-----------|")
            for ws in data["weekly_summaries"]:
                week = ws["week"]
                lines.append(
                    f"| [{week}](weekly/{week}.md) | "
                    f"{ws.get('prompt_count', 0)} | "
                    f"{ws.get('decision_count', 0)} | "
                    f"{ws.get('requirements_completed', 0)} | "
                    f"{ws.get('learning_count', 0)} |"
                )
            lines.append("")

        # Footer
        lines.extend([
            "---",
            f"_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_",
            f"_Period: {data['start_date']} to {data['end_date']}_",
            f"_Weeks covered: {len(data['weeks_included'])}/{len(data['weeks_included']) + len(data['weeks_missing'])}_",
        ])

        content = "\n".join(lines)

        # Save summary
        summary_path = self.project_storage.get_summary_file(self.MONTHLY, month_str)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(content)

        self.mark_summary_generated(self.MONTHLY, month_str)

        return content

    def generate_yearly_summary(self, year_str: str) -> str:
        """
        Generate a yearly summary from monthly summaries.

        Args:
            year_str: Year string (e.g., '2026').

        Returns:
            Markdown summary content.
        """
        data = self.collect_year_data(year_str)

        # Build summary
        lines = [
            f"# {year_str} Annual Summary",
            "",
            "## Overview",
            f"- **Months included**: {len(data['months_included'])}",
            f"- **Months missing**: {len(data['months_missing'])}",
            f"- **Total prompts**: {data['total_prompts']}",
            f"- **Total decisions**: {data['total_decisions']}",
            f"- **Total requirements completed**: {data['total_requirements_completed']}",
            f"- **Total learnings**: {data['total_learnings']}",
            "",
        ]

        # Monthly breakdown
        if data["monthly_summaries"]:
            lines.append("## Monthly Breakdown")
            lines.append("")
            lines.append("| Month | Prompts | Decisions | Requirements | Learnings |")
            lines.append("|-------|---------|-----------|--------------|-----------|")
            for ms in data["monthly_summaries"]:
                month = ms["month"]
                lines.append(
                    f"| [{month}](monthly/{month}.md) | "
                    f"{ms.get('total_prompts', 0)} | "
                    f"{ms.get('total_decisions', 0)} | "
                    f"{ms.get('total_requirements_completed', 0)} | "
                    f"{ms.get('total_learnings', 0)} |"
                )
            lines.append("")

        # Footer
        lines.extend([
            "---",
            f"_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_",
            f"_Months covered: {len(data['months_included'])}/12_",
        ])

        content = "\n".join(lines)

        # Save summary
        summary_path = self.project_storage.get_summary_file(self.YEARLY, year_str)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(content)

        self.mark_summary_generated(self.YEARLY, year_str)

        return content

    # ==================== Breadcrumb Helpers ====================

    def create_breadcrumb(self, source_path: str, line_number: int) -> str:
        """
        Create a markdown breadcrumb link.

        Args:
            source_path: Relative path to source file.
            line_number: Line number in the file.

        Returns:
            Markdown link string.
        """
        return f"[Source]({source_path}#L{line_number})"

    # ==================== Pending Summary Detection ====================

    def check_pending_summaries(self, date: Optional[datetime] = None) -> list[tuple[str, str]]:
        """
        Check for summaries that need to be generated.

        Args:
            date: Current date. Defaults to now.

        Returns:
            List of (period_type, period) tuples that need generation.
        """
        if date is None:
            date = datetime.now()

        pending = []

        # Check weekly
        if self.is_week_boundary(date):
            prev_week = self.get_previous_week(date)
            if not self.summary_exists(self.WEEKLY, prev_week):
                pending.append((self.WEEKLY, prev_week))

        # Check monthly
        if self.is_month_boundary(date):
            prev_month = self.get_previous_month(date)
            if not self.summary_exists(self.MONTHLY, prev_month):
                pending.append((self.MONTHLY, prev_month))

        # Check yearly
        if self.is_year_boundary(date):
            prev_year = self.get_previous_year(date)
            if not self.summary_exists(self.YEARLY, prev_year):
                pending.append((self.YEARLY, prev_year))

        return pending
