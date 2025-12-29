"""
Reachy Mini robot control integration.

Responsibilities:
- Connect to Reachy Mini over network via REST API
- Get camera frames from MJPEG bridge (port 8081)
- Control expressions and movements (port 8000)
- Manage robot state and availability

Architecture:
- Port 8000: REST API for motors, status, daemon control
- Port 8081: Custom MJPEG bridge for camera frames
"""

from typing import Optional
import logging
import numpy as np
import httpx
import cv2

logger = logging.getLogger(__name__)


class ReachyController:
    """
    Control interface for Reachy Mini robot using REST API.

    Usage:
        reachy = ReachyController(host="10.0.0.48")
        await reachy.connect()

        # Get camera frame for face recognition
        frame = await reachy.get_camera_frame()

        # Control robot
        await reachy.express("happy")
        await reachy.look_at(x=0.5, y=0.3)
        await reachy.wave()
    """

    def __init__(self, host: str, api_port: int = 8000, camera_port: int = 8081):
        self.host = host
        self.api_port = api_port
        self.camera_port = camera_port
        self.api_base_url = f"http://{host}:{api_port}"
        self.camera_url = f"http://{host}:{camera_port}/frame"
        self.client: Optional[httpx.AsyncClient] = None
        self.is_connected = False

    async def connect(self):
        """Establish connection to Reachy Mini."""
        self.client = httpx.AsyncClient(timeout=10.0)
        try:
            # Test connection by checking status
            response = await self.client.get(f"{self.api_base_url}/")
            if response.status_code == 200:
                self.is_connected = True
                logger.info(f"Connected to Reachy at {self.host} (API:{self.api_port}, Camera:{self.camera_port})")
            else:
                logger.warning(f"Reachy API returned status {response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to Reachy: {e}")
            self.is_connected = False

    async def disconnect(self):
        """Disconnect from Reachy Mini."""
        if self.client:
            await self.client.aclose()
            self.client = None
        self.is_connected = False
        logger.info("Disconnected from Reachy")

    async def get_camera_frame(self) -> Optional[np.ndarray]:
        """
        Get a single frame from Reachy's camera via MJPEG bridge.

        Returns:
            BGR image as numpy array, or None if failed
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(self.camera_url)
                if response.status_code == 200:
                    # Decode JPEG to numpy array
                    img_array = np.frombuffer(response.content, np.uint8)
                    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    return frame
                else:
                    logger.warning(f"Camera returned status {response.status_code}")
                    return None
        except httpx.RequestError as e:
            logger.error(f"Failed to get camera frame: {e}")
            return None

    def get_camera_frame_sync(self) -> Optional[np.ndarray]:
        """
        Synchronous version of get_camera_frame for use outside async context.

        Returns:
            BGR image as numpy array, or None if failed
        """
        import requests
        try:
            response = requests.get(self.camera_url, timeout=5.0)
            if response.status_code == 200:
                img_array = np.frombuffer(response.content, np.uint8)
                frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                return frame
            else:
                logger.warning(f"Camera returned status {response.status_code}")
                return None
        except requests.RequestException as e:
            logger.error(f"Failed to get camera frame: {e}")
            return None

    async def express(self, emotion: str):
        """
        Display an emotion/expression.

        Args:
            emotion: One of "happy", "sad", "surprised", "thinking", "neutral"
        """
        if not self.client:
            logger.warning("Not connected to Reachy")
            return

        # TODO: Implement when we discover the exact endpoint
        # await self.client.post(f"{self.api_base_url}/expression", json={"emotion": emotion})
        logger.info(f"Expression: {emotion}")

    async def look_at(self, x: float, y: float):
        """
        Direct Reachy's gaze to a point.

        Args:
            x: Horizontal position (-1 to 1)
            y: Vertical position (-1 to 1)
        """
        if not self.client:
            logger.warning("Not connected to Reachy")
            return

        # TODO: Implement when we discover the exact endpoint
        logger.info(f"Look at: ({x}, {y})")

    async def wave(self):
        """Perform a friendly wave gesture."""
        if not self.client:
            logger.warning("Not connected to Reachy")
            return

        # TODO: Implement when we discover the exact endpoint
        logger.info("Wave gesture")

    async def nod(self):
        """Perform a nodding gesture (agreement)."""
        if not self.client:
            logger.warning("Not connected to Reachy")
            return

        # TODO: Implement when we discover the exact endpoint
        logger.info("Nod gesture")

    async def shake_head(self):
        """Perform a head shake gesture (disagreement)."""
        if not self.client:
            logger.warning("Not connected to Reachy")
            return

        # TODO: Implement when we discover the exact endpoint
        logger.info("Shake head gesture")

    async def attention(self):
        """Perk up - show attention/listening."""
        if not self.client:
            logger.warning("Not connected to Reachy")
            return

        # TODO: Implement when we discover the exact endpoint
        logger.info("Attention pose")

    async def idle(self):
        """Return to idle/neutral state."""
        if not self.client:
            logger.warning("Not connected to Reachy")
            return

        # TODO: Implement when we discover the exact endpoint
        logger.info("Idle state")

    @property
    def available(self) -> bool:
        """Check if robot is available for commands."""
        return self.is_connected
