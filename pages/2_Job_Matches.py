"""
pages/2_Job_Matches.py — Step 2: View top job matches and similarity scores.

Key rules applied:
- Session state guard at the top: if extracted_skills is missing, redirect to
  page 1 with st.switch_page(). This handles direct navigation and page refresh.
- Matching pipeline (embed + match_jobs) is inside st.button() callback.
- Scores are displayed as similarity (0–1), already converted from distance
  in matcher.py (1 - distance). Labels: Strong / Moderate / Weak.
- top_matches stored in session_state for page 3 to consume.
"""

import streamlit as st
from src.embedder import embed
from src.matcher import match_jobs
from src.styles import inject_css

st.set_page_config(page_title="Job Matches — Career Compass", page_icon="🧭", layout="wide")

inject_css()

# ── Session State Guard ───────────────────────────────────────────────────────
# If the user navigates here directly or refreshes, session state is empty.
# Redirect them to page 1 rather than crashing with a KeyError.
if "extracted_skills" not in st.session_state or not st.session_state["extracted_skills"]:
    st.warning("Please complete Step 1 first.")
    st.switch_page("pages/1_Brain_Dump.py")
    st.stop()

# Step indicator
step_indicator = """
<div class="step-indicator">
    <div class="step-dot"></div>
    <div class="step-dot active"></div>
    <div class="step-dot"></div>
</div>
"""
st.markdown(step_indicator, unsafe_allow_html=True)

# Page title
title_html = """
<div class="animated">
    <h1 class="page-title">Your Top Job Matches</h1>
    <p class="page-subtitle">Roles that align with your skills and experience</p>
</div>
"""
st.markdown(title_html, unsafe_allow_html=True)

skills = st.session_state["extracted_skills"]
st.markdown(f"<p style='text-align: center; color: var(--muted);'>Matching your <strong>{len(skills)} detected skills</strong> against the Sydney job market...</p>", unsafe_allow_html=True)

# ── Job Matching ──────────────────────────────────────────────────────────────
# Run matching when button is clicked, or if we already have results cached.
if "top_matches" not in st.session_state:
    if st.button("Find My Matches", type="primary"):
        with st.spinner("Searching for your best job matches..."):
            skills_text = ", ".join(skills)
            vector = embed(skills_text)
            st.session_state["user_vector"] = vector
            matches = match_jobs(vector, top_k=6)
            st.session_state["top_matches"] = matches
        st.rerun()
else:
    # ── Results Display ───────────────────────────────────────────────────────
    matches = st.session_state["top_matches"]

    LABEL_COLOURS = {
        "Strong match": "#28a745",
        "Moderate match": "#fd7e14",
        "Weak match": "#dc3545",
    }

    for i, job in enumerate(matches, start=1):
        score_pct = int(job["score"] * 100)
        label = job["label"]

        # Determine badge class
        if score_pct >= 60:
            badge_class = "match-badge strong"
        elif score_pct >= 40:
            badge_class = "match-badge moderate"
        else:
            badge_class = "match-badge weak"

        # Custom card with hover effect
        card_html = f"""
        <div class="compass-card animated delay-{min(i, 5)}">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                <div style="flex: 1;">
                    <h3 style="margin: 0 0 4px 0; font-family: 'Outfit', sans-serif; color: var(--text); font-size: 1.2em;">#{i} — {job['title']}</h3>
                </div>
                <span class="{badge_class}" style="white-space: nowrap; margin-left: 12px;">{label}</span>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

        st.progress(job["score"], text=f"{score_pct}% similarity")

        meta_parts = []
        if job.get("seniority"):
            meta_parts.append(job["seniority"])
        if job.get("company_type"):
            meta_parts.append(job["company_type"])
        if job.get("location"):
            meta_parts.append(job["location"])
        if meta_parts:
            st.caption(" · ".join(meta_parts))

        with st.expander("Required skills"):
            skills_required = job.get("skills_required", "")
            if skills_required:
                tag_html = " ".join(
                    f'<span class="skill-badge">{s.strip()}</span>'
                    for s in skills_required.split(",") if s.strip()
                )
                st.markdown(tag_html, unsafe_allow_html=True)
            else:
                st.write("Not specified.")

        st.markdown("", unsafe_allow_html=True)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", use_container_width=True):
            st.switch_page("pages/1_Brain_Dump.py")
    with col2:
        if st.button("Generate My Roadmap →", type="primary", use_container_width=True):
            st.switch_page("pages/3_My_Roadmap.py")