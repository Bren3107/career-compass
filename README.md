# Career Compass

An NLP-powered career matching tool that helps students break into the Sydney tech job market. Paste your resume or upload a PDF, get matched to real Sydney jobs, and receive a personalised 4-week learning roadmap for the gaps.

---

## How It Works

1. **Brain Dump** — Paste your resume text or upload a PDF. The app extracts your tech skills using spaCy PhraseMatcher against the ESCO skills taxonomy.
2. **Job Matches** — Your skills are embedded using `all-MiniLM-L6-v2` and compared against 58 real Sydney tech jobs stored in ChromaDB. The top 6 matches are returned with cosine similarity scores and match labels.
3. **Resume Optimizer** — Paste any job description to see your exact skill gaps and the ATS keywords you should add to your resume.
4. **Roadmap** — Select a matched job (or use your custom role). GPT-4o-mini identifies your skill gaps and writes a concrete 4-week learning plan to close them.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, React Router, Framer Motion, Tailwind CSS, Vite |
| Backend | FastAPI, Uvicorn |
| Skill Extraction | spaCy `en_core_web_sm` + PhraseMatcher + ESCO taxonomy |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (384-dim) |
| Vector Store | ChromaDB (persistent, pre-populated, committed to repo) |
| Gap Analysis | OpenAI GPT-4o-mini |
| PDF Parsing | pdfplumber |

---

## Prerequisites

- Python 3.11.x (ChromaDB has compatibility issues with 3.12+)
- Node.js 18+
- An OpenAI API key

---

## Setup

### 1. Install Python dependencies

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

Copy `.env.example` to `.env` and add your OpenAI key:

```bash
cp .env.example .env
```

Edit `.env`:

```
OPENAI_API_KEY=your_key_here
```

> Adzuna API keys are only needed if you want to re-fetch job data from scratch. They are not required to run the app — the ChromaDB vector store is already populated and committed to the repo.

---

## Running the App

You need **two terminals** open at the project root.

**Terminal 1 — Backend:**

```bash
uvicorn main:app --reload
```

API available at `http://localhost:8000`

**Terminal 2 — Frontend:**

```bash
cd frontend
npm run dev
```

App available at `http://localhost:5173`

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check — returns status and job count |
| `/api/extract-skills` | POST | Extract canonical skills from raw text |
| `/api/extract-from-pdf` | POST | Upload a PDF resume and extract skills |
| `/api/match-jobs` | POST | Embed skills and return top 6 matching jobs |
| `/api/analyze-gaps` | POST | Generate skill gap analysis and 4-week roadmap |
| `/api/resume-optimize` | POST | Identify skill gaps and ATS keywords from a job description |

---

## Project Structure

```
career-compass/
├── main.py                   # FastAPI backend (all endpoints)
├── requirements.txt
├── .env.example
├── render.yaml               # Render deployment config
│
├── src/                      # Python NLP pipeline
│   ├── config.py             # API key helper (tries st.secrets then .env)
│   ├── extractor.py          # spaCy PhraseMatcher skill extraction
│   ├── embedder.py           # sentence-transformers embeddings
│   ├── matcher.py            # ChromaDB semantic job matching
│   └── gap_analyzer.py       # OpenAI GPT-4o-mini roadmap + resume optimizer
│
├── frontend/
│   ├── src/
│   │   ├── pages/            # Landing, BrainDump, JobMatches, Optimize, Roadmap
│   │   ├── components/       # Header, SkillBadge, StepIndicator, ChatPanel, etc.
│   │   ├── context/          # AppContext (global skills, job, roadmap state)
│   │   └── api/              # client.js (typed API wrapper)
│   └── vercel.json           # Vercel frontend deployment config
│
├── data/
│   ├── job_descriptions.csv  # 58 Sydney tech jobs
│   ├── skills_taxonomy.csv   # ESCO skills taxonomy with aliases
│   └── chroma_db/            # Pre-embedded vector store (committed to repo)
│
├── scripts/
│   ├── fetch_adzuna_jobs.py  # Fetch jobs from Adzuna API
│   ├── fetch_esco_skills.py  # Fetch ESCO skills taxonomy
│   ├── process_esco_skills.py
│   └── ingest_jobs.py        # Embed jobs and load into ChromaDB
│
└── test_system.py            # Automated backend tests
```

---

## Similarity Score Labels

Scores are cosine similarity (0–1) converted from ChromaDB's distance output.

| Score | Label |
|-------|-------|
| ≥ 0.60 | Strong match |
| 0.40 – 0.59 | Moderate match |
| < 0.40 | Weak match |

Scores of 0.85+ are not expected for this task — the 0.35–0.65 range is normal and meaningful for semantic skill-to-job matching.

---

## Running Tests

With the backend running on port 8000:

```bash
python test_system.py
```

Manual test results are recorded in [test-results.md](test-results.md).

---

## Rebuilding the Job Database (Optional)

The `data/chroma_db/` folder is already populated with 58 jobs. Only do this if you want to re-ingest fresh data.

1. Add Adzuna API credentials to `.env` (get them from [developer.adzuna.com](https://developer.adzuna.com/))
2. Fetch new jobs: `python scripts/fetch_adzuna_jobs.py`
3. Re-ingest into ChromaDB: `python scripts/ingest_jobs.py`
