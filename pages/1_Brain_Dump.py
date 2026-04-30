"""
pages/1_Brain_Dump.py — Step 1: Paste your experience and extract skills.

Key rules applied:
- NLP pipeline call (extract_skills) is inside the st.button() callback.
  It does NOT run at the top level — Streamlit re-runs the whole script on
  every user interaction, so top-level NLP calls would fire on every keystroke.
- Extracted skills and brain dump text are stored in st.session_state so
  subsequent pages can read them without re-running extraction.
- Minimum word count validation (>30 words) prevents garbage extraction.
"""

import streamlit as st
from src.extractor import extract_skills
from src.styles import inject_css

st.set_page_config(page_title="Brain Dump — Career Compass", page_icon="🧭", layout="wide")

inject_css()

# Step indicator
step_indicator = """
<div class="step-indicator">
    <div class="step-dot active"></div>
    <div class="step-dot"></div>
    <div class="step-dot"></div>
</div>
"""
st.markdown(step_indicator, unsafe_allow_html=True)

# Page title
title_html = """
<div class="animated">
    <h1 class="page-title">Tell us about yourself</h1>
    <p class="page-subtitle">Paste anything — projects, experience, internships, side work. The more detail, the better.</p>
</div>
"""
st.markdown(title_html, unsafe_allow_html=True)

SAMPLE_BRAIN_DUMP = (
    "I studied Information Systems at UTS and did a data analysis project where I used SQL to query "
    "a large database and built reports in SSRS and Power BI. I've also done some Python scripting for "
    "data cleaning with pandas. During my internship at a financial services company I worked with Excel "
    "and learned about business requirements gathering and stakeholder communication. I'm interested in "
    "machine learning and have done the fast.ai course on my own. I've used Azure basics and know how "
    "Git works from my group projects. I'm comfortable with presenting findings to non-technical audiences."
)

brain_dump = st.text_area(
    label="Your experience",
    placeholder=SAMPLE_BRAIN_DUMP,
    height=280,
    help="Aim for at least 50 words. The more detail you include, the more skills we can find.",
    value=st.session_state.get("brain_dump", ""),
)

col1, col2 = st.columns([3, 1])

with col1:
    extract_button = st.button("Extract My Skills", type="primary", use_container_width=True)

with col2:
    if st.button("Use Sample", use_container_width=True):
        st.session_state["brain_dump"] = SAMPLE_BRAIN_DUMP
        st.rerun()

# ── Skill Extraction ─────────────────────────────────────────────────────────
# All NLP work is inside this button block — not at the top level of the script.
if extract_button:
    if not brain_dump or not brain_dump.strip():
        st.warning("Please paste some experience text before extracting skills.")
    elif len(brain_dump.split()) < 30:
        st.warning(
            f"Your text is only {len(brain_dump.split())} words. "
            "Add more detail for better skill extraction (aim for 50+ words)."
        )
    else:
        with st.spinner("Extracting skills from your experience..."):
            skills = extract_skills(brain_dump)

        st.session_state["brain_dump"] = brain_dump
        st.session_state["extracted_skills"] = skills

        # Clear downstream state so stale matches/analysis don't carry over
        st.session_state.pop("top_matches", None)
        st.session_state.pop("user_vector", None)
        for key in list(st.session_state.keys()):
            if key.startswith("gap_analysis_"):
                del st.session_state[key]

# ── Display Results ───────────────────────────────────────────────────────────
if st.session_state.get("extracted_skills") is not None:
    skills = st.session_state["extracted_skills"]

    st.divider()
    st.subheader(f"Skills detected ({len(skills)})")

    if not skills:
        st.warning(
            "No skills were detected. Try adding more specific tool names or technologies "
            "(e.g. 'Python', 'SQL', 'Power BI', 'dbt', 'Azure')."
        )
    else:
        # Display skills as styled badges
        tag_html = " ".join(
            f'<span class="skill-badge">{s}</span>'
            for s in sorted(skills)
        )
        st.markdown(tag_html, unsafe_allow_html=True)

        st.markdown("")
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            if st.button("Find My Job Matches →", type="primary", use_container_width=True):
                st.switch_page("pages/2_Job_Matches.py")