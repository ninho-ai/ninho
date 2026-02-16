"""
Ninho Core Library

LLM-agnostic library for AI coding context management.
"""

from .storage import Storage
from .capture import Capture
from .learnings import Learnings
from .prd import PRD

__version__ = "1.0.0"
__all__ = ["Storage", "Capture", "Learnings", "PRD"]
