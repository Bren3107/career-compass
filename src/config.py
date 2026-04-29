"""
config.py — Secret and configuration helpers.

get_secret() retrieves values from environment variables (.env via python-dotenv).
"""

import os
from dotenv import load_dotenv

load_dotenv()


def get_secret(key: str) -> str:
    """Retrieve a secret by key from environment variables. Raises ValueError if not found."""
    value = os.getenv(key)
    if value:
        return value
    raise ValueError(f"Secret '{key}' not found in environment.")