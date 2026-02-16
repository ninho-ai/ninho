"""
Ninho Core Library

LLM-agnostic library for AI coding context management.
"""

from .capture import Capture
from .learnings import Learnings
from .pr_integration import PRIntegration
from .prd import PRD
from .prd_capture import PRDCapture
from .storage import ProjectStorage, Storage

__version__ = "1.0.0"
__all__ = [
    "Storage",
    "ProjectStorage",
    "Capture",
    "Learnings",
    "PRD",
    "PRDCapture",
    "PRIntegration",
]
