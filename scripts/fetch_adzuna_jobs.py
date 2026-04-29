"""
fetch_adzuna_jobs.py — Fetch Sydney tech job listings from Adzuna API.

BEFORE RUNNING:
1. Go to: https://developer.adzuna.com/
2. Click "Register" and create a free account.
3. Create an app — you'll get an app_id and app_key.
4. Add both to your .env file:
       ADZUNA_APP_ID=your_app_id_here
       ADZUNA_APP_KEY=your_app_key_here

Run with:
    python scripts/fetch_adzuna_jobs.py

Output: data/job_descriptions.csv  (columns: id, title, company_type, seniority, location,
                                              skills_required, raw_description)

Notes:
- Free tier allows ~100 requests/day. This script makes ~10 requests (plenty).
- We fetch across multiple job categories to get diverse role types.
- skills_required is extracted via keyword matching against the description —
  no extra API calls needed.
"""

import os
import sys
import time
import re
import requests
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

OUTPUT_PATH = "data/job_descriptions.csv"
BASE_URL = "https://api.adzuna.com/v1/api/jobs/au/search"

# ── Credentials ───────────────────────────────────────────────────────────────
APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

# ── Search configuration ──────────────────────────────────────────────────────
# Each entry is (search_query, category_label, results_per_page)
# We target Sydney tech/data roles specifically.
SEARCHES = [
    ("data analyst",           "Data & Analytics",       20),
    ("data scientist",         "Data & Analytics",       20),
    ("data engineer",          "Data & Analytics",       15),
    ("business analyst",       "Business & Consulting",  15),
    ("software engineer",      "Software Engineering",   20),
    ("python developer",       "Software Engineering",   15),
    ("machine learning",       "Data & Analytics",       10),
    ("cloud engineer",         "Infrastructure & Cloud", 10),
    ("devops engineer",        "Infrastructure & Cloud", 10),
    ("frontend developer",     "Software Engineering",   10),
]

# ── Tech skill keywords for skills_required extraction ────────────────────────
# Checked against lowercased job description text.
SKILL_PATTERNS = [
    "python", "sql", "r ", "javascript", "typescript", "java", "scala",
    "c++", "c#", "golang", "ruby", "bash", "html", "css",
    "pandas", "numpy", "scikit-learn", "sklearn", "tensorflow", "pytorch", "keras",
    "spark", "pyspark", "hadoop", "kafka", "airflow", "dbt", "etl",
    "power bi", "tableau", "looker", "qlik", "excel",
    "aws", "azure", "gcp", "google cloud", "cloud",
    "docker", "kubernetes", "k8s", "terraform", "ansible",
    "git", "ci/cd", "devops", "linux",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "snowflake", "bigquery", "redshift", "databricks",
    "machine learning", "deep learning", "nlp", "computer vision",
    "api", "rest", "graphql", "microservices", "react", "node.js", "django", "flask",
    "fastapi", "spring boot",
    "agile", "scrum", "jira", "stakeholder management",
    "data visualisation", "data visualization", "data modelling", "data modeling",
    "statistics", "regression", "classification", "forecasting",
    "communication", "problem solving", "requirements gathering",
]

# ── Seniority detection ───────────────────────────────────────────────────────
SENIOR_PATTERNS = re.compile(
    r"\b(senior|sr\.?|lead|principal|staff|head of|director)\b", re.IGNORECASE
)
JUNIOR_PATTERNS = re.compile(
    r"\b(junior|jr\.?|graduate|grad|entry.?level|associate)\b", re.IGNORECASE
)


def check_credentials():
    if not APP_ID or not APP_KEY:
        print(
            "\nAdzuna credentials not found.\n\n"
            "Steps:\n"
            "  1. Register at https://developer.adzuna.com/\n"
            "  2. Create an app to get your app_id and app_key.\n"
            "  3. Add to your .env file:\n"
            "       ADZUNA_APP_ID=your_app_id_here\n"
            "       ADZUNA_APP_KEY=your_app_key_here\n"
        )
        sys.exit(1)


