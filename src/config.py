"""
config.py — Secret and configuration helpers.

get_secret() tries st.secrets first (Streamlit Cloud), then falls back to
.env via python-dotenv (local dev). This means you never change code between
environments — just set the key in the right place.
"""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_secret(key: str) -> str:
    """
    Retrieve a secret by key. Checks st.secrets first, then os.environ.
    Raises ValueError if the key is not found in either place.
    """
    try:
        value = st.secrets[key]
        if value:
            return value
    except Exception:
        pass

    value = os.getenv(key)
    if value:
        return value

    raise ValueError(
        f"Secret '{key}' not found. "
        "Add it to your .env file (local) or Streamlit Secrets (cloud)."
    )