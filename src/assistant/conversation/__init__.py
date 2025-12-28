"""
Conversation management modules.

This package provides:
- Conversation state management
- Intent recognition and routing
- Multi-turn dialogue handling
"""

from .manager import ConversationManager
from .intents import IntentRecognizer

__all__ = ["ConversationManager", "IntentRecognizer"]
