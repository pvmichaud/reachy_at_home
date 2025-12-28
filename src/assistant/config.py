"""
Configuration management for the assistant service.

Loads settings from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # Database
    database_url: str = "postgresql://reachy:password@localhost:5432/reachy_db"

    # Claude API
    anthropic_api_key: Optional[str] = None
    claude_model: str = "claude-sonnet-4-20250514"

    # Cozi
    cozi_email: Optional[str] = None
    cozi_password: Optional[str] = None

    # Reachy
    reachy_host: str = "localhost"
    reachy_port: int = 8000

    # Application behavior
    log_level: str = "INFO"
    quiet_hours_start: str = "05:00"
    quiet_hours_end: str = "07:00"

    # Recognition
    face_recognition_threshold: float = 0.6
    voice_recognition_threshold: float = 0.7

    # Wake word
    wake_word: str = "hey_reachy"
    wake_word_threshold: float = 0.5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
