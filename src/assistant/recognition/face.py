"""
Face recognition module using face_recognition library.

Responsibilities:
- Detect faces in camera frames
- Generate 128-dimensional face encodings
- Match against enrolled family members
- Handle enrollment of new faces
- Preserve reference images for future library migration

Uses dlib's face recognition model via face_recognition library.

Performance notes (tested on Jetson Orin NX):
- Processing time: ~1-2 seconds per 1080x1920 frame
- Confidence: 65-80% typical for good matches
- Threshold: 0.6 works well for family recognition
"""

import numpy as np
from typing import Optional, Tuple, List, Dict
from pathlib import Path
import logging
import json
import cv2
from datetime import datetime

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

        # Enroll a family member (saves images for future reference)
        success = recognizer.enroll("patrick", face_images, save_images=True)

        # Recognize from frame
        user_id, confidence = recognizer.recognize(frame)
    """

    def __init__(
        self,
        threshold: float = 0.6,
        data_dir: Optional[Path] = None
    ):
        """
        Initialize face recognizer.

        Args:
            threshold: Distance threshold for matching (lower = stricter)
                      Default 0.6 is recommended by face_recognition library
            data_dir: Directory for face data (encodings + reference images)
        """
        self.threshold = threshold
        self.data_dir = Path(data_dir) if data_dir else Path("data/faces")
        self.encodings_path = self.data_dir / "encodings.json"
        self.images_dir = self.data_dir / "images"
        self.enrolled_faces: Dict[str, List[np.ndarray]] = {}
        self._initialized = False

    async def initialize(self):
        """Load the face recognition system and any saved encodings."""
        if not FACE_RECOGNITION_AVAILABLE:
            logger.error("Cannot initialize - face_recognition library not available")
            return

        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)

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
                json.dump(data, f, indent=2)
            logger.info(f"Saved encodings for {len(self.enrolled_faces)} users")
        except Exception as e:
            logger.error(f"Failed to save encodings: {e}")

    def _select_largest_face(self, face_locations: List[Tuple]) -> Tuple:
        """
        Select the largest face when multiple are detected.

        Args:
            face_locations: List of (top, right, bottom, left) tuples

        Returns:
            Location of largest face by area
        """
        if len(face_locations) == 1:
            return face_locations[0]

        # Calculate area for each face
        def face_area(loc):
            top, right, bottom, left = loc
            return (bottom - top) * (right - left)

        return max(face_locations, key=face_area)

    def _ensure_rgb(self, image: np.ndarray) -> np.ndarray:
        """
        Ensure image is in RGB format.
        Camera typically returns BGR, face_recognition expects RGB.

        Args:
            image: Input image (BGR or RGB)

        Returns:
            Image in RGB format
        """
        # Check if likely BGR by looking at channel order
        # This is a heuristic - caller should ideally specify format
        if len(image.shape) == 3 and image.shape[2] == 3:
            # Assume BGR from OpenCV/camera, convert to RGB
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image

    def enroll(
        self,
        user_id: str,
        images: List[np.ndarray],
        save_images: bool = True,
        is_bgr: bool = True
    ) -> bool:
        """
        Enroll a user with multiple face images.

        Extracts face encodings from each image and stores them.
        Multiple encodings per user improve recognition robustness.
        Reference images are saved for potential future library migration.

        Args:
            user_id: Unique identifier for the user
            images: List of face images
            save_images: Whether to save reference images to disk
            is_bgr: If True, convert from BGR to RGB (default for camera images)

        Returns:
            True if at least one face was successfully enrolled
        """
        if not FACE_RECOGNITION_AVAILABLE:
            logger.error("face_recognition not available")
            return False

        encodings = []
        user_images_dir = self.images_dir / user_id

        if save_images:
            user_images_dir.mkdir(parents=True, exist_ok=True)

        for i, image in enumerate(images):
            # Convert to RGB if needed
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if is_bgr else image

            # Detect face locations
            face_locations = face_recognition.face_locations(rgb_image)

            if len(face_locations) == 0:
                logger.warning(f"No face found in image {i+1} for user {user_id}")
                continue

            # Select largest face if multiple detected
            if len(face_locations) > 1:
                logger.warning(f"Multiple faces in image {i+1}, using largest")
                face_location = self._select_largest_face(face_locations)
                face_locations = [face_location]

            # Get encoding for selected face
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            if face_encodings:
                encodings.append(face_encodings[0])
                logger.debug(f"Encoded face {i+1} for user {user_id}")

                # Save reference image (in original BGR for compatibility)
                if save_images:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    image_path = user_images_dir / f"sample_{i+1}_{timestamp}.jpg"
                    cv2.imwrite(str(image_path), image)
                    logger.debug(f"Saved reference image: {image_path}")

        if not encodings:
            logger.error(f"No faces could be encoded for user {user_id}")
            return False

        # Store encodings
        self.enrolled_faces[user_id] = encodings
        self._save_encodings()

        logger.info(f"Enrolled user {user_id} with {len(encodings)} face encodings")
        return True

    def recognize(
        self,
        frame: np.ndarray,
        is_bgr: bool = True
    ) -> Tuple[Optional[str], float]:
        """
        Recognize a face in a camera frame.

        Args:
            frame: Camera frame
            is_bgr: If True, convert from BGR to RGB (default for camera images)

        Returns:
            Tuple of (user_id or None, confidence score 0-1)
            Confidence is 1.0 - distance, so higher is better
        """
        if not FACE_RECOGNITION_AVAILABLE:
            return None, 0.0

        if not self.enrolled_faces:
            logger.debug("No enrolled faces to match against")
            return None, 0.0

        # Convert to RGB if needed
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) if is_bgr else frame

        # Detect faces
        face_locations = face_recognition.face_locations(rgb_frame)
        if not face_locations:
            return None, 0.0

        # Select largest face if multiple
        if len(face_locations) > 1:
            face_location = self._select_largest_face(face_locations)
            face_locations = [face_location]

        # Get encoding for selected face
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        if not face_encodings:
            return None, 0.0

        unknown_encoding = face_encodings[0]

        # Compare against all enrolled faces
        best_match: Optional[str] = None
        best_distance = float('inf')

        for user_id, user_encodings in self.enrolled_faces.items():
            # Compare against all encodings for this user
            distances = face_recognition.face_distance(user_encodings, unknown_encoding)
            min_distance = float(np.min(distances))

            if min_distance < best_distance:
                best_distance = min_distance
                best_match = user_id

        # Check threshold
        confidence = max(0.0, 1.0 - best_distance)

        if best_distance <= self.threshold:
            logger.debug(f"Recognized {best_match} with confidence {confidence:.2f}")
            return best_match, confidence
        else:
            logger.debug(f"Best match {best_match} below threshold (distance={best_distance:.2f})")
            return None, confidence

    def detect_faces(self, frame: np.ndarray, is_bgr: bool = True) -> List[Dict]:
        """
        Detect all faces in a frame without identification.

        Args:
            frame: Camera frame
            is_bgr: If True, convert from BGR to RGB

        Returns:
            List of detected faces with bounding boxes:
            [{"top": int, "right": int, "bottom": int, "left": int, "area": int}, ...]
        """
        if not FACE_RECOGNITION_AVAILABLE:
            return []

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) if is_bgr else frame
        face_locations = face_recognition.face_locations(rgb_frame)

        return [
            {
                "top": top,
                "right": right,
                "bottom": bottom,
                "left": left,
                "area": (bottom - top) * (right - left)
            }
            for (top, right, bottom, left) in face_locations
        ]

    def get_encoding(
        self,
        frame: np.ndarray,
        is_bgr: bool = True
    ) -> Optional[np.ndarray]:
        """
        Get face encoding from a frame (for database storage).

        Args:
            frame: Camera frame containing a face
            is_bgr: If True, convert from BGR to RGB

        Returns:
            128-dimensional face encoding, or None if no face found
        """
        if not FACE_RECOGNITION_AVAILABLE:
            return None

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) if is_bgr else frame
        face_locations = face_recognition.face_locations(rgb_frame)

        if not face_locations:
            return None

        # Select largest face if multiple
        if len(face_locations) > 1:
            face_location = self._select_largest_face(face_locations)
            face_locations = [face_location]

        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
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

    def get_enrolled_users(self) -> List[str]:
        """Get list of enrolled user IDs."""
        return list(self.enrolled_faces.keys())

    @property
    def is_available(self) -> bool:
        """Check if face recognition is available."""
        return FACE_RECOGNITION_AVAILABLE and self._initialized
