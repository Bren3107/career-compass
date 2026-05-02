# Career Compass

An NLP-powered career matching tool that helps students break into the Sydney tech job market. Paste your resume or skills, get matched to real jobs, and receive a personalised 4-week learning roadmap for the gaps.

---

## How It Works

1. **Brain Dump** — Paste your resume text or upload a PDF. The app extracts your tech skills using spaCy.
2. **Job Matches** — Your skills are embedded and compared against 58 Sydney tech jobs in a vector database. The top 6 matches are shown with similarity scores.
3. **Roadmap** — Select a job you want to target. GPT-4o-mini identifies your skill gaps and writes a concrete 4-week plan to close them.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, React Router, Framer Motion, Tailwind CSS, Vite |
| Backend | FastAPI, Uvicorn |
| Skill Extraction | spaCy `en_core_web_sm` + PhraseMatcher |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector Store | ChromaDB (persistent, committed to repo) |
| Gap Analysis | OpenAI GPT-4o-mini |
| PDF Parsing | pdfplumber |

---

## Prerequisites

- Python 3.11.x (ChromaDB has issues with 3.12+)
- Node.js 18+
- An OpenAI API key

---

## Setup

### 1. Clone and install Python dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Install frontend dependencies

```bash
cd frontend
npm install
```

### 3. Configure your API key

Copy `.env.example` to `.env` and fill in your OpenAI key:

```bash
cp .env.example .env
```

Then edit `.env`:

```
OPENAI_API_KEY=your_key_here
```

> The Adzuna keys are only needed if you want to re-fetch job data. They are not required to run the app.

---

## Running the App

You need **two terminals** open in the project root.

**Terminal 1 — Backend:**

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

**Terminal 2 — Frontend:**

```bash
cd frontend
npm run dev
```

The app will be available at `http://localhost:5173`.

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Status check — returns job count |
| `/api/extract-skills` | POST | Extract skills from raw text |
| `/api/extract-from-pdf` | POST | Upload a PDF and extract skills |
| `/api/match-jobs` | POST | Match skills to top 6 jobs |
| `/api/analyze-gaps` | POST | Generate skill gap analysis and 4-week roadmap |

---

## Project Structure

```
career-compass/
├── main.py                  # FastAPI backend (all endpoints)
├── requirements.txt
├── .env.example
│
├── src/                     # Python NLP pipeline
│   ├── config.py            # API key helper (get_secret)
│   ├── extractor.py         # spaCy PhraseMatcher skill extraction
│   ├── embedder.py          # sentence-transformers embeddings
│   ├── matcher.py           # ChromaDB job matching
│   └── gap_analyzer.py      # OpenAI GPT-4o-mini roadmap generation
│
├── frontend/
│   └── src/
│       ├── pages/           # Landing, BrainDump, JobMatches, Roadmap
│       ├── components/      # Header, SkillBadge, StepIndicator, etc.
│       ├── context/         # AppContext (global state)
│       └── api/             # client.js (API wrapper)
│
├── data/
│   ├── job_descriptions.csv # 58 Sydney tech jobs
│   ├── skills_taxonomy.csv  # ESCO skills taxonomy
│   └── chroma_db/           # Pre-embedded vector store (committed)
│
└── scripts/
    ├── fetch_adzuna_jobs.py  # Fetch jobs from Adzuna API
    ├── ingest_jobs.py        # Embed jobs into ChromaDB
    └── fetch_esco_skills.py  # Fetch ESCO skills taxonomy
```

---

## Similarity Score Labels

| Score | Label |
|-------|-------|
| ≥ 0.60 | Strong match |
| 0.40 – 0.59 | Moderate match |
| < 0.40 | Weak match |

A warning is shown on the Job Matches page if no strong matches are found.

---

## Rebuilding the Job Database (Optional)

The `data/chroma_db/` folder is already populated with 58 jobs and committed to the repo. You only need this if you want to re-ingest fresh job data.

1. Get Adzuna API credentials from [developer.adzuna.com](https://developer.adzuna.com/) and add them to `.env`
2. Fetch new jobs: `python scripts/fetch_adzuna_jobs.py`
3. Re-ingest into ChromaDB: `python scripts/ingest_jobs.py`

---

## Running Tests

```bash
# With the backend running on port 8000:
python test_system.py
```
