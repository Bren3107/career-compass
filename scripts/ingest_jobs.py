"""
ingest_jobs.py — One-time script to embed all jobs and persist them to ChromaDB.

Run this locally after your job_descriptions.csv is ready:
    python scripts/ingest_jobs.py

IMPORTANT: This script has a collection.count() guard at the start.
If the collection already has entries, it exits without adding duplicates.
To re-ingest from scratch, delete data/chroma_db/ and run again.

After running, commit data/chroma_db/ to git — Streamlit Cloud's ephemeral
filesystem means the folder is gone after every restart unless it's in the repo.
"""

import sys
import os

# Allow imports from the project root when run as a script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import chromadb
from src.embedder import embed

JOBS_CSV = "data/job_descriptions.csv"
CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "jobs"


def run_ingest():
    """
    Read job_descriptions.csv, embed each job, and store in ChromaDB.

    Embedding strategy: Option A (skills-only).
    We embed the skills_required field so the student vector (embedded extracted skills)
    and job vectors are in the same semantic space.
    Both sides are lists of skills joined as a comma-separated string.
    """
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # Ensure cosine distance is used
    )

    # Duplicate guard — exit early if already ingested
    existing_count = collection.count()
    if existing_count > 0:
        print(f"Collection already has {existing_count} entries.")
        print("Delete data/chroma_db/ and re-run to ingest fresh data.")
        return

    df = pd.read_csv(JOBS_CSV, encoding="utf-8")
    print(f"Loaded {len(df)} jobs from {JOBS_CSV}")

    ids = []
    embeddings = []
    metadatas = []

    for idx, row in df.iterrows():
        job_id = str(row.get("id", idx))

        # Embed the skills_required field (Option A — aligned with student embedding)
        skills_text = str(row.get("skills_required", "")).strip()
        if not skills_text:
            print(f"  Warning: job '{row.get('title', job_id)}' has no skills_required — skipping.")
            continue

        print(f"  Embedding job {idx + 1}/{len(df)}: {row.get('title', job_id)}")
        vector = embed(skills_text)  # Returns list[float] via .tolist() in embedder

        ids.append(job_id)
        embeddings.append(vector)
        metadatas.append({
            "title": str(row.get("title", "")),
            "company_type": str(row.get("company_type", "")),
            "seniority": str(row.get("seniority", "")),
            "location": str(row.get("location", "")),
            "skills_required": str(row.get("skills_required", "")),
            "raw_description": str(row.get("raw_description", "")),
        })

    if not ids:
        print("No valid jobs to ingest. Check that skills_required column is populated.")
        return

    collection.add(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print(f"\nIngestion complete. {collection.count()} jobs stored in ChromaDB.")
    print("Next step: commit data/chroma_db/ to git before deploying to Streamlit Cloud.")


if __name__ == "__main__":
    run_ingest()