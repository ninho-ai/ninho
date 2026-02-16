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

    def get_last_assistant_summary(self, max_length: int = 200) -> Optional[str]:
        """
        Get a summary of the full assistant response to the last user prompt.

        Collects all assistant entries after the last user message,
        extracts text, files edited, and tools used to build a
        comprehensive one-line summary.

        Args:
            max_length: Maximum length for the text portion.

        Returns:
            Summary string or None if no assistant response found.
        """
        entries = self._load_transcript()
        if not entries:
            return None

        # Find the last user entry index
        last_user_idx = -1
        for i in range(len(entries) - 1, -1, -1):
            if entries[i].get("type") == "user":
                last_user_idx = i
                break

        if last_user_idx == -1:
            return None

        # Collect all assistant content after the last user message
        all_text = []
        tools_used = []
        files_edited = []
        files_read = []

        for entry in entries[last_user_idx + 1:]:
            if entry.get("type") != "assistant":
                continue
            content = entry.get("message", {}).get("content", [])
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "text":
                    text = block.get("text", "").strip()
                    if text:
                        all_text.append(text)
                elif block.get("type") == "tool_use":
                    name = block.get("name", "")
                    inputs = block.get("input", {})
                    if name in ("Edit", "Write", "NotebookEdit"):
                        path = inputs.get("file_path") or inputs.get("notebook_path", "")
                        if path:
                            short = path.rsplit("/", 1)[-1]
                            if short not in files_edited:
                                files_edited.append(short)
                    elif name == "Read":
                        path = inputs.get("file_path", "")
                        if path:
                            short = path.rsplit("/", 1)[-1]
                            if short not in files_read:
                                files_read.append(short)
                    if name not in tools_used:
                        tools_used.append(name)

        if not all_text and not tools_used:
            return None

        # Build summary from combined text: first and last sentences
        parts = []
        if all_text:
            combined = " ".join(all_text)
            # Collapse newlines and clean markdown artifacts
            combined = re.sub(r'\s*\n\s*', ' ', combined)
            combined = re.sub(r'\*\*|##|`{1,3}|---|\|', '', combined)
            combined = re.sub(r'\s{2,}', ' ', combined).strip()
            sentences = re.split(r'(?<=[.!?])\s+', combined)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

            if sentences:
                summary_text = sentences[0]
                # Add last sentence if different and there are many
                if len(sentences) > 3:
                    last = sentences[-1]
                    if last != summary_text:
                        summary_text += " ... " + last
                if len(summary_text) > max_length:
                    summary_text = summary_text[:max_length] + "..."
                parts.append(summary_text)

        # Add files edited
        if files_edited:
            parts.append(f"edited: {', '.join(files_edited[:5])}")

        # Add files read (only if no edits, to keep it concise)
        if not files_edited and files_read:
            parts.append(f"read: {', '.join(files_read[:5])}")

        return " | ".join(parts) if parts else None
