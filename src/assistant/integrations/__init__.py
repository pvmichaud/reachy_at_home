"""
External service integrations.

This package provides:
- Claude API client for conversation
- Cozi calendar/task sync
- Reachy Mini robot control
"""

from .claude import ClaudeClient
from .cozi import CoziSync
from .reachy import ReachyController

__all__ = ["ClaudeClient", "CoziSync", "ReachyController"]
