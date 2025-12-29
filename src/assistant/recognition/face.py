"""
Face recognition module using face_recognition library.

Responsibilities:
- Detect faces in camera frames
- Generate 128-dimensional face encodings
- Match against enrolled family members
- Handle enrollment of new faces

Uses dlib's face recognition model via face_recognition library.
"""

import numpy as np
from typing import Optional, Tuple, List, Dict
from pathlib import Path
import logging
import json

logger = logging.getLogger(__name__)

# Import face_recognition - will be available on Jetson
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    logger.warning("face_recognition not available - face recognition disabled")


class FaceRecognizer:
    """
    Face recognition using face_recognition library (dlib-based).

    The face_recognition library provides:
    - Face detection (HOG-based, fast)
    - Face encoding (128-dimensional vectors)
    - Face comparison (euclidean distance)

    Usage:
        recognizer = FaceRecognizer()
        await recognizer.initialize()

        # Enroll a family member
        success = recognizer.enroll("patrick", face_images)

        # Recognize from frame
        user_id, confidence = recognizer.recognize(frame)
    """

    def __init__(self, threshold: float = 0.6, encodings_path: Optional[Path] = None):
        """
        Initialize face recognizer.

        Args:
            threshold: Distance threshold for matching (lower = stricter)
                      Default 0.6 is recommended by face_recognition library
            encodings_path: Path to save/load enrolled face encodings
        """
        self.threshold = threshold
        self.encodings_path = encodings_path or Path("data/face_encodings.json")
        self.enrolled_faces: Dict[str, List[np.ndarray]] = {}
        self._initialized = False

    async def initialize(self):
        """Load the face recognition system and any saved encodings."""
        if not FACE_RECOGNITION_AVAILABLE:
            logger.error("Cannot initialize - face_recognition library not available")
            return

        # Load saved encodings if they exist
        if self.encodings_path.exists():
            self._load_encodings()

        self._initialized = True
        logger.info(f"Face recognizer initialized with {len(self.enrolled_faces)} enrolled users")

    def _load_encodings(self):
        """Load saved face encodings from disk."""
        try:
            with open(self.encodings_path, 'r') as f:
                data = json.load(f)
                for user_id, encodings_list in data.items():
                    self.enrolled_faces[user_id] = [
                        np.array(enc) for enc in encodings_list
                    ]
            logger.info(f"Loaded encodings for {len(self.enrolled_faces)} users")
        except Exception as e:
            logger.error(f"Failed to load encodings: {e}")

    def _save_encodings(self):
        """Save face encodings to disk."""
        try:
            self.encodings_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                user_id: [enc.tolist() for enc in encodings]
                for user_id, encodings in self.enrolled_faces.items()
            }
            with open(self.encodings_path, 'w') as f:
                json.dump(data, f)
            logger.info(f"Saved encodings for {len(self.enrolled_faces)} users")
        except Exception as e:
            logger.error(f"Failed to save encodings: {e}")

    def enroll(self, user_id: str, images: List[np.ndarray]) -> bool:
        """
        Enroll a user with multiple face images.

        Extracts face encodings from each image and stores them.
        Multiple encodings per user improve recognition robustness.

        Args:
            user_id: Unique identifier for the user
            images: List of face images (RGB format, as from camera)

        Returns:
            True if at least one face was successfully enrolled
        """
        if not FACE_RECOGNITION_AVAILABLE:
            logger.error("face_recognition not available")
            return False

        encodings = []
        for i, image in enumerate(images):
            # Detect face locations
            face_locations = face_recognition.face_locations(image)

            if len(face_locations) == 0:
                logger.warning(f"No face found in image {i+1} for user {user_id}")
                continue

            if len(face_locations) > 1:
                logger.warning(f"Multiple faces in image {i+1}, using first one")

            # Get encoding for first face found
            face_encodings = face_recognition.face_encodings(image, face_locations[:1])
            if face_encodings:
                encodings.append(face_encodings[0])
                logger.debug(f"Encoded face {i+1} for user {user_id}")

        if not encodings:
            logger.error(f"No faces could be encoded for user {user_id}")
            return False

        # Store encodings
        self.enrolled_faces[user_id] = encodings
        self._save_encodings()

        logger.info(f"Enrolled user {user_id} with {len(encodings)} face encodings")
        return True

    def recognize(self, frame: np.ndarray) -> Tuple[Optional[str], float]:
        """
        Recognize a face in a camera frame.

        Args:
            frame: Camera frame (RGB format)

        Returns:
            Tuple of (user_id or None, confidence score 0-1)
            Confidence is 1.0 - distance, so higher is better
        """
        if not FACE_RECOGNITION_AVAILABLE:
            return None, 0.0

        if not self.enrolled_faces:
            logger.debug("No enrolled faces to match against")
            return None, 0.0

        # Detect faces
        face_locations = face_recognition.face_locations(frame)
        if not face_locations:
            return None, 0.0

        # Get encoding for first face
        face_encodings = face_recognition.face_encodings(frame, face_locations[:1])
        if not face_encodings:
            return None, 0.0

        unknown_encoding = face_encodings[0]

        # Compare against all enrolled faces
        best_match: Optional[str] = None
        best_distance = float('inf')

        for user_id, user_encodings in self.enrolled_faces.items():
            # Compare against all encodings for this user
            distances = face_recognition.face_distance(user_encodings, unknown_encoding)
            min_distance = np.min(distances)

            if min_distance < best_distance:
                best_distance = min_distance
                best_match = user_id

        # Check threshold
        if best_distance <= self.threshold:
            confidence = 1.0 - best_distance  # Convert distance to confidence
            logger.debug(f"Recognized {best_match} with confidence {confidence:.2f}")
            return best_match, confidence
        else:
            logger.debug(f"Best match {best_match} below threshold (distance={best_distance:.2f})")
            return None, 1.0 - best_distance

    def detect_faces(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect all faces in a frame without identification.

        Args:
            frame: Camera frame (RGB format)

        Returns:
            List of detected faces with bounding boxes:
            [{"top": int, "right": int, "bottom": int, "left": int}, ...]
        """
        if not FACE_RECOGNITION_AVAILABLE:
            return []

        face_locations = face_recognition.face_locations(frame)

        return [
            {"top": top, "right": right, "bottom": bottom, "left": left}
            for (top, right, bottom, left) in face_locations
        ]

    def get_encoding(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Get face encoding from a frame (for database storage).

        Args:
            frame: Camera frame (RGB format) containing exactly one face

        Returns:
            128-dimensional face encoding, or None if no face found
        """
        if not FACE_RECOGNITION_AVAILABLE:
            return None

        face_locations = face_recognition.face_locations(frame)
        if not face_locations:
            return None

        face_encodings = face_recognition.face_encodings(frame, face_locations[:1])
        if face_encodings:
            return face_encodings[0]
        return None

    def is_same_person(self, encoding1: np.ndarray, encoding2: np.ndarray) -> bool:
        """
        Check if two encodings are from the same person.

        Args:
            encoding1: First face encoding
            encoding2: Second face encoding

        Returns:
            True if encodings are within threshold distance
        """
        if not FACE_RECOGNITION_AVAILABLE:
            return False

        distance = face_recognition.face_distance([encoding1], encoding2)[0]
        return distance <= self.threshold

    @property
    def is_available(self) -> bool:
        """Check if face recognition is available."""
        return FACE_RECOGNITION_AVAILABLE and self._initialized
