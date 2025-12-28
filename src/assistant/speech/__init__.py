"""
Speech processing modules.

This package provides:
- Speech-to-text using faster-whisper
- Text-to-speech using Kokoro
- Wake word detection using OpenWakeWord
"""

from .stt import SpeechToText
from .tts import TextToSpeech
from .wake_word import WakeWordDetector

__all__ = ["SpeechToText", "TextToSpeech", "WakeWordDetector"]
