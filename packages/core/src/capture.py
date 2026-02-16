"""
Capture module for Ninho.

Handles extraction of prompts from Claude Code transcripts.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional


class Capture:
    """Extract and process prompts from transcripts."""

    def __init__(self, transcript_path: str):
        """
        Initialize capture with a transcript file.

        Args:
            transcript_path: Path to the transcript JSONL file.
        """
        self.transcript_path = Path(transcript_path)
        self._entries: Optional[list[dict]] = None

    def _load_transcript(self) -> list[dict]:
        """Load and parse transcript JSONL file."""
        if self._entries is not None:
            return self._entries

        entries = []
        if self.transcript_path.exists():
            with open(self.transcript_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        self._entries = entries
        return entries

    def get_user_prompts(self) -> list[dict]:
        """
        Extract all user prompts from transcript.

        Returns:
            List of prompt dictionaries with 'text' and 'timestamp' keys.
        """
        entries = self._load_transcript()
        prompts = []

        for entry in entries:
            if entry.get("type") == "user":
                message = entry.get("message", {})
                content = message.get("content", [])

                # Extract text from content blocks
                text_parts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                    elif isinstance(block, str):
                        text_parts.append(block)

                if text_parts:
                    prompts.append({
                        "text": "\n".join(text_parts),
                        "timestamp": entry.get("timestamp", datetime.now().isoformat()),
                    })

        return prompts

    def get_recent_prompts(self, count: int = 5) -> list[dict]:
        """
        Get the most recent user prompts.

        Args:
            count: Number of prompts to return.

        Returns:
            List of recent prompt dictionaries.
        """
        prompts = self.get_user_prompts()
        return prompts[-count:] if len(prompts) > count else prompts

    def get_tool_uses(self) -> list[dict]:
        """
        Extract all tool uses from transcript.

        Returns:
            List of tool use dictionaries.
        """
        entries = self._load_transcript()
        tool_uses = []

        for entry in entries:
            if entry.get("type") == "assistant":
                message = entry.get("message", {})
                content = message.get("content", [])

                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        tool_uses.append({
                            "name": block.get("name"),
                            "input": block.get("input", {}),
                            "timestamp": entry.get("timestamp"),
                        })

        return tool_uses

    def get_modified_files(self) -> list[str]:
        """
        Extract list of files modified during the session.

        Returns:
            List of file paths that were edited or written.
        """
        tool_uses = self.get_tool_uses()
        modified_files = set()

        for tool in tool_uses:
            name = tool.get("name", "")
            inputs = tool.get("input", {})

            if name in ("Edit", "Write", "NotebookEdit"):
                file_path = inputs.get("file_path") or inputs.get("notebook_path")
                if file_path:
                    modified_files.add(file_path)

        return sorted(modified_files)

    def detect_feature_context(self) -> Optional[str]:
        """
        Detect the feature context based on modified files.

        Returns:
            Feature name or None if not detected.
        """
        modified_files = self.get_modified_files()

        # Common folder-to-feature mappings
        feature_patterns = [
            (r"src/auth/", "auth-system"),
            (r"src/api/", "api-integration"),
            (r"src/components/dashboard/", "user-dashboard"),
            (r"src/components/", "frontend"),
            (r"src/utils/", "utilities"),
            (r"tests/", "testing"),
            (r"docs/", "documentation"),
        ]

        for file_path in modified_files:
            for pattern, feature in feature_patterns:
                if re.search(pattern, file_path):
                    return feature

        # Try to infer from first significant directory
        for file_path in modified_files:
            parts = Path(file_path).parts
            if len(parts) > 1 and parts[0] == "src":
                return parts[1].replace("_", "-")

        return None

    def get_last_assistant_summary(self, max_length: int = 150) -> Optional[str]:
        """
        Get a brief summary of the last assistant response.

        Extracts the first sentence of text and lists tools used.

        Args:
            max_length: Maximum length for the text portion.

        Returns:
            Summary string or None if no assistant response found.
        """
        entries = self._load_transcript()

        for entry in reversed(entries):
            if entry.get("type") == "assistant":
                message = entry.get("message", {})
                content = message.get("content", [])

                text_parts = []
                tools_used = []

                for block in content:
                    if isinstance(block, dict):
                        if block.get("type") == "text":
                            text_parts.append(block.get("text", ""))
                        elif block.get("type") == "tool_use":
                            tools_used.append(block.get("name", ""))

                summary_parts = []

                if text_parts:
                    full_text = " ".join(text_parts).strip()
                    # Get first sentence
                    first_sentence = re.split(r'(?<=[.!?])\s', full_text, maxsplit=1)[0]
                    if len(first_sentence) > max_length:
                        first_sentence = first_sentence[:max_length] + "..."
                    summary_parts.append(first_sentence)

                if tools_used:
                    unique_tools = list(dict.fromkeys(tools_used))
                    summary_parts.append(f"[{', '.join(unique_tools)}]")

                if summary_parts:
                    return " ".join(summary_parts)

        return None
