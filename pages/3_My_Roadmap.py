"""
pages/3_My_Roadmap.py — Step 3: Skill gap analysis and 30-day learning roadmap.

Key rules applied:
- Session state guard: redirects to page 2 if top_matches is absent.
- API call (analyze_gaps) is inside st.button() callback and wrapped in st.spinner().
  The gap_analyzer itself also caches in session_state — repeated page visits
  don't trigger another API call.
- Gap result is stored in session_state["gap_analysis"] for display persistence.
- Missing skills displayed as coloured tags.
- 30-day plan displayed week by week in expandable sections.
"""

import streamlit as st
from src.gap_analyzer import analyze_gaps

st.set_page_config(page_title="My Roadmap — Career Compass", page_icon="🧭", layout="centered")

# ── Session State Guard ───────────────────────────────────────────────────────
if "top_matches" not in st.session_state or not st.session_state["top_matches"]:
    st.warning("Please complete Step 2 first.")
    st.switch_page("pages/2_Job_Matches.py")
    st.stop()

st.title("🧭 Career Compass")
st.header("Step 3: Your Personalised Roadmap")

top_job = st.session_state["top_matches"][0]
student_skills = st.session_state.get("extracted_skills", [])

st.markdown(
    f"Analysing your skill gaps for **{top_job['title']}** "
    f"({top_job['label']} — {int(top_job['score'] * 100)}% match)"
)

# ── Gap Analysis ──────────────────────────────────────────────────────────────
cache_key = f"gap_analysis_{top_job.get('title', '')}"

if cache_key not in st.session_state:
    if st.button("Generate My Roadmap", type="primary"):
        with st.spinner("Generating your personalised roadmap... (this takes 5–10 seconds)"):
            result = analyze_gaps(top_job, student_skills)
            st.session_state["gap_analysis"] = result
        st.rerun()
else:
    result = st.session_state[cache_key]
    st.session_state["gap_analysis"] = result

    # ── Missing Skills ────────────────────────────────────────────────────────
    st.divider()
    st.subheader("Skills to develop")

    missing = result.get("missing_skills", [])
    if missing:
        tag_html = " ".join(
            f'<span style="background:transparent;border:1.5px solid white;color:white;border-radius:12px;padding:5px 12px;'
            f'margin:3px;display:inline-block;font-size:0.95em;font-weight:500;">'
            f'{skill}</span>'
            for skill in missing
        )
        st.markdown(tag_html, unsafe_allow_html=True)
    else:
        st.info("No specific skill gaps identified — you may already be a strong match!")

    # ── 30-Day Plan ───────────────────────────────────────────────────────────
    st.divider()
    st.subheader("Your 30-Day Learning Plan")

    weeks = [
        ("Week 1", result.get("week1", "")),
        ("Week 2", result.get("week2", "")),
        ("Week 3", result.get("week3", "")),
        ("Week 4", result.get("week4", "")),
    ]

    for week_label, content in weeks:
        if content and content.strip():
            with st.expander(week_label, expanded=True):
                st.write(content)

    # ── Export ────────────────────────────────────────────────────────────────
    st.divider()

    plan_text = f"Career Compass — 30-Day Roadmap\n"
    plan_text += f"Target Role: {top_job['title']}\n"
    plan_text += f"Match Score: {int(top_job['score'] * 100)}% ({top_job['label']})\n\n"
    plan_text += f"Skills to Develop:\n"
    plan_text += "\n".join(f"  - {s}" for s in missing) + "\n\n"
    for week_label, content in weeks:
        if content:
            plan_text += f"{week_label}:\n{content}\n\n"

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Matches", use_container_width=True):
            st.switch_page("pages/2_Job_Matches.py")
    with col2:
        st.download_button(
            label="Download Plan",
            data=plan_text,
            file_name="career-compass-roadmap.txt",
            mime="text/plain",
            use_container_width=True,
        )

    # ── Start Over ────────────────────────────────────────────────────────────
    st.divider()
    if st.button("Start Over", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("pages/1_Brain_Dump.py")