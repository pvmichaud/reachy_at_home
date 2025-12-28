"""
Wake word detection module using OpenWakeWord.

Responsibilities:
- Continuously listen for wake word ("Hey Reachy")
- Trigger recording when wake word detected
- Handle false positive filtering
"""

import numpy as np
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)


class WakeWordDetector:
    """
    Wake word detection using OpenWakeWord.

    Usage:
        detector = WakeWordDetector()
        await detector.initialize()

        # Blocking detection
        await detector.wait_for_wake_word()

        # Or with callback
        detector.start(on_detected=handle_wake_word)
    """

    def __init__(self, wake_word: str = "hey_reachy", threshold: float = 0.5):
        self.wake_word = wake_word
        self.threshold = threshold
        self.model = None
        self.is_listening = False

    async def initialize(self):
        """Load the wake word model."""
        # TODO: Implement
        # from openwakeword import Model
        # self.model = Model(
        #     wakeword_models=[self.wake_word],
        #     inference_framework="onnx"
        # )
        logger.info(f"Wake word detector initialized: {self.wake_word}")

    def detect(self, audio_chunk: np.ndarray) -> bool:
        """
        Check if audio chunk contains wake word.

        Args:
            audio_chunk: Audio samples (16kHz mono, ~80ms)

        Returns:
            True if wake word detected
        """
        # TODO: Implement
        # prediction = self.model.predict(audio_chunk)
        # return prediction[self.wake_word] > self.threshold
        pass

    async def wait_for_wake_word(self) -> bool:
        """
        Block until wake word is detected.

        Returns:
            True when wake word detected
        """
        # TODO: Implement
        # - Open audio stream
        # - Process chunks until wake word detected
        # - Return True
        pass

    def start(self, on_detected: Callable[[], None]):
        """
        Start continuous wake word detection.

        Args:
            on_detected: Callback function when wake word detected
        """
        # TODO: Implement
        # - Start background thread/task
        # - Call on_detected when wake word found
        pass

    def stop(self):
        """Stop continuous detection."""
        self.is_listening = False
