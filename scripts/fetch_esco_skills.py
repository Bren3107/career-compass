"""
fetch_esco_skills.py — Build skills_taxonomy.csv from the ESCO public REST API.

No registration or download required. Queries the public ESCO API at ec.europa.eu.

Run with:
    python scripts/fetch_esco_skills.py

Output: data/skills_taxonomy.csv  (columns: skill_name, aliases)

Strategy:
  1. Search the ESCO API using a list of tech-relevant query terms.
  2. Collect unique skill URIs from search results.
  3. Fetch the full resource record for each URI to get alternativeLabels.
  4. Write out as skill_name, aliases CSV.

Rate limiting: 0.3s delay between requests — the ESCO API is a public EU service,
be polite. A full run takes ~3-5 minutes for ~300-400 skills.
"""

import time
import sys
import requests
import pandas as pd
from pathlib import Path

OUTPUT_PATH = "data/skills_taxonomy.csv"
BASE_URL = "https://ec.europa.eu/esco/api"
DELAY = 0.3  # seconds between API calls

# ── Search queries ────────────────────────────────────────────────────────────
# We run these searches and union all unique skill URIs returned.
# Broad terms first (capture whole subtrees), then specifics for common tools
# that may sit in non-obvious ESCO categories.
SEARCH_QUERIES = [
    # Languages
    "python", "sql", "java", "javascript", "typescript", "scala", "r programming",
    "c++", "c#", "golang", "ruby", "bash", "php", "kotlin", "swift",
    # Data & ML
    "machine learning", "deep learning", "neural network", "natural language processing",
    "data analysis", "data science", "data engineering", "data visualisation",
    "statistics", "statistical analysis", "regression", "classification",
    "pandas", "numpy", "scikit", "tensorflow", "pytorch", "keras",
    "computer vision", "predictive modelling",
    # Big data & pipelines
    "apache spark", "apache kafka", "apache airflow", "hadoop", "etl",
    "data pipeline", "data warehouse", "data lake", "dbt",
    # BI & reporting
    "power bi", "tableau", "looker", "qlik", "business intelligence",
    "data reporting", "dashboard",
    # Databases
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "snowflake", "bigquery", "redshift", "databricks", "oracle database",
    # Cloud & infrastructure
    "amazon web services", "microsoft azure", "google cloud",
    "cloud computing", "docker", "kubernetes", "terraform", "ansible",
    "devops", "continuous integration", "linux",
    # Web & software engineering
    "rest api", "graphql", "microservices", "react", "node.js",
    "django", "flask", "fastapi", "spring boot", "software development",
    "agile", "scrum",
    # Soft/business skills relevant to tech
    "stakeholder management", "requirements analysis", "project management",
    "communication", "problem solving", "data governance",
    # Generic tech umbrella terms (capture remaining ESCO subtrees)
    "programming", "software", "database", "network", "cybersecurity",
    "information technology", "digital", "automation",
]


def search_skills(query: str, limit: int = 50) -> list[dict]:
    """
    Search ESCO for skills matching a query string.
    Returns list of result dicts from the _embedded results.
    """
    url = f"{BASE_URL}/search"
    params = {
        "language": "en",
        "type": "skill",
        "text": query,
        "limit": limit,
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        embedded = data.get("_embedded", {})
        # Results can be under "results" or "skillCompetenceList"
        results = embedded.get("results", embedded.get("skillCompetenceList", []))
        return results
    except Exception as e:
        print(f"    Search error for '{query}': {e}")
        return []


def fetch_skill_detail(uri: str) -> dict | None:
    """
    Fetch the full resource record for a skill URI to get alternativeLabels.
    """
    url = f"{BASE_URL}/resource/skill"
    params = {"uri": uri, "language": "en"}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"    Detail error for URI {uri}: {e}")
        return None


def extract_aliases(detail: dict) -> str:
    """
    Extract English alternative labels from a full skill detail record.
    Returns a comma-separated string of aliases.
    """
    alt = detail.get("alternativeLabel", {})

    # alternativeLabel is a dict keyed by language code
    if isinstance(alt, dict):
        en_labels = alt.get("en", [])
    elif isinstance(alt, list):
        en_labels = alt
    else:
        en_labels = []

    return ", ".join(str(label).strip() for label in en_labels if str(label).strip())


def main():
    print("Fetching ESCO skills via public API...\n")

    # ── Phase 1: Collect unique URIs via search ───────────────────────────────
    uri_to_label: dict[str, str] = {}

    for i, query in enumerate(SEARCH_QUERIES, start=1):
        print(f"[{i}/{len(SEARCH_QUERIES)}] Searching: '{query}'")
        results = search_skills(query)
        new = 0
        for result in results:
            uri = result.get("uri", "")
            preferred = result.get("preferredLabel", "")
            # preferredLabel is a plain string in search results (not a dict)
            if isinstance(preferred, dict):
                preferred = preferred.get("en", "")
            label = preferred or result.get("title", "") or result.get("searchHit", "")
            if uri and label and uri not in uri_to_label:
                uri_to_label[uri] = label.strip()
                new += 1
        print(f"    +{new} new skills (total unique: {len(uri_to_label)})")
        time.sleep(DELAY)

    print(f"\nPhase 1 complete. {len(uri_to_label)} unique skill URIs collected.")

    if not uri_to_label:
        print("No skills found. Check your internet connection and try again.")
        sys.exit(1)

    # ── Phase 2: Fetch full details for aliases ───────────────────────────────
    print("\nFetching alternative labels for each skill...\n")
    rows = []
    uris = list(uri_to_label.items())

    for i, (uri, preferred_label) in enumerate(uris, start=1):
        if i % 25 == 0 or i == 1:
            print(f"  [{i}/{len(uris)}] Fetching details...")

        detail = fetch_skill_detail(uri)
        if detail:
            aliases = extract_aliases(detail)
        else:
            aliases = ""

        rows.append({
            "skill_name": preferred_label,
            "aliases": aliases,
        })
        time.sleep(DELAY)

    # ── Phase 3: Write CSV ────────────────────────────────────────────────────
    df = pd.DataFrame(rows).drop_duplicates(subset="skill_name")
    df = df.sort_values("skill_name")

    Path(OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    print(f"\nDone. {len(df)} skills saved to {OUTPUT_PATH}")
    print("\nSample output:")
    print(df.head(10).to_string(index=False))
    print(
        "\nNext step: run the skill extraction test or proceed to fetch jobs:\n"
        "    python scripts/fetch_adzuna_jobs.py"
    )


if __name__ == "__main__":
    main()
