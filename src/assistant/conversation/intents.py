"""
Intent recognition and routing module.

Responsibilities:
- Classify user intents from text
- Route to appropriate handlers
- Handle quick-response intents locally
"""

from typing import Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Intent(Enum):
    """Known user intents."""
    GREETING = "greeting"
    FAREWELL = "farewell"
    CALENDAR_QUERY = "calendar_query"
    REMINDER_SET = "reminder_set"
    TASK_QUERY = "task_query"
    TASK_UPDATE = "task_update"
    WEATHER = "weather"
    GENERAL_CHAT = "general_chat"
    HELP = "help"
    UNKNOWN = "unknown"


class IntentRecognizer:
    """
    Recognize user intents from text.

    Usage:
        recognizer = IntentRecognizer()
        intent, confidence = recognizer.classify("What's the weather?")
    """

    def __init__(self):
        self.patterns: dict[Intent, list[str]] = {}

    def classify(self, text: str) -> Tuple[Intent, float]:
        """
        Classify the intent of user text.

        Args:
            text: User's transcribed speech

        Returns:
            Tuple of (Intent, confidence score)
        """
        # TODO: Implement
        # - Pattern matching for common intents
        # - Fall back to GENERAL_CHAT for complex queries
        pass

    def extract_entities(self, text: str, intent: Intent) -> dict:
        """
        Extract relevant entities from text based on intent.

        Args:
            text: User's transcribed speech
            intent: Classified intent

        Returns:
            Dict of extracted entities (times, names, etc.)
        """
        # TODO: Implement
        # - Time expressions
        # - Names
        # - Task/event references
        pass

    def should_use_llm(self, intent: Intent) -> bool:
        """
        Determine if this intent needs LLM processing.

        Some intents (greeting, time) can be handled locally.
        """
        local_intents = {Intent.GREETING, Intent.FAREWELL, Intent.HELP}
        return intent not in local_intents
