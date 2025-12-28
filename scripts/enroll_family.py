#!/usr/bin/env python3
"""
Family member enrollment script.

This script guides the user through enrolling face and voice data
for each family member. The enrolled data is used for recognition.

Usage:
    python scripts/enroll_family.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


async def enroll_face(user_name: str) -> bool:
    """
    Capture and enroll face images for a user.

    Args:
        user_name: Name of the family member

    Returns:
        True if enrollment successful
    """
    print(f"\n=== Face Enrollment for {user_name} ===")
    print("We'll capture 5 photos from different angles.")
    print("Please look at the camera and follow the prompts.")
    print()

    # TODO: Implement
    # - Open camera
    # - Guide user through poses (front, left, right, up, down)
    # - Capture frames
    # - Extract face embeddings
    # - Average and store

    print("  [TODO: Face enrollment not yet implemented]")
    return True


async def enroll_voice(user_name: str) -> bool:
    """
    Capture and enroll voice samples for a user.

    Args:
        user_name: Name of the family member

    Returns:
        True if enrollment successful
    """
    print(f"\n=== Voice Enrollment for {user_name} ===")
    print("We'll record 3 voice samples.")
    print("Please speak clearly when prompted.")
    print()

    prompts = [
        "Please say: 'Hey Reachy, what's on my calendar today?'",
        "Please say: 'Remind me to check my email at 3 PM.'",
        "Please say: 'What's the weather like outside?'"
    ]

    # TODO: Implement
    # - Record each prompt
    # - Extract voice embeddings
    # - Average and store

    print("  [TODO: Voice enrollment not yet implemented]")
    return True


async def enroll_family_member(name: str, role: str) -> bool:
    """
    Full enrollment process for one family member.

    Args:
        name: Family member's name
        role: 'parent' or 'child'

    Returns:
        True if all enrollments successful
    """
    print(f"\n{'='*50}")
    print(f"Enrolling: {name} ({role})")
    print('='*50)

    # Face enrollment
    face_ok = await enroll_face(name)

    # Voice enrollment
    voice_ok = await enroll_voice(name)

    if face_ok and voice_ok:
        print(f"\n✓ {name} enrolled successfully!")
        return True
    else:
        print(f"\n✗ Enrollment incomplete for {name}")
        return False


async def main():
    """Main enrollment flow."""
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
        await enroll_family_member(member['name'], member['role'])

    print("\n" + "="*50)
    print("Enrollment Complete!")
    print("="*50)
    print()
    print("You can now start the assistant with:")
    print("  python -m assistant.main")
    print()


if __name__ == "__main__":
    asyncio.run(main())
