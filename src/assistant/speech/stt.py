"""
Speech-to-text module using faster-whisper.

Responsibilities:
- Transcribe audio to text
- Handle streaming transcription
- Optimize for Jetson GPU
"""

import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SpeechToText:
    """
    Speech recognition using faster-whisper on Jetson GPU.

    Usage:
        stt = SpeechToText()
        await stt.initialize()

        text = stt.transcribe(audio)
    """

    def __init__(self, model_size: str = "small", device: str = "cuda"):
        self.model_size = model_size
        self.device = device
        self.model = None

    async def initialize(self):
        """Load the Whisper model."""
        # TODO: Implement
        # from faster_whisper import WhisperModel
        # self.model = WhisperModel(
        #     self.model_size,
        #     device=self.device,
        #     compute_type="float16"
        # )
        logger.info(f"Whisper {self.model_size} model loaded on {self.device}")

    def transcribe(self, audio: np.ndarray) -> str:
        """
        Transcribe audio to text.

        Args:
            audio: Audio array (16kHz mono)

        Returns:
            Transcribed text
        """
        # TODO: Implement
        # segments, info = self.model.transcribe(audio)
        # return " ".join([seg.text for seg in segments])
        pass

    def transcribe_with_timestamps(self, audio: np.ndarray) -> list:
        """
        Transcribe audio with word-level timestamps.

        Args:
            audio: Audio array (16kHz mono)

        Returns:
            List of (word, start_time, end_time) tuples
        """
        # TODO: Implement
        pass
