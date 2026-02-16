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

    def get_last_assistant_summary(self, max_total: int = 300) -> Optional[str]:
        """
        Get a high-level summary of the full assistant response.

        Extracts one short highlight per text block, producing a
        semicolon-separated list of actions/messages. Appends files
        edited when applicable.

        Args:
            max_total: Maximum total length of the summary.

        Returns:
            Single-line summary string or None.
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

        # Collect highlights and file info from all assistant turns
        highlights = []
        files_edited = []
        files_read = []
        bash_actions = []

        for entry in entries[last_user_idx + 1:]:
            if entry.get("type") != "assistant":
                continue
            content = entry.get("message", {}).get("content", [])
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "text":
                    highlight = self._extract_highlight(block.get("text", ""))
                    if highlight and highlight not in highlights:
                        highlights.append(highlight)
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
                    elif name == "Bash":
                        cmd = inputs.get("command", "")
                        action = self._summarize_bash(cmd)
                        if action and action not in bash_actions:
                            bash_actions.append(action)

        if not highlights and not files_edited and not bash_actions:
            return None

        # Merge bash actions into highlights
        for action in bash_actions:
            if action not in highlights:
                highlights.append(action)

        # Build final summary
        parts = []
        if highlights:
            parts.append("; ".join(highlights))
        if files_edited:
            parts.append(f"edited: {', '.join(files_edited[:5])}")
        elif files_read:
            parts.append(f"read: {', '.join(files_read[:5])}")

        result = " | ".join(parts)
        if len(result) > max_total:
            result = result[:max_total] + "..."
        return result

    @staticmethod
    def _extract_highlight(text: str, max_len: int = 80) -> Optional[str]:
        """Extract a single short highlight from a text block."""
        if not text or not text.strip():
            return None
        # Collapse whitespace, strip markdown
        clean = re.sub(r'\s*\n\s*', ' ', text)
        clean = re.sub(r'\*\*|##|`{1,3}|---|\|', '', clean)
        clean = re.sub(r'\s{2,}', ' ', clean).strip()
        if len(clean) < 5:
            return None
        # Take first sentence
        sentence = re.split(r'(?<=[.!?])\s', clean, maxsplit=1)[0].strip()
        # Skip filler phrases
        skip = ("let me", "now let", "good", "here's", "i can see",
                "i'll", "looking at", "the user")
        lower = sentence.lower()
        if any(lower.startswith(s) for s in skip):
            # Try second sentence instead
            rest = clean[len(sentence):].strip()
            if rest:
                sentence = re.split(r'(?<=[.!?])\s', rest, maxsplit=1)[0].strip()
            else:
                return None
        if len(sentence) < 5:
            return None
        if len(sentence) > max_len:
            sentence = sentence[:max_len] + "..."
        return sentence

    @staticmethod
    def _summarize_bash(cmd: str) -> Optional[str]:
        """Extract a short action description from a bash command."""
        if not cmd:
            return None
        cmd = cmd.strip().split("&&")[0].strip()
        if cmd.startswith("git commit"):
            return "committed changes"
        if cmd.startswith("git push"):
            return "pushed to remote"
        if cmd.startswith("git add"):
            return None  # staging is implied by commit
        if "gh run watch" in cmd:
            return "CI passed" if "--exit-status" in cmd else "watched CI"
        if "gh run list" in cmd:
            return None  # minor action
        if cmd.startswith("python3 -m py_compile"):
            return "verified compilation"
        if cmd.startswith("ruff check") or cmd.startswith("python3 -m ruff"):
            return "ran linter"
        if "rm -rf" in cmd:
            return f"removed {cmd.split()[-1].rsplit('/', 1)[-1]}"
        return None
