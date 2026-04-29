"""
process_esco_skills.py — Convert ESCO skills download into skills_taxonomy.csv.

BEFORE RUNNING:
1. Go to: https://esco.ec.europa.eu/en/use-esco/download
2. Under "ESCO dataset", select Version 1.1.0 (or latest), language English.
3. Download the ZIP and extract it. Find the file called: skills_en.csv
4. Place skills_en.csv in the data/ folder (or pass its path as an argument).

Run with:
    python scripts/process_esco_skills.py
    python scripts/process_esco_skills.py --input path/to/skills_en.csv

Output: data/skills_taxonomy.csv  (columns: skill_name, aliases)
"""

import argparse
import pandas as pd
from pathlib import Path

DEFAULT_INPUT = "data/skills_en.csv"
OUTPUT_PATH = "data/skills_taxonomy.csv"

# ── Tech/digital skill keywords ───────────────────────────────────────────────
# ESCO skills are tagged with a conceptType and broaderConceptUri hierarchy.
# We filter by keyword presence in the preferredLabel since it's the most
# reliable signal — ESCO's hierarchy URIs change between versions.
#
# This list is tuned for Sydney tech/data/analytics job market.
TECH_KEYWORDS = [
    # Languages
    "python", "sql", "r programming", "javascript", "typescript", "java", "scala",
    "c++", "c#", "go ", " rust", "ruby", "php", "kotlin", "swift", "bash", "shell",
    "html", "css",
    # Data & analytics
    "data", "analytics", "analysis", "statistical", "machine learning",
    "deep learning", "neural network", "natural language processing", "nlp",
    "computer vision", "etl", "pipeline", "warehouse", "database",
    "tableau", "power bi", "looker", "qlik", "excel", "spreadsheet",
    "pandas", "numpy", "scikit", "tensorflow", "pytorch", "keras",
    "spark", "hadoop", "hive", "kafka", "airflow", "dbt", "dax",
    # Cloud & infrastructure
    "aws", "azure", "google cloud", "gcp", "cloud", "docker", "kubernetes",
    "terraform", "ansible", "devops", "ci/cd", "git", "linux", "unix",
    # Databases
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "snowflake",
    "bigquery", "redshift", "oracle", "sql server",
    # Web & software
    "api", "rest", "graphql", "microservice", "react", "angular", "vue",
    "node", "django", "flask", "fastapi", "spring",
    # Business & soft skills relevant to tech roles
    "agile", "scrum", "stakeholder", "requirements", "documentation",
    "communication", "presentation", "problem solving",
]


def load_esco(path: str) -> pd.DataFrame:
    """Load and validate the ESCO skills CSV."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"\nskills_en.csv not found at: {path}\n\n"
            "Download steps:\n"
            "  1. Go to https://esco.ec.europa.eu/en/use-esco/download\n"
            "  2. Download the ESCO dataset ZIP (English, latest version)\n"
            "  3. Extract and place skills_en.csv in data/\n"
        )

    df = pd.read_csv(path, low_memory=False)
    print(f"Loaded {len(df):,} rows from {path}")

    # Check expected columns exist
    required = {"preferredLabel", "altLabels"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Expected columns not found: {missing}\n"
            f"Available columns: {list(df.columns)[:10]}"
        )

    return df


def is_tech_skill(label: str) -> bool:
    """Return True if the skill label contains any tech keyword."""
    label_lower = label.lower()
    return any(kw in label_lower for kw in TECH_KEYWORDS)


def process(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to tech skills and reshape into skill_name / aliases format."""

    # Keep only rows where preferredLabel matches tech keywords
    mask = df["preferredLabel"].fillna("").apply(is_tech_skill)
    tech_df = df[mask].copy()
    print(f"Tech-relevant skills after filtering: {len(tech_df):,}")

    rows = []
    for _, row in tech_df.iterrows():
        skill_name = str(row["preferredLabel"]).strip()

        # altLabels is a pipe-separated string in ESCO: "alias1|alias2|alias3"
        alt_raw = str(row.get("altLabels", "")).strip()
        if alt_raw and alt_raw.lower() not in ("nan", ""):
            aliases = ", ".join(
                a.strip() for a in alt_raw.split("|") if a.strip()
            )
        else:
            aliases = ""

        rows.append({
            "skill_name": skill_name,
            "aliases": aliases,
        })

    result = pd.DataFrame(rows).drop_duplicates(subset="skill_name")

    # Also add common abbreviations / short-forms that ESCO sometimes misses
    extras = [
        ("Python", "python3, py"),
        ("SQL", "structured query language, mysql, postgresql, tsql, t-sql"),
        ("Power BI", "powerbi, power-bi, pbi"),
        ("dbt", "data build tool"),
        ("Git", "github, gitlab, version control"),
        ("Docker", "containerisation, containerization, containers"),
        ("Kubernetes", "k8s, container orchestration"),
        ("AWS", "amazon web services, amazon aws"),
        ("Azure", "microsoft azure, azure cloud"),
        ("GCP", "google cloud platform, google cloud"),
        ("Tableau", "tableau desktop, tableau server"),
        ("Spark", "apache spark, pyspark"),
        ("Airflow", "apache airflow"),
        ("Snowflake", "snowflake data warehouse"),
        ("BigQuery", "google bigquery, bq"),
        ("Pandas", "pandas dataframe"),
        ("scikit-learn", "sklearn, scikit learn"),
        ("TensorFlow", "tensorflow 2, tf"),
        ("PyTorch", "torch"),
        ("FastAPI", "fast api"),
        ("React", "reactjs, react.js"),
        ("Node.js", "nodejs, node"),
        ("MongoDB", "mongo"),
        ("Redis", "redis cache"),
        ("Elasticsearch", "elastic search, opensearch"),
    ]

    extra_df = pd.DataFrame(extras, columns=["skill_name", "aliases"])

    # Only add extras not already in the ESCO-derived set
    existing = set(result["skill_name"].str.lower())
    new_extras = extra_df[~extra_df["skill_name"].str.lower().isin(existing)]

    result = pd.concat([result, new_extras], ignore_index=True)
    print(f"Final taxonomy size (after adding extras): {len(result):,} skills")

    return result


def main():
    parser = argparse.ArgumentParser(description="Process ESCO skills into skills_taxonomy.csv")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="Path to skills_en.csv")
    parser.add_argument("--output", default=OUTPUT_PATH, help="Output CSV path")
    args = parser.parse_args()

    df = load_esco(args.input)
    result = process(df)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False, encoding="utf-8")
    print(f"\nSaved to {args.output}")
    print("Sample rows:")
    print(result.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
