"""Tests configuration and fixtures."""

import pytest
import asyncio
from typing import AsyncGenerator

from hope.config import Settings


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings with mock values."""
    import os
    
    # Set minimal required environment variables for testing
    os.environ.setdefault("HOPE_DB_PASSWORD", "test_password")
    os.environ.setdefault("HOPE_JWT_SECRET_KEY", "test_secret_key_for_jwt_signing_min_32_chars")
    os.environ.setdefault("HOPE_ENCRYPTION_KEY", "dGVzdF9lbmNyeXB0aW9uX2tleV8zMl9ieXRlcw==")
    
    return Settings(
        env="development",
        debug=True,
    )
