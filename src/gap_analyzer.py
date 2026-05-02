"""
gap_analyzer.py — Skill gap analysis and 30-day roadmap via OpenAI.

Builds a RAG prompt from the matched job's requirements + student skill list,
calls the OpenAI API, and parses the structured JSON response.

Key rules applied here:
- Prompt explicitly requests JSON output — prevents free-form markdown responses.
- Response is defensively parsed: markdown code fences stripped before json.loads().
- json.loads() is wrapped in try/except with a graceful fallback.
- Result is cached in a module-level dict to avoid repeat API calls.
- API key retrieved via get_secret().

Locked interface (do not change signature without team agreement):
    analyze_gaps(job: dict, student_skills: list[str]) -> dict
    Returns {missing_skills, week1, week2, week3, week4}
"""

import json
import re
from openai import OpenAI
from src.config import get_secret

_GAP_CACHE: dict[str, dict] = {}

MODEL = "gpt-4o-mini"

_PROMPT_TEMPLATE = """You are a career coach helping a student break into the Sydney tech job market.

The student has these skills:
{student_skills}

They are being matched to this role:
Job Title: {job_title}
Required Skills: {job_skills}
Full Job Description:
{job_description}

Identify the 2-3 most important skills the student is missing for this specific role.
Then write a practical 30-day learning plan to close those gaps, broken into four weekly focuses.

Respond ONLY with valid JSON in this exact format — no markdown, no explanation outside the JSON:
{{
  "missing_skills": ["skill1", "skill2", "skill3"],
  "week1": "Specific focus and concrete actions for Week 1",
  "week2": "Specific focus and concrete actions for Week 2",
  "week3": "Specific focus and concrete actions for Week 3",
  "week4": "Specific focus and concrete actions for Week 4"
}}"""


def _parse_response(text: str) -> dict:
    """
    Parse Claude's response into a structured dict.

    Claude sometimes wraps JSON in markdown code fences (```json ... ```).
    Strip them before parsing. If parsing still fails, return a fallback
    so the app doesn't crash — the raw text is preserved in week1.
    """
    # Strip markdown code fences: ```json ... ``` or ``` ... ```
    cleaned = re.sub(r"```(?:json)?", "", text).strip()
    cleaned = cleaned.rstrip("`").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "missing_skills": [],
            "week1": text,  # Preserve raw response so user sees something
            "week2": "",
            "week3": "",
            "week4": "",
        }


def analyze_gaps(job: dict, student_skills: list[str]) -> dict:
    """
    Call Claude Haiku to identify skill gaps and generate a 30-day learning plan.

    Args:
        job: Job dict from matcher.match_jobs() output.
             Must have keys: title, skills_required, raw_description.
        student_skills: List of canonical skill names from extractor.extract_skills().

    Returns:
        Dict with keys: {missing_skills, week1, week2, week3, week4}
    """
    cache_key = f"gap_analysis_{job.get('title', '')}"
    if cache_key in _GAP_CACHE:
        return _GAP_CACHE[cache_key]

    api_key = get_secret("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    student_skills_str = ", ".join(student_skills) if student_skills else "No skills detected"

    prompt = _PROMPT_TEMPLATE.format(
        student_skills=student_skills_str,
        job_title=job.get("title", "Unknown"),
        job_skills=job.get("skills_required", ""),
        job_description=job.get("raw_description", ""),
    )

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = response.choices[0].message.content
    result = _parse_response(raw_text)

    _GAP_CACHE[cache_key] = result
    return result