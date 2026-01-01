#!/usr/bin/env python3
"""
Family member enrollment script.

This script guides the user through enrolling face and voice data
for each family member. The enrolled data is used for recognition.

Usage:
    python scripts/enroll_family.py

    # Enroll specific person
    python scripts/enroll_family.py --name Patrick --role parent

    # Use custom Reachy host
    python scripts/enroll_family.py --reachy-host 10.0.0.48
"""

import asyncio
import sys
import argparse
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from assistant.recognition.face import FaceRecognizer
from assistant.integrations.reachy import ReachyController
from assistant.config import settings


async def capture_enrollment_images(
    reachy: ReachyController,
    user_name: str,
    num_samples: int = 5,
    delay_between: float = 2.0
) -> list:
    """
    Capture enrollment images from Reachy's camera.

    Args:
        reachy: Connected ReachyController
        user_name: Name for prompts
        num_samples: Number of images to capture
        delay_between: Seconds between captures

    Returns:
        List of captured BGR images
    """
    poses = [
        "looking straight at the camera",
        "slightly to the LEFT",
        "slightly to the RIGHT",
        "slightly UP",
        "slightly DOWN"
    ]

    images = []

    print(f"\n  We'll capture {num_samples} photos from different angles.")
    print("  Please position yourself in front of the camera.\n")

    for i in range(num_samples):
        pose = poses[i] if i < len(poses) else "at the camera"
        print(f"  [{i+1}/{num_samples}] Look {pose}...")

        # Countdown
        for countdown in range(3, 0, -1):
            print(f"    Capturing in {countdown}...", end="\r")
            await asyncio.sleep(1)

        # Capture frame
        frame = await reachy.get_camera_frame()
        if frame is not None:
            images.append(frame)
            print(f"    Captured!                    ")
        else:
            print(f"    Failed to capture frame")

        if i < num_samples - 1:
            await asyncio.sleep(delay_between)

    return images


async def enroll_face(
    reachy: ReachyController,
    recognizer: FaceRecognizer,
    user_name: str
) -> bool:
    """
    Capture and enroll face images for a user.

    Args:
        reachy: Connected ReachyController
        recognizer: Initialized FaceRecognizer
        user_name: Name of the family member

    Returns:
        True if enrollment successful
    """
    print(f"\n=== Face Enrollment for {user_name} ===")

    # Check if already enrolled
    if user_name.lower() in recognizer.get_enrolled_users():
        response = input(f"  {user_name} is already enrolled. Re-enroll? (y/n): ").strip().lower()
        if response != 'y':
            print("  Keeping existing enrollment.")
            return True

    # Capture images
    images = await capture_enrollment_images(reachy, user_name)

    if not images:
        print("  No images captured!")
        return False

    print(f"\n  Captured {len(images)} images. Processing...")

    # Enroll with FaceRecognizer
    success = recognizer.enroll(
        user_id=user_name.lower(),
        images=images,
        save_images=True,
        is_bgr=True  # Camera returns BGR
    )

    if success:
        print(f"  ✓ Face enrollment complete for {user_name}")
    else:
        print(f"  ✗ Face enrollment failed - no faces detected in images")

    return success


async def test_recognition(
    reachy: ReachyController,
    recognizer: FaceRecognizer,
    user_name: str
) -> bool:
    """
    Test recognition after enrollment.

    Args:
        reachy: Connected ReachyController
        recognizer: Initialized FaceRecognizer
        user_name: Expected name

    Returns:
        True if recognition successful
    """
    print(f"\n  Testing recognition for {user_name}...")
    print("  Look at the camera...")

    await asyncio.sleep(2)

    frame = await reachy.get_camera_frame()
    if frame is None:
        print("  Failed to capture test frame")
        return False

    detected_id, confidence = recognizer.recognize(frame, is_bgr=True)

    if detected_id:
        if detected_id == user_name.lower():
            print(f"  ✓ Recognized as {detected_id} (confidence: {confidence:.0%})")
            return True
        else:
            print(f"  ✗ Recognized as {detected_id} instead of {user_name}")
            return False
    else:
        print(f"  ✗ Face not recognized (confidence: {confidence:.0%})")
        return False


