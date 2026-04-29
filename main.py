"""
main.py — FastAPI backend for Career Compass.

Serves four endpoints for the React frontend:
- GET  /health              → { status, job_count }
- POST /api/extract-skills  → { text } → { skills }
- POST /api/match-jobs      → { skills } → { matches }
- POST /api/analyze-gaps    → { job, student_skills } → { missing_skills, week1..4 }

Run with: uvicorn main:app --reload
Deploy with: uvicorn main:app --host 0.0.0.0 --port $PORT
"""

import os
import chromadb
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.config import get_secret
from src.extractor import extract_skills
from src.embedder import embed
from src.matcher import match_jobs
from src.gap_analyzer import analyze_gaps

# ── Startup validation ────────────────────────────────────────────────────────
def validate_startup():
    """Check that required dependencies are available before starting."""
    try:
        get_secret("ANTHROPIC_API_KEY")
    except ValueError as e:
        raise RuntimeError(f"ANTHROPIC_API_KEY not set: {e}")

    try:
        client = chromadb.PersistentClient(path="data/chroma_db")
        collection = client.get_collection("jobs")
        job_count = collection.count()
        if job_count == 0:
            raise ValueError("ChromaDB collection is empty")
        print(f"✓ ChromaDB ready with {job_count} jobs")
    except Exception as e:
        raise RuntimeError(f"ChromaDB failed: {e}. Run scripts/ingest_jobs.py first.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context: startup validation, shutdown cleanup."""
    validate_startup()
    yield
    # Cleanup on shutdown (if needed)


app = FastAPI(
    title="Career Compass API",
    description="NLP-powered career matching for Sydney tech jobs",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS configuration ────────────────────────────────────────────────────────
# Allow frontend to call this API
FRONTEND_URL = os.getenv("FRONTEND_URL", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL] if FRONTEND_URL != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request/Response models ───────────────────────────────────────────────────


class ExtractRequest(BaseModel):
    text: str


class ExtractResponse(BaseModel):
    skills: list[str]


class MatchJobsRequest(BaseModel):
    skills: list[str]


class MatchJobsResponse(BaseModel):
    matches: list[dict]


class AnalyzeGapsRequest(BaseModel):
    job: dict
    student_skills: list[str]


class AnalyzeGapsResponse(BaseModel):
    missing_skills: list[str]
    week1: str
    week2: str
    week3: str
    week4: str


# ── Endpoints ─────────────────────────────────────────────────────────────────


@app.get("/health")
async def health():
    """Health check: returns status and job count."""
    try:
        client = chromadb.PersistentClient(path="data/chroma_db")
        collection = client.get_collection("jobs")
        job_count = collection.count()
        return {"status": "ok", "job_count": job_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")


@app.post("/api/extract-skills", response_model=ExtractResponse)
async def api_extract_skills(req: ExtractRequest):
    """Extract canonical skills from raw text using spaCy PhraseMatcher."""
    try:
        skills = extract_skills(req.text)
        return ExtractResponse(skills=skills)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {e}")


@app.post("/api/match-jobs", response_model=MatchJobsResponse)
async def api_match_jobs(req: MatchJobsRequest):
    """Embed skills and find top 6 matching jobs from ChromaDB."""
    try:
        if not req.skills:
            return MatchJobsResponse(matches=[])

        skills_text = ", ".join(req.skills)
        vector = embed(skills_text)
        matches = match_jobs(vector, top_k=6)

        return MatchJobsResponse(matches=matches)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job matching failed: {e}")


@app.post("/api/analyze-gaps", response_model=AnalyzeGapsResponse)
async def api_analyze_gaps(req: AnalyzeGapsRequest):
    """Call Claude Haiku to identify skill gaps and generate a 30-day plan."""
    try:
        result = analyze_gaps(req.job, req.student_skills)

        return AnalyzeGapsResponse(
            missing_skills=result.get("missing_skills", []),
            week1=result.get("week1", ""),
            week2=result.get("week2", ""),
            week3=result.get("week3", ""),
            week4=result.get("week4", ""),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gap analysis failed: {e}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
