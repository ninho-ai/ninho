"""
Ninho Core Library

LLM-agnostic library for AI coding context management.
"""

from .storage import Storage, ProjectStorage
from .capture import Capture
from .learnings import Learnings
from .prd import PRD
from .pr_integration import PRIntegration

__version__ = "1.0.0"
__all__ = ["Storage", "ProjectStorage", "Capture", "Learnings", "PRD", "PRIntegration"]
