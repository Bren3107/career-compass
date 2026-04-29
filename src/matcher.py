"""
matcher.py — Semantic job matching using ChromaDB.

Queries the persisted ChromaDB collection with a student embedding vector
and returns the top-k most similar jobs.

IMPORTANT: ChromaDB query() returns DISTANCE (0=identical, 2=opposite).
We convert to SIMILARITY with: score = 1 - distance
Do NOT display raw distances to users — they are backwards.

Similarity label thresholds (calibrated for all-MiniLM-L6-v2 on job matching):
    >= 0.60  → "Strong match"
    0.40–0.59 → "Moderate match"
    < 0.40   → "Weak match"
Do NOT use 0.85 as a threshold — it is never reached in practice for this task.

Locked interface (do not change signature without team agreement):
    match_jobs(student_vector: list[float], top_k: int = 3) -> list[dict]
    Returns list of {title, score, skills_required, raw_description}
    score is cosine SIMILARITY (0–1), not distance.
"""

import streamlit as st
import chromadb

CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "jobs"


@st.cache_resource
def _load_collection():
    """
    Load the ChromaDB persistent client and the jobs collection.
    @st.cache_resource = one shared instance across all sessions.
    """
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_collection(COLLECTION_NAME)


def _score_label(score: float) -> str:
    """Return a human-readable match label based on calibrated thresholds."""
    if score >= 0.60:
        return "Strong match"
    elif score >= 0.40:
        return "Moderate match"
    else:
        return "Weak match"


def match_jobs(student_vector: list[float], top_k: int = 3) -> list[dict]:
    """
    Query ChromaDB for the top-k most similar jobs to the student vector.

    Args:
        student_vector: 384-dim embedding as a Python list (from embedder.embed()).
        top_k: Number of top matches to return (default 3).

    Returns:
        List of dicts, each with:
            {
                "title": str,
                "score": float,        # cosine similarity, 0–1
                "label": str,          # "Strong match" / "Moderate match" / "Weak match"
                "skills_required": str,
                "raw_description": str,
                "company_type": str,
                "seniority": str,
                "location": str,
            }
        Sorted by score descending (best match first).
    """
    collection = _load_collection()

    results = collection.query(
        query_embeddings=[student_vector],
        n_results=top_k,
        include=["metadatas", "distances"],
    )

    matches = []
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for metadata, distance in zip(metadatas, distances):
        # ChromaDB returns cosine DISTANCE. Convert to SIMILARITY.
        score = 1.0 - distance

        matches.append({
            "title": metadata.get("title", "Unknown"),
            "score": round(score, 4),
            "label": _score_label(score),
            "skills_required": metadata.get("skills_required", ""),
            "raw_description": metadata.get("raw_description", ""),
            "company_type": metadata.get("company_type", ""),
            "seniority": metadata.get("seniority", ""),
            "location": metadata.get("location", ""),
        })

    return sorted(matches, key=lambda x: x["score"], reverse=True)