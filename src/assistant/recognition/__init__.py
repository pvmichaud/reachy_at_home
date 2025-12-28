"""
Recognition modules for identifying family members.

This package provides:
- Face recognition using InsightFace
- Voice/speaker recognition using pyannote
"""

from .face import FaceRecognizer
from .voice import VoiceRecognizer

__all__ = ["FaceRecognizer", "VoiceRecognizer"]
