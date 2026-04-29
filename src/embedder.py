"""
embedder.py — Text embedding using sentence-transformers.

Model: all-MiniLM-L6-v2 (384-dim, fast on CPU, MTEB ~56)
Cached as a module-level singleton — model loads once, shared across all processes.

Locked interface (do not change signature without team agreement):
    embed(text: str) -> list[float]
    Returns 384-dim embedding as a Python list (NOT a numpy array).
    ChromaDB requires list, not numpy — always call .tolist().
"""

from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_MODEL = None


def _load_model() -> SentenceTransformer:
    """Load the sentence-transformers model. Cached as a module-level singleton."""
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer(MODEL_NAME)
    return _MODEL


def embed(text: str) -> list[float]:
    """
    Embed a text string into a 384-dimensional vector.

    Args:
        text: Any string — typically a joined skill list
              (e.g. "python, sql, power bi, dbt") or raw brain dump text.

    Returns:
        384-dim embedding as a Python list[float].
        .tolist() is called internally — safe to pass directly to ChromaDB.
    """
    model = _load_model()
    # .tolist() converts numpy ndarray -> Python list.
    # ChromaDB will reject numpy arrays — this is non-negotiable.
    return model.encode(text).tolist()