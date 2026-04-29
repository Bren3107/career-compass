"""
app.py — Career Compass landing page and startup checks.

This is the entry point Streamlit loads first. It:
1. Checks for ANTHROPIC_API_KEY and stops with a clear error if missing.
2. Verifies ChromaDB has been ingested (helpful error if not).
3. Shows the landing page with navigation to the brain dump input.

Run with: streamlit run app.py
"""

import streamlit as st
import chromadb

from src.config import get_secret

st.set_page_config(
    page_title="Career Compass",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── API Key Check ────────────────────────────────────────────────────────────
# Must happen before any NLP calls. If the key is missing, stop immediately
# with an actionable error — the default anthropic error is hard to diagnose.
try:
    _api_key = get_secret("ANTHROPIC_API_KEY")
except ValueError:
    st.error(
        "**ANTHROPIC_API_KEY not found.**\n\n"
        "- Local: copy `.env.example` to `.env` and add your key.\n"
        "- Streamlit Cloud: add it via Settings > Secrets."
    )
    st.stop()

# ── ChromaDB Check ───────────────────────────────────────────────────────────
# Give a clear error if the user forgot to run ingest_jobs.py.
try:
    _client = chromadb.PersistentClient(path="data/chroma_db")
    _collection = _client.get_collection("jobs")
    _job_count = _collection.count()
    if _job_count == 0:
        raise ValueError("Empty collection")
except Exception:
    st.error(
        "**Job database not found or empty.**\n\n"
        "Run the ingestion script first:\n"
        "```\npython scripts/ingest_jobs.py\n```\n\n"
        "Make sure `data/job_descriptions.csv` exists before running."
    )
    st.stop()

# ── Landing Page ─────────────────────────────────────────────────────────────
st.title("🧭 Career Compass")
st.subheader("Turn your experience into a job-ready roadmap")

st.markdown(
    """
    **You have real skills. Let's find them — and the jobs that match.**

    Career Compass takes your unstructured life experience (a "brain dump"),
    extracts the skills hidden inside it, and matches you against real Sydney
    job descriptions. You'll see exactly which skills you're missing and get
    a personalised 30-day plan to close the gap.

    ---
    ### How it works
    1. **Paste your experience** — anything: projects, uni work, jobs, hobbies
    2. **See your top job matches** — with similarity scores and required skills
    3. **Get your roadmap** — a week-by-week plan to land that role

    ---
    """
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Get Started →", type="primary", use_container_width=True):
        st.switch_page("pages/1_Brain_Dump.py")

st.caption(f"Matching against {_job_count} Sydney job descriptions.")