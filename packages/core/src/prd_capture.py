"""
PRD Capture module for Ninho.

Extracts requirements, decisions, constraints, and questions from transcripts
to automatically populate PRDs.
"""

import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from .storage import ProjectStorage
except ImportError:
    from storage import ProjectStorage


class PRDCapture:
    """Extract PRD-worthy content from transcripts."""

    # Patterns for detecting requirements and tasks
    REQUIREMENT_PATTERNS = [
        r"\b(i\s+)?need\s+to\s+(build|create|add|fix|implement|make|write|update)\b",
        r"\bfix\s+(this|the|a)\b",
        r"\bshould\s+have\b",
        r"\bmust\s+support\b",
        r"\brequire[sd]?\b",
        r"\bwe\s+(need|should|must)\b",
        r"\b(add|create|build|implement|write)\s+a\b",
        r"\bmake\s+(it|this|the)\b",
        r"\b(can|could)\s+you\b",
        r"\bplease\s+(add|create|fix|implement|update)\b",
        r"\b(i|we)\s+(want|'d like)\s+to\b",
        r"\blet's\s+(add|create|build|implement)\b",
        r"\bi('d| would)\s+like\s+to\b",
    ]

    # Patterns for detecting bugs and issues
    BUG_PATTERNS = [
        r"\bfix\s+(this|the|a)\b",
        r"\bthere's\s+a\s+bug\b",
        r"\bbug\s+in\b",
        r"\bdoesn't\s+work\b",
        r"\bnot\s+working\b",
        r"\bbroken\b",
        r"\berror\s+when\b",
        r"\bfailing\b",
        r"\bcrashes\b",
        r"\bissue\s+with\b",
    ]

    # Patterns for detecting decisions
    DECISION_PATTERNS = [
        r"\blet's\s+use\b",
        r"\bwe'll\s+(go\s+with|use)\b",
        r"\bdecided\s+(to|on)\b",
        r"\bchose\b",
        r"\bi'll\s+use\b",
        r"\bwe\s+should\s+use\b",
        r"\bgoing\s+with\b",
        r"\bprefer\s+to\b",
        r"\bbetter\s+to\b",
        r"\bmakes\s+sense\s+to\b",
        r"\bagreed\s+(to|on)\b",
    ]

    # Patterns for detecting constraints
    CONSTRAINT_PATTERNS = [
        r"\bmust\s+be\b",
        r"\bcannot\b",
        r"\bcan't\b",
        r"\bshouldn't\b",
        r"\blimited\s+to\b",
        r"\bmaximum\b",
        r"\bminimum\b",
        r"\bat\s+(most|least)\b",
        r"\bonly\s+if\b",
        r"\bunless\b",
        r"\bno\s+more\s+than\b",
    ]

    # Patterns for detecting questions
    QUESTION_PATTERNS = [
        r"\?$",
        r"\bhow\s+(do|can|should)\b",
        r"\bwhat\s+if\b",
        r"\bshould\s+we\b",
        r"\bcan\s+we\b",
        r"\bwhy\s+(do|does|is|are)\b",
        r"\bwhat\s+(is|are|does)\b",
    ]

    def __init__(self, project_storage: Optional[ProjectStorage] = None):
        """
        Initialize PRD capture.

        Args:
            project_storage: ProjectStorage instance for saving prompts.
        """
        self.storage = project_storage
        self._index: Optional[dict] = None

    def _load_index(self) -> dict:
        """Load deduplication index."""
        if self._index is not None:
            return self._index

        if self.storage is None:
            self._index = {"hashes": []}
            return self._index

        index_path = self.storage.ninho_path / "prompt-index.json"
        if index_path.exists():
            import json
            try:
                self._index = json.loads(index_path.read_text())
            except json.JSONDecodeError:
                self._index = {"hashes": []}
        else:
            self._index = {"hashes": []}
        return self._index

    def _save_index(self) -> None:
        """Save deduplication index."""
        if self._index is not None and self.storage is not None:
            import json
            index_path = self.storage.ninho_path / "prompt-index.json"
            index_path.write_text(json.dumps(self._index, indent=2))

    def _hash_content(self, content: str) -> str:
        """Generate hash for content deduplication."""
        normalized = re.sub(r"\s+", " ", content.strip().lower())
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    def _is_duplicate(self, content: str) -> bool:
        """Check if content is a duplicate."""
        index = self._load_index()
        content_hash = self._hash_content(content)
        return content_hash in index.get("hashes", [])

    def _mark_as_seen(self, content: str) -> None:
        """Mark content as seen for deduplication."""
        index = self._load_index()
        content_hash = self._hash_content(content)
        if content_hash not in index.get("hashes", []):
            index.setdefault("hashes", []).append(content_hash)
            # Keep only last 1000 hashes
            if len(index["hashes"]) > 1000:
                index["hashes"] = index["hashes"][-1000:]
            self._save_index()

    def detect_item_type(self, text: str) -> Optional[str]:
        """
        Detect the type of PRD item in text.

        Args:
            text: Text to analyze.

        Returns:
            Item type: 'requirement', 'bug', 'decision', 'constraint', 'question', or None.
        """
        text_lower = text.lower()

        # Check question first (most specific - ends with ?)
        for pattern in self.QUESTION_PATTERNS:
            if re.search(pattern, text_lower):
                return "question"

        # Check decisions
        for pattern in self.DECISION_PATTERNS:
            if re.search(pattern, text_lower):
                return "decision"

        # Check bugs
        for pattern in self.BUG_PATTERNS:
            if re.search(pattern, text_lower):
                return "bug"

        # Check constraints
        for pattern in self.CONSTRAINT_PATTERNS:
            if re.search(pattern, text_lower):
                return "constraint"

        # Check requirements (broadest category)
        for pattern in self.REQUIREMENT_PATTERNS:
            if re.search(pattern, text_lower):
                return "requirement"

        return None

    def extract_prd_items(self, prompts: list[dict]) -> list[dict]:
        """
        Extract PRD-worthy items from a list of prompts.

        Args:
            prompts: List of prompt dictionaries with 'text' and 'timestamp'.

        Returns:
            List of item dictionaries with type, text, and extracted content.
        """
        items = []

        for prompt in prompts:
            text = prompt.get("text", "")
            timestamp = prompt.get("timestamp", datetime.now().isoformat())

            # Skip duplicates
            if self._is_duplicate(text):
                continue

            item_type = self.detect_item_type(text)
            if item_type:
                item = {
                    "type": item_type,
                    "text": text,
                    "timestamp": timestamp,
                    "signal": self._get_signal(text, item_type),
                }

                # Extract additional data based on type
                if item_type == "decision":
                    item["rationale"] = self._extract_rationale(text)
                    item["summary"] = self._summarize_decision(text)
                elif item_type == "requirement" or item_type == "bug":
                    item["summary"] = self._summarize_requirement(text)
                elif item_type == "constraint":
                    item["summary"] = self._summarize_constraint(text)
                elif item_type == "question":
                    item["summary"] = self._extract_question(text)

                items.append(item)
                self._mark_as_seen(text)

        return items

    def _get_signal(self, text: str, item_type: str) -> str:
        """Get the specific signal that triggered the detection."""
        text_lower = text.lower()

        patterns = {
            "requirement": self.REQUIREMENT_PATTERNS,
            "bug": self.BUG_PATTERNS,
            "decision": self.DECISION_PATTERNS,
            "constraint": self.CONSTRAINT_PATTERNS,
            "question": self.QUESTION_PATTERNS,
        }

        for pattern in patterns.get(item_type, []):
            match = re.search(pattern, text_lower)
            if match:
                return match.group(0).strip()

        return item_type

    def _extract_rationale(self, text: str) -> str:
        """
        Extract rationale from a decision statement.

        Looks for patterns like "because", "since", "for", "to enable" etc.
        """
        rationale_patterns = [
            r"because\s+(.+?)(?:\.|$)",
            r"since\s+(.+?)(?:\.|$)",
            r"for\s+(.+?)(?:\.|$)",
            r"to\s+(enable|allow|support|ensure|make)\s+(.+?)(?:\.|$)",
            r"it's\s+(.+?)(?:\.|$)",
            r"this\s+(is|will|allows?|enables?)\s+(.+?)(?:\.|$)",
        ]

        text_lower = text.lower()
        for pattern in rationale_patterns:
            match = re.search(pattern, text_lower)
            if match:
                # Get the last group (the actual rationale)
                rationale = match.groups()[-1]
                # Capitalize first letter and clean up
                rationale = rationale.strip()
                if rationale:
                    return rationale[0].upper() + rationale[1:]

        return "See discussion"

    def _summarize_decision(self, text: str) -> str:
        """Extract a short summary of the decision."""
        # Remove the rationale part to get the core decision
        text_clean = re.sub(r"\s+(because|since|for|to enable|to allow).*$", "", text, flags=re.IGNORECASE)

        # Truncate if too long
        if len(text_clean) > 80:
            text_clean = text_clean[:77] + "..."

        return text_clean.strip()

    def _summarize_requirement(self, text: str) -> str:
        """Extract a short summary of the requirement."""
        # Truncate if too long
        if len(text) > 100:
            return text[:97] + "..."
        return text.strip()

    def _summarize_constraint(self, text: str) -> str:
        """Extract a short summary of the constraint."""
        if len(text) > 100:
            return text[:97] + "..."
        return text.strip()

    def _extract_question(self, text: str) -> str:
        """Extract the question text."""
        # If it ends with ?, it's likely the whole thing is a question
        if text.strip().endswith("?"):
            return text.strip()

        # Try to find a question within the text
        match = re.search(r"([^.!]+\?)", text)
        if match:
            return match.group(1).strip()

        return text.strip()

    def save_prompt(
        self,
        prompt: dict,
        feature: str,
        date: Optional[datetime] = None,
    ) -> str:
        """
        Save a prompt to the daily prompts file.

        Args:
            prompt: Prompt dictionary with 'text' and 'timestamp'.
            feature: Feature name for tagging.
            date: Date for the file. Defaults to today.

        Returns:
            Line reference string (e.g., "prompts/2026-02-16.md#L42").
        """
        if self.storage is None:
            return ""

        if date is None:
            date = datetime.now()

        file_path = self.storage.prompts_path / f"{date.strftime('%Y-%m-%d')}.md"

        # Create file with header if it doesn't exist
        if not file_path.exists():
            header = f"# Prompts - {date.strftime('%Y-%m-%d')}\n\n"
            self.storage.write_file(file_path, header)

        # Count current lines to get line number
        current_content = self.storage.read_file(file_path) or ""
        line_count = len(current_content.split("\n"))

        # Format prompt entry
        timestamp = prompt.get("timestamp", datetime.now().isoformat())
        if isinstance(timestamp, str) and "T" in timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                time_str = dt.strftime("%H:%M:%S")
            except ValueError:
                time_str = timestamp
        else:
            time_str = str(timestamp)

        text = prompt.get("text", "")
        entry = f"## [{feature}] {time_str}\n\n> {text}\n\n---\n\n"

        # Append to file
        self.storage.append_file(file_path, entry)

        # Return line reference
        return f"prompts/{date.strftime('%Y-%m-%d')}.md#L{line_count + 1}"
