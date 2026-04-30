"""
app.py — Career Compass landing page and startup checks.

This is the entry point Streamlit loads first. It:
1. Checks for ANTHROPIC_API_KEY and stops with a clear error if missing.
2. Verifies ChromaDB has been ingested (helpful error if not).
3. Shows the landing page with hero section and smooth transitions.

Run with: streamlit run app.py
"""

import streamlit as st
import chromadb

from src.config import get_secret
from src.styles import inject_css

st.set_page_config(
    page_title="Career Compass",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()

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

# ── Hero Section ─────────────────────────────────────────────────────────────
hero_html = """
<div class="hero-section">
    <div class="scroll-indicator">⬇️</div>
</div>
"""
st.markdown(hero_html, unsafe_allow_html=True)

# ── Content Section with Smooth Transitions ──────────────────────────────────
content_html = """
<div class="landing-hero animated">
    <h1 class="landing-title">Career Compass</h1>
    <p class="landing-subtitle">Transform your experience into a job-ready roadmap</p>
</div>
"""
st.markdown(content_html, unsafe_allow_html=True)

st.markdown(
    """
    <div style="max-width: 800px; margin: 0 auto; padding: 0 20px;">
        <p style="text-align: center; color: var(--muted); font-family: 'Outfit', sans-serif; font-size: 1.05em; margin-bottom: 48px;">
            You have real skills hidden in your experience. Let's find them and match you with the roles you're made for.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Step cards
step_cards_html = """
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 24px; max-width: 900px; margin: 48px auto; padding: 0 20px;">
    <div class="step-card animated delay-1">
        <h3>1️⃣ Brain Dump</h3>
        <p>Share everything: your projects, experience, skills, interests. No need to be formal.</p>
    </div>
    <div class="step-card animated delay-2">
        <h3>2️⃣ Find Matches</h3>
        <p>AI extracts your skills and finds the Sydney jobs that align with your profile.</p>
    </div>
    <div class="step-card animated delay-3">
        <h3>3️⃣ Your Roadmap</h3>
        <p>Get a personalized 30-day plan to close skill gaps and land your next role.</p>
    </div>
</div>
"""
st.markdown(step_cards_html, unsafe_allow_html=True)

st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1.5, 1])
with col2:
    if st.button("Get Started →", type="primary", use_container_width=True):
        st.switch_page("pages/1_Brain_Dump.py")

st.markdown(f"""
    <p style="text-align: center; color: var(--muted); font-family: 'Outfit', sans-serif; font-size: 0.9em; margin-top: 32px;">
        Matching against {_job_count} Sydney job descriptions
    </p>
    """,
    unsafe_allow_html=True
)