def extract_skills(description: str) -> str:
    """
    Extract skill keywords from a job description via simple pattern matching.
    Returns a comma-separated string of matched skills.
    """
    desc_lower = description.lower()
    found = []
    for skill in SKILL_PATTERNS:
        # Use word-boundary-aware matching for short patterns like "r " to avoid
        # matching "r" inside other words
        if skill.endswith(" "):
            if f" {skill.strip()} " in f" {desc_lower} " or f" {skill.strip()}," in desc_lower:
                found.append(skill.strip().title())
        elif re.search(r'\b' + re.escape(skill) + r'\b', desc_lower):
            found.append(skill.title())

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for s in found:
        if s.lower() not in seen:
            seen.add(s.lower())
            unique.append(s)

    return ", ".join(unique)


def detect_seniority(title: str, description: str) -> str:
    text = f"{title} {description}"
    if SENIOR_PATTERNS.search(text):
        return "Senior"
    elif JUNIOR_PATTERNS.search(text):
        return "Graduate / Junior"
    else:
        return "Mid-level"


def fetch_page(query: str, page: int = 1, results_per_page: int = 20) -> dict:
    """Fetch one page of results from the Adzuna API."""
    url = f"{BASE_URL}/{page}"
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "what": query,
        "where": "Sydney",
        "results_per_page": results_per_page,
    }
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def fetch_jobs() -> list[dict]:
    """
    Run all searches and collect deduplicated job listings.
    Returns list of raw Adzuna job dicts.
    """
    all_jobs = []
    seen_ids = set()

    for query, category, count in SEARCHES:
        print(f"  Fetching: '{query}' in Sydney (requesting {count})...")
        try:
            data = fetch_page(query, page=1, results_per_page=count)
            results = data.get("results", [])
            new = 0
            for job in results:
                job_id = str(job.get("id", ""))
                if job_id and job_id not in seen_ids:
                    job["_category_label"] = category
                    all_jobs.append(job)
                    seen_ids.add(job_id)
                    new += 1
            print(f"    Got {new} new jobs (total so far: {len(all_jobs)})")
        except requests.HTTPError as e:
            print(f"    HTTP error for '{query}': {e}")
        except Exception as e:
            print(f"    Error for '{query}': {e}")

        # Be polite — don't hammer the API
        time.sleep(0.5)

    return all_jobs


def transform(raw_jobs: list[dict]) -> pd.DataFrame:
    """Convert raw Adzuna job dicts into the project's CSV schema."""
    rows = []

    for job in raw_jobs:
        title = job.get("title", "").strip()
        description = job.get("description", "").strip()

        if not title or not description:
            continue

        skills = extract_skills(description)
        if not skills:
            # Skip jobs where we can't identify any skills — they're noise
            continue

        rows.append({
            "id": str(job.get("id", "")),
            "title": title,
            "company_type": job.get("_category_label", "Technology"),
            "seniority": detect_seniority(title, description),
            "location": "Sydney, NSW",
            "skills_required": skills,
            "raw_description": description[:2000],  # Cap at 2000 chars for ChromaDB metadata
        })

    df = pd.DataFrame(rows)
    print(f"\nTransformed {len(df)} jobs with extractable skills (from {len(raw_jobs)} fetched)")
    return df


def main():
    check_credentials()

    print(f"Fetching Sydney tech jobs from Adzuna...\n")
    raw_jobs = fetch_jobs()

    if not raw_jobs:
        print("\nNo jobs fetched. Check your credentials and internet connection.")
        sys.exit(1)

    df = transform(raw_jobs)

    if df.empty:
        print("\nNo jobs with extractable skills. Check the SKILL_PATTERNS list.")
        sys.exit(1)

    Path(OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    print(f"\nSaved {len(df)} jobs to {OUTPUT_PATH}")
    print("\nRole breakdown:")
    print(df["seniority"].value_counts().to_string())
    print("\nSample rows:")
    print(df[["title", "seniority", "skills_required"]].head(5).to_string(index=False))
    print(
        "\nNext step: run the ingestion script:\n"
        "    python scripts/ingest_jobs.py"
    )


if __name__ == "__main__":
    main()
