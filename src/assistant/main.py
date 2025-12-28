"""
Main entry point for the Reachy Home Assistant service.

This service runs continuously and:
1. Listens for wake word ("Hey Reachy")
2. Monitors for face detection (proactive greetings)
3. Processes voice commands
4. Manages conversation state
5. Coordinates with external services
"""

import asyncio
import logging
from .config import settings

logger = logging.getLogger(__name__)


async def main():
    """Main async entry point."""
    logger.info("Starting Reachy Home Assistant...")
    logger.info(f"Quiet hours: {settings.quiet_hours_start} - {settings.quiet_hours_end}")

    # TODO: Initialize components
    # - Face recognition
    # - Voice recognition
    # - Wake word detection
    # - Speech services
    # - Database connection
    # - Reachy connection

    # TODO: Start main event loop
    # - Wake word listener
    # - Face detection loop
    # - Scheduled tasks (reminders, briefings)

    logger.info("Assistant ready!")

    # Keep running
    while True:
        await asyncio.sleep(1)


def run():
    """Synchronous entry point."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