async def enroll_voice(user_name: str) -> bool:
    """
    Capture and enroll voice samples for a user.

    Args:
        user_name: Name of the family member

    Returns:
        True if enrollment successful
    """
    print(f"\n=== Voice Enrollment for {user_name} ===")
    print("  [Voice enrollment will be implemented in a future update]")
    return True


async def enroll_family_member(
    reachy: ReachyController,
    recognizer: FaceRecognizer,
    name: str,
    role: str
) -> bool:
    """
    Full enrollment process for one family member.

    Args:
        reachy: Connected ReachyController
        recognizer: Initialized FaceRecognizer
        name: Family member's name
        role: 'parent' or 'child'

    Returns:
        True if all enrollments successful
    """
    print(f"\n{'='*50}")
    print(f"Enrolling: {name} ({role})")
    print('='*50)

    # Face enrollment
    face_ok = await enroll_face(reachy, recognizer, name)

    # Test recognition
    if face_ok:
        test_ok = await test_recognition(reachy, recognizer, name)
        if not test_ok:
            retry = input("  Recognition test failed. Retry enrollment? (y/n): ").strip().lower()
            if retry == 'y':
                face_ok = await enroll_face(reachy, recognizer, name)

    # Voice enrollment (placeholder for now)
    voice_ok = await enroll_voice(name)

    if face_ok:
        print(f"\n✓ {name} enrolled successfully!")
        return True
    else:
        print(f"\n✗ Enrollment incomplete for {name}")
        return False


async def interactive_enrollment(reachy: ReachyController, recognizer: FaceRecognizer):
    """Interactive enrollment flow for multiple family members."""
    print("="*50)
    print("Reachy Home Assistant - Family Enrollment")
    print("="*50)
    print()
    print("This script will help you enroll each family member")
    print("for face and voice recognition.")
    print()

    # Get family members
    family = []

    print("Enter family members (empty name to finish):")
    while True:
        name = input("  Name: ").strip()
        if not name:
            break

        role = input("  Role (parent/child): ").strip().lower()
        if role not in ['parent', 'child']:
            print("  Invalid role, defaulting to 'parent'")
            role = 'parent'

        family.append({'name': name, 'role': role})
        print()

    if not family:
        print("No family members entered. Exiting.")
        return

    print(f"\nEnrolling {len(family)} family members...")

    # Enroll each member
    for member in family:
        await enroll_family_member(reachy, recognizer, member['name'], member['role'])

    print("\n" + "="*50)
    print("Enrollment Complete!")
    print("="*50)
    enrolled = recognizer.get_enrolled_users()
    print(f"\nEnrolled users: {', '.join(enrolled)}")
    print()
    print("You can now start the assistant with:")
    print("  python -m assistant.main")
    print()


async def main():
    """Main enrollment flow."""
    parser = argparse.ArgumentParser(description="Enroll family members for recognition")
    parser.add_argument("--name", help="Name of person to enroll")
    parser.add_argument("--role", choices=["parent", "child"], default="parent")
    parser.add_argument("--reachy-host", default=settings.reachy_host,
                        help=f"Reachy host (default: {settings.reachy_host})")
    parser.add_argument("--camera-port", type=int, default=settings.reachy_camera_port,
                        help=f"Camera port (default: {settings.reachy_camera_port})")
    args = parser.parse_args()

    # Initialize Reachy connection
    print(f"Connecting to Reachy at {args.reachy_host}...")
    reachy = ReachyController(
        host=args.reachy_host,
        camera_port=args.camera_port
    )
    await reachy.connect()

    # Test camera access
    print("Testing camera access...")
    frame = await reachy.get_camera_frame()
    if frame is None:
        print(f"ERROR: Cannot access camera at http://{args.reachy_host}:{args.camera_port}/frame")
        print("Make sure the MJPEG bridge is running on the Reachy.")
        return

    print(f"Camera OK - frame size: {frame.shape[1]}x{frame.shape[0]}")

    # Initialize face recognizer
    recognizer = FaceRecognizer(
        threshold=settings.face_recognition_threshold,
        data_dir=Path("data/faces")
    )
    await recognizer.initialize()

    if args.name:
        # Single person enrollment
        await enroll_family_member(reachy, recognizer, args.name, args.role)
    else:
        # Interactive mode
        await interactive_enrollment(reachy, recognizer)

    # Cleanup
    await reachy.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
