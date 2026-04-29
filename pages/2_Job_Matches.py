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

st.set_page_config(page_title="Job Matches — Career Compass", page_icon="🧭", layout="centered")

# ── Session State Guard ───────────────────────────────────────────────────────
# If the user navigates here directly or refreshes, session state is empty.
# Redirect them to page 1 rather than crashing with a KeyError.
if "extracted_skills" not in st.session_state or not st.session_state["extracted_skills"]:
    st.warning("Please complete Step 1 first.")
    st.switch_page("pages/1_Brain_Dump.py")
    st.stop()

st.title("🧭 Career Compass")
st.header("Step 2: Your Top Job Matches")

skills = st.session_state["extracted_skills"]
st.markdown(f"Matching your **{len(skills)} detected skills** against the Sydney job market...")

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
        colour = LABEL_COLOURS.get(label, "#6c757d")

        with st.container(border=True):
            col_title, col_badge = st.columns([4, 1])
            with col_title:
                st.subheader(f"#{i} — {job['title']}")
            with col_badge:
                st.markdown(
                    f'<div style="text-align:right;margin-top:8px;">'
                    f'<span style="background:{colour};color:white;border-radius:12px;'
                    f'padding:4px 10px;font-size:0.85em;font-weight:bold;">{label}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

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
                        f'<span style="background:transparent;border:1.5px solid white;color:white;border-radius:12px;padding:3px 8px;'
                        f'margin:2px;display:inline-block;font-size:0.85em;">{s.strip()}</span>'
                        for s in skills_required.split(",") if s.strip()
                    )
                    st.markdown(tag_html, unsafe_allow_html=True)
                else:
                    st.write("Not specified.")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", use_container_width=True):
            st.switch_page("pages/1_Brain_Dump.py")
    with col2:
        if st.button("Generate My Roadmap →", type="primary", use_container_width=True):
            st.switch_page("pages/3_My_Roadmap.py")