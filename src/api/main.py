"""
FastAPI backend for the Reachy Home Assistant web application.

Provides REST and WebSocket APIs for:
- User management
- Calendar/schedule access
- Task management
- Chat with Reachy
- Real-time updates
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .routers import users, calendar, tasks, chat

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Reachy Home Assistant API",
    description="Backend API for the Reachy Home Assistant",
    version="0.1.0"
)

# CORS for local network access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup():
    """Initialize connections on startup."""
    logger.info("Starting Reachy API server...")
    # TODO: Initialize database connection
    # TODO: Initialize WebSocket manager


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    logger.info("Shutting down Reachy API server...")
    # TODO: Close connections


def main():
    """Entry point for running the API server."""
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=3000,
        reload=False
    )


if __name__ == "__main__":
    main()
