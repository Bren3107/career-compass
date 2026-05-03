"""
main.py — FastAPI backend for Career Compass.

Serves five endpoints for the React frontend:
- GET  /health                    → { status, job_count }
- POST /api/extract-skills        → { text } → { skills }
- POST /api/match-jobs            → { skills } → { matches }
- POST /api/analyze-gaps          → { job, student_skills } → { missing_skills, week1..4 }
- POST /api/resume-optimize       → { job_description, student_skills } → { missing_skills, keyword_recommendations }

Run with: uvicorn main:app --reload
Deploy with: uvicorn main:app --host 0.0.0.0 --port $PORT
"""

import os
import chromadb
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pdfplumber
import io

from src.config import get_secret
from src.extractor import extract_skills
from src.embedder import embed
from src.matcher import match_jobs
from src.gap_analyzer import analyze_gaps, optimize_resume

# ── Startup validation ────────────────────────────────────────────────────────
def validate_startup():
    """Check that required dependencies are available before starting."""
    try:
        get_secret("OPENAI_API_KEY")
    except ValueError as e:
        raise RuntimeError(f"OPENAI_API_KEY not set: {e}")

    try:
        client = chromadb.PersistentClient(path="data/chroma_db")
        collection = client.get_collection("jobs")
        job_count = collection.count()
        if job_count == 0:
            raise ValueError("ChromaDB collection is empty")
        print(f"[OK] ChromaDB ready with {job_count} jobs")
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


class ResumeOptimizeRequest(BaseModel):
    job_description: str
    student_skills: list[str]


class ResumeOptimizeResponse(BaseModel):
    missing_skills: list[str]
    keyword_recommendations: list[str]


class ExtractFromPdfResponse(BaseModel):
    text: str
    skills: list[str]


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


@app.post("/api/resume-optimize", response_model=ResumeOptimizeResponse)
async def api_resume_optimize(req: ResumeOptimizeRequest):
    """Analyse a raw job description against student skills for resume optimisation."""
    try:
        result = optimize_resume(req.job_description, req.student_skills)
        return ResumeOptimizeResponse(
            missing_skills=result.get("missing_skills", []),
            keyword_recommendations=result.get("keyword_recommendations", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume optimization failed: {e}")


@app.post("/api/extract-from-pdf", response_model=ExtractFromPdfResponse)
async def api_extract_from_pdf(file: UploadFile = File(...)):
    """Extract text from a PDF resume and extract skills from it."""
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")

        # Read the uploaded file into memory
        contents = await file.read()
        pdf_file = io.BytesIO(contents)

        # Extract text from PDF
        extracted_text = ""
        try:
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    extracted_text += page.extract_text() or ""
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read PDF: {str(e)}")

        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="No text found in PDF")

        # Extract skills from the extracted text
        skills = extract_skills(extracted_text)

        return ExtractFromPdfResponse(text=extracted_text, skills=skills)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF extraction failed: {e}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
