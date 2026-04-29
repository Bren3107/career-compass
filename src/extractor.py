"""
extractor.py — Skill extraction from raw text.

Uses spaCy PhraseMatcher (attr="LOWER") against the skills taxonomy CSV.
DO NOT use spaCy's built-in NER — it will silently find zero tech skills.
PhraseMatcher matches taxonomy terms and aliases directly against tokenised text.

Locked interface (do not change signature without team agreement):
    extract_skills(text: str) -> list[str]
    Returns canonical skill names, deduplicated, lowercased.
"""

import streamlit as st
import pandas as pd
import spacy
from spacy.matcher import PhraseMatcher

DATA_PATH = "data/skills_taxonomy.csv"

# ── Tech skills supplement ────────────────────────────────────────────────────
# The ESCO taxonomy uses formal names like "Python (computer programming)" and
# omits many common tools entirely (Power BI, Azure, pandas, etc.).
# This supplement maps canonical names → list of surface forms to match.
TECH_SUPPLEMENT: dict[str, list[str]] = {
    "python": ["python"],
    "sql": ["sql"],
    "r": ["r programming", "r language"],
    "power bi": ["power bi", "powerbi"],
    "tableau": ["tableau"],
    "excel": ["excel", "microsoft excel", "ms excel"],
    "ssrs": ["ssrs", "sql server reporting services"],
    "ssis": ["ssis", "sql server integration services"],
    "azure": ["azure", "microsoft azure", "azure cloud"],
    "aws": ["aws", "amazon web services"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "git": ["git", "github", "gitlab"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "terraform": ["terraform"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch"],
    "keras": ["keras"],
    "spark": ["apache spark", "pyspark", "spark"],
    "kafka": ["apache kafka", "kafka"],
    "airflow": ["apache airflow", "airflow"],
    "dbt": ["dbt", "data build tool"],
    "snowflake": ["snowflake"],
    "databricks": ["databricks"],
    "bigquery": ["bigquery", "google bigquery"],
    "redshift": ["redshift", "amazon redshift"],
    "mongodb": ["mongodb"],
    "postgresql": ["postgresql", "postgres"],
    "mysql": ["mysql"],
    "redis": ["redis"],
    "elasticsearch": ["elasticsearch"],
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning"],
    "nlp": ["nlp", "natural language processing"],
    "computer vision": ["computer vision"],
    "react": ["react", "react.js", "reactjs"],
    "javascript": ["javascript", "js"],
    "typescript": ["typescript"],
    "node.js": ["node.js", "nodejs", "node"],
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi"],
    "java": ["java"],
    "scala": ["scala"],
    "c#": ["c#", "c sharp"],
    "c++": ["c++"],
    "golang": ["golang", "go language"],
    "ruby": ["ruby", "ruby on rails"],
    "rest api": ["rest api", "restful api", "rest"],
    "graphql": ["graphql"],
    "microservices": ["microservices"],
    "devops": ["devops"],
    "ci/cd": ["ci/cd", "cicd", "continuous integration"],
    "linux": ["linux", "unix"],
    "looker": ["looker"],
    "qlik": ["qlik", "qlikview", "qliksense"],
    "jira": ["jira"],
    "agile": ["agile", "agile methodology"],
    "scrum": ["scrum"],
    "data modelling": ["data modelling", "data modeling"],
    "data visualisation": ["data visualisation", "data visualization"],
    "statistics": ["statistics", "statistical analysis"],
    "forecasting": ["forecasting"],
    "regression": ["regression analysis", "regression"],
    "etl": ["etl", "extract transform load"],
    "hadoop": ["hadoop"],
    "requirements gathering": ["requirements gathering", "requirements elicitation"],
    "stakeholder management": ["stakeholder management", "stakeholder communication"],
}


@st.cache_resource
def _load_matcher():
    """
    Load spaCy model and build PhraseMatcher from skills taxonomy.
    Cached with @st.cache_resource — one instance shared across all sessions.
    Do NOT use @st.cache_data here (will fail with pickle error on model objects).
    """
    nlp = spacy.load("en_core_web_sm")
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

    df = pd.read_csv(DATA_PATH, encoding="utf-8")

    # Build a mapping: lowercased term -> canonical skill name
    term_to_canonical: dict[str, str] = {}

    for _, row in df.iterrows():
        canonical = str(row["skill_name"]).strip()
        terms = [canonical]

        # Explode aliases — stored as comma-separated string in the CSV
        aliases_raw = str(row.get("aliases", "")).strip()
        if aliases_raw and aliases_raw.lower() != "nan":
            terms += [a.strip() for a in aliases_raw.split(",") if a.strip()]

        for term in terms:
            term_to_canonical[term.lower()] = canonical.lower()

    # Merge tech supplement into the term mapping (supplement takes priority
    # so that bare "python" maps to "python" not "python (computer programming)")
    for canonical, surface_forms in TECH_SUPPLEMENT.items():
        for form in surface_forms:
            term_to_canonical[form.lower()] = canonical

    # Add all unique terms as PhraseMatcher patterns
    all_terms = list(term_to_canonical.keys())
    patterns = [nlp.make_doc(term) for term in all_terms]
    matcher.add("SKILLS", patterns)

    return nlp, matcher, term_to_canonical


def extract_skills(text: str) -> list[str]:
    """
    Extract canonical skills from raw text using PhraseMatcher.

    Args:
        text: Raw brain dump or any unstructured experience text.

    Returns:
        Deduplicated list of canonical skill names (lowercased).
        Example: ["python", "sql", "power bi", "dbt"]
    """
    if not text or not text.strip():
        return []

    nlp, matcher, term_to_canonical = _load_matcher()

    doc = nlp(text)
    matches = matcher(doc)

    found: set[str] = set()
    for _match_id, start, end in matches:
        matched_text = doc[start:end].text.lower()
        # Map the matched text back to its canonical name
        canonical = term_to_canonical.get(matched_text, matched_text)
        found.add(canonical)

    return sorted(found)