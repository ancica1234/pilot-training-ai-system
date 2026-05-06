"""
tests/conftest.py
-----------------
Shared pytest fixtures and configuration.
"""

import os
import pytest

# Set a dummy API key so graph.py can be imported without a real key
os.environ.setdefault("GROQ_API_KEY", "dummy")
os.environ.setdefault("LANGSMITH_API_KEY", "")


@pytest.fixture(autouse=True)
def reset_notification_log():
    """Clear the notification log before each test to prevent state leakage."""
    from agents.instructor_notification import NOTIFICATION_LOG
    NOTIFICATION_LOG.clear()
    yield
    NOTIFICATION_LOG.clear()
