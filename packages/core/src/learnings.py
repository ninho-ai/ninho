"""
Learnings module for Ninho.

Extracts and stores daily learnings from conversations.
"""

import hashlib
import re
from datetime import datetime
from typing import Optional

try:
    from .storage import Storage
except ImportError:
    from storage import Storage


class Learnings:
    """Extract and manage daily learnings."""

    # Patterns for detecting learning signals
    CORRECTION_PATTERNS = [
        r"\bno,\s",
        r"\bactually,\s",
        r"\bdon't\s+do\b",
        r"\bnever\s",
        r"\bwrong\b",
        r"\bincorrect\b",
        r"\binstead\s+of\b",
        r"\bshould\s+not\b",
        r"\bshouldn't\b",
    ]

    LEARNING_PATTERNS = [
        r"\bi\s+learned\b",
        r"\btil:\s",
        r"\bnote:\s",
        r"\bremember:\s",
        r"\bimportant:\s",
        r"\bkeep\s+in\s+mind\b",
        r"\bgood\s+to\s+know\b",
    ]

    DECISION_PATTERNS = [
        r"\bwe\s+decided\b",
        r"\blet's\s+go\s+with\b",
        r"\bconvention\s+is\b",
        r"\bstandard\s+is\b",
        r"\bprefer\s+to\b",
        r"\balways\s+use\b",
        r"\bchose\s+to\b",
        r"\bagreed\s+on\b",
    ]

    def __init__(self, storage: Optional[Storage] = None):
        """
        Initialize learnings manager.

        Args:
            storage: Storage instance. Creates new one if not provided.
        """
        self.storage = storage or Storage()
        self._index: Optional[dict] = None

    def _load_index(self) -> dict:
        """Load deduplication index."""
        if self._index is not None:
            return self._index

        index_path = self.storage.get_index_path()
        self._index = self.storage.read_json(index_path) or {"hashes": []}
        return self._index

    def _save_index(self) -> None:
        """Save deduplication index."""
        if self._index is not None:
            self.storage.write_json(self.storage.get_index_path(), self._index)

    def _hash_content(self, content: str) -> str:
        """Generate hash for content deduplication."""
        # Normalize content before hashing
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

    def detect_learning_type(self, text: str) -> Optional[str]:
        """
        Detect the type of learning signal in text.

        Args:
            text: Text to analyze.

        Returns:
            Learning type: 'correction', 'learning', 'decision', or None.
        """
        text_lower = text.lower()

        for pattern in self.CORRECTION_PATTERNS:
            if re.search(pattern, text_lower):
                return "correction"

        for pattern in self.LEARNING_PATTERNS:
            if re.search(pattern, text_lower):
                return "learning"

        for pattern in self.DECISION_PATTERNS:
            if re.search(pattern, text_lower):
                return "decision"

        return None

    def extract_learnings(self, prompts: list[dict]) -> list[dict]:
        """
        Extract learnings from a list of prompts.

        Args:
            prompts: List of prompt dictionaries with 'text' and 'timestamp'.

        Returns:
            List of learning dictionaries.
        """
        learnings = []

        for prompt in prompts:
            text = prompt.get("text", "")
            timestamp = prompt.get("timestamp", datetime.now().isoformat())

            learning_type = self.detect_learning_type(text)
            if learning_type:
                learnings.append({
                    "type": learning_type,
                    "text": text,
                    "timestamp": timestamp,
                    "signal": self._get_signal(text, learning_type),
                })

        return learnings

    def _get_signal(self, text: str, learning_type: str) -> str:
        """Get the specific signal that triggered the learning detection."""
        text_lower = text.lower()

        patterns = {
            "correction": self.CORRECTION_PATTERNS,
            "learning": self.LEARNING_PATTERNS,
            "decision": self.DECISION_PATTERNS,
        }

        for pattern in patterns.get(learning_type, []):
            match = re.search(pattern, text_lower)
            if match:
                return match.group(0).strip()

        return learning_type

    def format_learning(self, learning: dict) -> str:
        """
        Format a learning for markdown output.

        Args:
            learning: Learning dictionary.

        Returns:
            Formatted markdown string.
        """
        timestamp = learning.get("timestamp", "")
        if isinstance(timestamp, str) and "T" in timestamp:
            # Parse ISO format and extract time
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                time_str = dt.strftime("%H:%M:%S")
            except ValueError:
                time_str = timestamp
        else:
            time_str = timestamp

        learning_type = learning.get("type", "learning").title()
        text = learning.get("text", "")
        signal = learning.get("signal", "")

        return f"""## [{learning_type}] {time_str}

> {text}

**Signal:** `{signal}`

---

"""

    def save_learnings(
        self,
        learnings: list[dict],
        date: Optional[datetime] = None
    ) -> int:
        """
        Save learnings to daily file, deduplicating.

        Args:
            learnings: List of learning dictionaries.
            date: Date for the file. Defaults to today.

        Returns:
            Number of new learnings saved.
        """
        if not learnings:
            return 0

        file_path = self.storage.get_daily_file(date)
        saved_count = 0

        # Create file with header if it doesn't exist
        if not file_path.exists():
            date_str = (date or datetime.now()).strftime("%Y-%m-%d")
            header = f"# Daily Learnings - {date_str}\n\n"
            self.storage.write_file(file_path, header)

        # Append non-duplicate learnings
        for learning in learnings:
            text = learning.get("text", "")
            if text and not self._is_duplicate(text):
                formatted = self.format_learning(learning)
                self.storage.append_file(file_path, formatted)
                self._mark_as_seen(text)
                saved_count += 1

        return saved_count
