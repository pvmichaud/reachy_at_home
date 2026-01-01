"""
Recognition modules for identifying family members.

This package provides:
- Face recognition using face_recognition library (dlib)
- Voice/speaker recognition using resemblyzer
- Presence detection with greeting management
"""

from .face import FaceRecognizer
from .voice import VoiceRecognizer
from .presence import PresenceDetector, PresenceEvent

__all__ = [
    "FaceRecognizer",
    "VoiceRecognizer",
    "PresenceDetector",
    "PresenceEvent",
]
