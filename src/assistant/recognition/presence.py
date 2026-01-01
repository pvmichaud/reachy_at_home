"""
Presence detection service.

Continuously monitors the camera for family members and triggers
appropriate greetings and notifications.

Architecture:
- Runs as background task polling camera at configurable interval
- Uses FaceRecognizer for identification
- Maintains greeting cooldowns to avoid repetition
- Emits events for detected presence changes
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass, field

from .face import FaceRecognizer

logger = logging.getLogger(__name__)


@dataclass
class PresenceEvent:
    """Event emitted when presence is detected or changes."""
    user_id: Optional[str]
    confidence: float
    timestamp: datetime
    is_new_arrival: bool  # True if first detection after absence
    is_unknown: bool  # True if face detected but not recognized


@dataclass
class UserPresence:
    """Tracks presence state for a single user."""
    user_id: str
    last_seen: datetime
    last_greeted: Optional[datetime] = None
    is_present: bool = False


class PresenceDetector:
    """
    Continuous presence detection service.

    Usage:
        detector = PresenceDetector(
            face_recognizer=recognizer,
            camera_getter=reachy.get_camera_frame,
            on_person_detected=handle_greeting
        )
        await detector.start()

        # ... later
        await detector.stop()
    """

    def __init__(
        self,
        face_recognizer: FaceRecognizer,
        camera_getter: Callable,
        on_person_detected: Optional[Callable[[PresenceEvent], Any]] = None,
        on_unknown_face: Optional[Callable[[PresenceEvent], Any]] = None,
        poll_interval: float = 2.0,
        greeting_cooldown: float = 300.0,  # 5 minutes
        absence_threshold: float = 60.0,  # 1 minute
    ):
        """
        Initialize presence detector.

        Args:
            face_recognizer: Initialized FaceRecognizer instance
            camera_getter: Async function that returns camera frame (BGR numpy array)
            on_person_detected: Callback when known person is detected
            on_unknown_face: Callback when unknown face is detected
            poll_interval: Seconds between camera polls
            greeting_cooldown: Seconds before greeting same person again
            absence_threshold: Seconds of no detection before considered "left"
        """
        self.recognizer = face_recognizer
        self.camera_getter = camera_getter
        self.on_person_detected = on_person_detected
        self.on_unknown_face = on_unknown_face
        self.poll_interval = poll_interval
        self.greeting_cooldown = timedelta(seconds=greeting_cooldown)
        self.absence_threshold = timedelta(seconds=absence_threshold)

        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._user_presence: Dict[str, UserPresence] = {}

    async def start(self):
        """Start the presence detection loop."""
        if self._running:
            logger.warning("Presence detector already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._detection_loop())
        logger.info(f"Presence detection started (interval={self.poll_interval}s)")

    async def stop(self):
        """Stop the presence detection loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("Presence detection stopped")

    async def _detection_loop(self):
        """Main detection loop."""
        while self._running:
            try:
                await self._check_presence()
            except Exception as e:
                logger.error(f"Error in presence detection: {e}")

            await asyncio.sleep(self.poll_interval)

    async def _check_presence(self):
        """Check camera for faces and process detections."""
        # Get camera frame
        frame = await self.camera_getter()
        if frame is None:
            logger.debug("No frame from camera")
            return

        now = datetime.now()

        # Try to recognize face
        user_id, confidence = self.recognizer.recognize(frame, is_bgr=True)

        if user_id:
            # Known person detected
            await self._handle_known_person(user_id, confidence, now)
        else:
            # Check if there's an unknown face
            faces = self.recognizer.detect_faces(frame, is_bgr=True)
            if faces:
                await self._handle_unknown_face(confidence, now)

        # Check for people who have left
        await self._check_departures(now)

    async def _handle_known_person(
        self,
        user_id: str,
        confidence: float,
        now: datetime
    ):
        """Handle detection of a known person."""
        # Get or create presence record
        if user_id not in self._user_presence:
            self._user_presence[user_id] = UserPresence(user_id=user_id, last_seen=now)

        presence = self._user_presence[user_id]
        was_present = presence.is_present

        # Update presence
        presence.last_seen = now
        presence.is_present = True

        # Determine if this is a new arrival
        is_new_arrival = not was_present

        # Check if we should greet
        should_greet = False
        if presence.last_greeted is None:
            should_greet = True
        elif now - presence.last_greeted > self.greeting_cooldown:
            should_greet = True

        if should_greet and self.on_person_detected:
            event = PresenceEvent(
                user_id=user_id,
                confidence=confidence,
                timestamp=now,
                is_new_arrival=is_new_arrival,
                is_unknown=False
            )

            try:
                result = self.on_person_detected(event)
                if asyncio.iscoroutine(result):
                    await result
                presence.last_greeted = now
                logger.info(f"Greeted {user_id} (confidence={confidence:.2f})")
            except Exception as e:
                logger.error(f"Error in person detected callback: {e}")

    async def _handle_unknown_face(self, confidence: float, now: datetime):
        """Handle detection of an unknown face."""
        if self.on_unknown_face:
            event = PresenceEvent(
                user_id=None,
                confidence=confidence,
                timestamp=now,
                is_new_arrival=True,
                is_unknown=True
            )

            try:
                result = self.on_unknown_face(event)
                if asyncio.iscoroutine(result):
                    await result
                logger.debug("Unknown face detected")
            except Exception as e:
                logger.error(f"Error in unknown face callback: {e}")

    async def _check_departures(self, now: datetime):
        """Check for users who have left (not seen recently)."""
        for user_id, presence in self._user_presence.items():
            if presence.is_present:
                if now - presence.last_seen > self.absence_threshold:
                    presence.is_present = False
                    logger.debug(f"{user_id} has left (absent for {self.absence_threshold})")

    def get_present_users(self) -> list:
        """Get list of currently present users."""
        return [
            p.user_id for p in self._user_presence.values()
            if p.is_present
        ]

    def is_user_present(self, user_id: str) -> bool:
        """Check if a specific user is currently present."""
        presence = self._user_presence.get(user_id)
        return presence.is_present if presence else False

    def reset_greeting(self, user_id: str):
        """Reset greeting cooldown for a user (force re-greet on next detection)."""
        if user_id in self._user_presence:
            self._user_presence[user_id].last_greeted = None

    @property
    def is_running(self) -> bool:
        """Check if detection loop is running."""
        return self._running
