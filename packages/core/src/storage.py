"""
Storage module for Ninho.

Handles file read/write operations and directory management.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Union


class Storage:
    """File storage abstraction for Ninho."""

    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize storage.

        Args:
            base_path: Base path for storage. Defaults to ~/.ninho
        """
        self.base_path = Path(base_path or os.path.expanduser("~/.ninho"))
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create required directories if they don't exist."""
        directories = [
            self.base_path / "daily",
            self.base_path / "storage",
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @property
    def daily_path(self) -> Path:
        """Get path for daily learnings directory."""
        return self.base_path / "daily"

    def get_daily_file(self, date: Optional[datetime] = None) -> Path:
        """
        Get path for a specific day's learnings file.

        Args:
            date: Date for the file. Defaults to today.

        Returns:
            Path to the daily file.
        """
        if date is None:
            date = datetime.now()
        return self.daily_path / f"{date.strftime('%Y-%m-%d')}.md"

    def read_file(self, path: Union[str, Path]) -> Optional[str]:
        """
        Read contents of a file.

        Args:
            path: Path to the file.

        Returns:
            File contents or None if file doesn't exist.
        """
        path = Path(path)
        if path.exists():
            return path.read_text(encoding="utf-8")
        return None

    def write_file(self, path: Union[str, Path], content: str) -> None:
        """
        Write content to a file.

        Args:
            path: Path to the file.
            content: Content to write.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def append_file(self, path: Union[str, Path], content: str) -> None:
        """
        Append content to a file.

        Args:
            path: Path to the file.
            content: Content to append.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)

    def read_json(self, path: Union[str, Path]) -> Optional[dict]:
        """
        Read JSON file.

        Args:
            path: Path to the JSON file.

        Returns:
            Parsed JSON or None if file doesn't exist.
        """
        content = self.read_file(path)
        if content:
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return None
        return None

    def write_json(self, path: Union[str, Path], data: dict) -> None:
        """
        Write data as JSON file.

        Args:
            path: Path to the JSON file.
            data: Data to write.
        """
        self.write_file(path, json.dumps(data, indent=2))

    def get_index_path(self) -> Path:
        """Get path to learnings deduplication index."""
        return self.base_path / "learnings-index.json"

    def get_config_path(self) -> Path:
        """Get path to config file."""
        return self.base_path / "config.json"


class ProjectStorage:
    """Project-level storage for PRDs and prompts."""

    def __init__(self, project_path: str):
        """
        Initialize project storage.

        Args:
            project_path: Path to the project root.
        """
        self.project_path = Path(project_path)
        self.ninho_path = self.project_path / ".ninho"
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create required directories if they don't exist."""
        directories = [
            self.ninho_path / "prds",
            self.ninho_path / "prompts",
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @property
    def prds_path(self) -> Path:
        """Get path for PRDs directory."""
        return self.ninho_path / "prds"

    @property
    def prompts_path(self) -> Path:
        """Get path for prompts directory."""
        return self.ninho_path / "prompts"

    def get_prd_file(self, name: str) -> Path:
        """
        Get path for a specific PRD file.

        Args:
            name: Name of the PRD (without .md extension).

        Returns:
            Path to the PRD file.
        """
        return self.prds_path / f"{name}.md"

    def get_prompt_file(self, date: Optional[datetime] = None) -> Path:
        """
        Get path for a specific day's prompts file.

        Args:
            date: Date for the file. Defaults to today.

        Returns:
            Path to the prompts file.
        """
        if date is None:
            date = datetime.now()
        return self.prompts_path / f"{date.strftime('%Y-%m-%d')}.md"

    def list_prds(self) -> list[str]:
        """
        List all PRD files.

        Returns:
            List of PRD names (without .md extension).
        """
        if not self.prds_path.exists():
            return []
        return [f.stem for f in self.prds_path.glob("*.md")]

    def read_file(self, path: Union[str, Path]) -> Optional[str]:
        """Read contents of a file."""
        path = Path(path)
        if path.exists():
            return path.read_text(encoding="utf-8")
        return None

    def write_file(self, path: Union[str, Path], content: str) -> None:
        """Write content to a file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def append_file(self, path: Union[str, Path], content: str) -> None:
        """Append content to a file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)
