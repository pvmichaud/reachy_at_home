"""
Chat/conversation API endpoints.

Handles:
- Send messages to Reachy
- WebSocket for real-time chat
- Conversation history
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Optional
from uuid import UUID

router = APIRouter()


@router.post("/message")
async def send_message(
    message: str,
    user_id: Optional[UUID] = None
):
    """
    Send a message to Reachy and get a response.

    Args:
        message: User's message text
        user_id: Sending user (for context)

    Returns:
        Reachy's response
    """
    # TODO: Implement
    # - Get conversation manager
    # - Process message
    # - Return response
    pass


@router.get("/history")
async def get_history(
    user_id: Optional[UUID] = None,
    limit: int = 50
):
    """
    Get conversation history.

    Args:
        user_id: Filter to specific user
        limit: Maximum messages to return

    Returns:
        Recent conversation messages
    """
    # TODO: Implement
    pass


@router.websocket("/ws")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat.

    Allows bidirectional communication for:
    - Sending messages
    - Receiving responses
    - Status updates
    """
    await websocket.accept()

    try:
        while True:
            # Receive message
            data = await websocket.receive_json()

            # TODO: Process message
            # response = await conversation_manager.process(...)

            # Send response
            # await websocket.send_json({"response": response})
            pass

    except WebSocketDisconnect:
        pass  # Client disconnected
