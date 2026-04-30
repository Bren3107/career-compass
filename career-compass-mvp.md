# MVP Plan: The Career Compass

> **Context:** Students in the 2026 Sydney market have real skills but cannot articulate them in ways that match job descriptions. They write vague "brain dumps" and don't know which specific skills they're missing to land specific roles. This NLP tool solves the translation problem: unstructured student life → market-aligned career roadmap.

---

## Project Overview

**The Career Compass** is a full-stack NLP web app (React frontend + FastAPI backend + Python NLP pipeline) that accepts a student's unstructured "brain dump" of life experience, extracts latent skills using NLP, semantically matches those skills against a curated dataset of 50 Sydney job descriptions, identifies the 2–3 skill gaps preventing a "match," and generates a personalised 30-day learning roadmap.

**MVP Complete =** A student can paste their brain dump → see their Top 3 job matches with similarity scores → see the exact skills they're missing → receive a 30-day plan to close the gap. Runnable locally, deployable to cloud (Vercel + Railway/Heroku).

---

## Core MVP Feature Set

| Priority | Feature | Description | Why It's MVP |
|----------|---------|-------------|--------------|
| P0 | Brain Dump Input | Streamlit text area for unstructured student experience text | Entry point — nothing works without it |
| P0 | Skill Extraction | spaCy + skills taxonomy CSV to extract latent skills from text | Core NLP signal — must exist before matching |
| P0 | Semantic Job Matching | Embed student profile, query ChromaDB, return Top 3 jobs with cosine similarity scores | The core value proposition |
| P0 | Gap Analysis | RAG retrieval of matched job requirements + hosted LLM to identify missing skills | Answers "what do I need to learn?" |
| P0 | Learning Roadmap | LLM-generated 30-day plan based on skill gaps | Answers "how do I get there?" |
| P0 | Curated Job Dataset | CSV of 30–50 Sydney job descriptions, pre-embedded into ChromaDB | No matching without data |
| P1 | Match Score Visualisation | Progress bars / radar chart showing similarity score per job | Makes the result legible to non-technical users |
| P1 | Extracted Skills Display | Show which skills were detected from the brain dump | Builds trust in the system |
| P1 | Sample Brain Dump | Pre-filled example so users can see the output immediately | Demo-critical for showcasing the project |
| P2 | PDF / Link Export | Export the roadmap as a shareable document | Post-MVP polish |
| P2 | User Accounts | Persistent profiles across sessions | Not needed for MVP demo |
| P2 | Real-time Job Scraping | Pull live jobs from Seek/LinkedIn | MVP uses static curated dataset |

---

## Tech Stack Decision

| Layer | Choice | Rationale | Alternatives Ruled Out |
|-------|--------|-----------|------------------------|
| **Frontend** | React + Vite | Modern, component-based, fast hot reload, easy animations (Framer Motion) | Vue (learning curve), Next.js (overkill for SPA) |
| **Backend** | FastAPI | Fast, async-ready, automatic API docs, CORS support, easy to deploy | Flask (no async, slower), Django (overkill) |
| **Embedding Model** | `sentence-transformers/all-MiniLM-L6-v2` | 384-dim, ~14k sentences/sec on CPU, MTEB ~56, community standard for semantic search | `all-mpnet-base-v2` (3.5x slower, marginal accuracy gain), OpenAI embeddings (API cost + latency) |
| **Vector Store** | ChromaDB | Auto-persists (DuckDB+Parquet), metadata filtering, zero config for <10k docs | FAISS (no built-in persistence, same speed at 50 docs, higher complexity), Pinecone (cloud cost) |
| **Skill Extraction** | spaCy + skills taxonomy CSV | No training data needed, fast, deterministic, easy to extend taxonomy | Custom NER model (needs 500+ labeled examples), Llama-3-8B locally (8GB+ VRAM, slow) |
| **Gap Generation LLM** | Claude Haiku API (`claude-haiku-4-5-20251001`) | ~$0.001/request, fast, reliable, structured output, no local GPU needed | GPT-4o-mini (equivalent cost, second choice), Llama local (slow, fragile setup) |
| **Data Storage** | CSV + ChromaDB persistence | No database server to manage; job data is static for MVP | SQLite (overcomplicated), PostgreSQL (far too heavy) |
| **Frontend Deployment** | Vercel | 1-click GitHub deploy, free tier, automatic builds, edge functions | Netlify (similar), GitHub Pages (no API support) |
| **Backend Deployment** | Railway or Heroku | Simple deploy, environment variables, PostgreSQL optional | AWS (overkill), DigitalOcean (more ops work) |
| **Python Version** | 3.11+ | Required by latest sentence-transformers and ChromaDB | — |

---

## System Architecture

```
┌──────────────────────────────────────┐
│        REACT FRONTEND (Vite)         │
│  Landing → Brain Dump → Matches →    │
│  Roadmap (animated page transitions) │
└────────────────┬─────────────────────┘
                 │ fetch() via API
                 ▼
┌──────────────────────────────────────┐
│      FASTAPI BACKEND (Python)        │
│                                      │
│  /health                             │
│  /api/extract-skills                 │
│  /api/match-jobs                     │
│  /api/analyze-gaps                   │
└────────────────┬─────────────────────┘
                 │ imports
                 ▼
┌──────────────────────────────────────┐
│      src/ NLP PIPELINE (Python)      │
│                                      │
│  brain_dump.txt                      │
│       │                              │
│       ▼                              │
│  [extractor.py]  ← skills_taxonomy  │
│  spaCy PhraseMatcher                 │
│       │                              │
│       ▼                              │
│  [embedder.py]                       │
│  sentence-transformers (384-dim)     │
│       │                              │
│       ▼                              │
│  [matcher.py]  ← ChromaDB (jobs)    │
│  Cosine similarity → Top 3 matches   │
│       │                              │
│       ▼                              │
│  [gap_analyzer.py]                   │
│  Claude Haiku API → 30-day plan      │
└──────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│        DATA LAYER (Persistent)       │
│  data/job_descriptions.csv           │
│  data/skills_taxonomy.csv            │
│  data/chroma_db/                     │
└──────────────────────────────────────┘
```

**Key Data Flow:**
1. React user pastes brain dump → `POST /api/extract-skills`
2. Backend calls `extractor.py` → returns skill list
3. React shows skills → user clicks "Find Matches" → `POST /api/match-jobs`
4. Backend embeds skills + queries ChromaDB → returns Top 3 jobs
5. React displays matches → user clicks "Generate Roadmap" → `POST /api/analyze-gaps`
6. Backend calls Claude Haiku → returns gap analysis + weekly plan
7. React displays roadmap with animations

---

## Data Model

### `job_descriptions.csv`
| Field | Type | Description |
|-------|------|-------------|
| `id` | str | Unique job ID |
| `title` | str | Job title (e.g., "BI Engineer") |
| `company_type` | str | Industry/sector |
| `seniority` | str | Junior / Mid / Senior |
| `location` | str | Sydney suburb / Remote |
| `skills_required` | str | Comma-separated required skills |
| `raw_description` | str | Full job description text |

### `skills_taxonomy.csv`
| Field | Type | Description |
|-------|------|-------------|
| `skill_name` | str | Canonical skill name |
| `category` | str | Domain (e.g., "Data Engineering", "ML") |
| `aliases` | str | Alternate names / abbreviations |

### Streamlit Session State (ephemeral per session)
```python
st.session_state = {
    "brain_dump": str,
    "extracted_skills": list[str],
    "user_vector": np.ndarray,
    "top_matches": list[dict],  # {title, score, skills_required}
    "gap_analysis": dict,       # {missing_skills, learning_plan}
}
```

---

## Project Structure

```
career-compass/
├── main.py                     # FastAPI entry point with 4 endpoints
├── src/                        # Python NLP pipeline (shared by FastAPI)
│   ├── __init__.py
│   ├── config.py               # get_secret() helper for .env
│   ├── extractor.py            # spaCy PhraseMatcher skill extraction
│   ├── embedder.py             # sentence-transformers embedding
│   ├── matcher.py              # ChromaDB query + similarity scoring
│   └── gap_analyzer.py         # Claude Haiku API + gap analysis
├── frontend/                   # React + Vite
│   ├── src/
│   │   ├── App.jsx             # Router + page transitions
│   │   ├── main.jsx            # React entry point
│   │   ├── pages/
│   │   │   ├── Landing.jsx     # Hero + intro
│   │   │   ├── BrainDump.jsx   # Text input + skill extraction
│   │   │   ├── JobMatches.jsx  # Top matches display
│   │   │   └── Roadmap.jsx     # Skill gaps + 30-day plan
│   │   ├── components/
│   │   │   ├── StepIndicator.jsx
│   │   │   ├── SkillBadge.jsx
│   │   │   └── LinearBackground.jsx
│   │   ├── context/
│   │   │   └── AppContext.jsx  # Global state management
│   │   ├── api/
│   │   │   └── client.js       # API client (fetch wrapper)
│   │   └── styles/
│   │       └── global.css      # Tailwind + custom vars
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── index.html
│   └── dist/                   # Built assets (deployed to Vercel)
├── data/
│   ├── job_descriptions.csv    # 30-50 curated Sydney job descriptions
│   ├── skills_taxonomy.csv     # ~200 skills with categories + aliases
│   └── chroma_db/              # ChromaDB persisted vector store
├── scripts/
│   └── ingest_jobs.py          # One-time: embed jobs into ChromaDB
├── .env.example                # ANTHROPIC_API_KEY=your_key_here
├── requirements.txt            # Python dependencies
└── README.md
```

---

## Implementation Roadmap

### Phase 1 — Foundation (Days 1–3) **[MOSTLY DONE]**
- [x] Create project directory + Python virtual environment
- [x] Write `requirements.txt` (fastapi, uvicorn, sentence-transformers, chromadb, spacy, anthropic, python-dotenv, pandas)
- [x] Download spaCy model: `python -m spacy download en_core_web_sm`
- [x] Build `data/job_descriptions.csv` with 30–50 Sydney jobs
- [x] Build `data/skills_taxonomy.csv` with ~200 skills + aliases
- [x] Write and run `scripts/ingest_jobs.py` to embed jobs into ChromaDB
- [x] Verify ChromaDB collection is populated

### Phase 2 — Core NLP Pipeline (Days 4–7) **[DONE]**
- [x] `src/config.py`: `get_secret()` helper for .env files
- [x] `src/extractor.py`: spaCy PhraseMatcher + taxonomy CSV → deduplicated skills
- [x] `src/embedder.py`: sentence-transformers with module-level caching → 384-dim vector
- [x] `src/matcher.py`: ChromaDB query with distance→similarity conversion, score labels
- [x] `src/gap_analyzer.py`: RAG prompt builder, Claude Haiku API call, JSON parsing with error handling
- [x] Manual test of full pipeline

### Phase 3a — FastAPI Backend (Days 8–9) **[STRUCTURED, NEEDS TESTING]**
- [x] `main.py`: FastAPI setup with CORS, startup validation
- [x] `GET /health`: status + job count check
- [x] `POST /api/extract-skills`: accept text → return skill list
- [x] `POST /api/match-jobs`: accept skills → return top 6 matches with scores
- [x] `POST /api/analyze-gaps`: accept job + student skills → return gap analysis + 30-day plan
- [ ] **Test all endpoints end-to-end** (curl, Postman, or automated)
- [ ] **Verify error handling** (missing ChromaDB, API key, malformed requests)
- [ ] **Add request/response logging** for debugging

### Phase 3b — React Frontend (Days 10–12) **[SCAFFOLD DONE, NEEDS VERIFICATION]**
- [x] Setup Vite + React project structure
- [x] Configure Tailwind CSS + custom CSS variables
- [x] `frontend/src/App.jsx`: Router + page transitions (Framer Motion)
- [x] `frontend/src/pages/Landing.jsx`: Hero + intro section
- [x] `frontend/src/pages/BrainDump.jsx`: Text input + extract button
- [x] `frontend/src/pages/JobMatches.jsx`: Display top 6 matches with scores
- [x] `frontend/src/pages/Roadmap.jsx`: Display missing skills + 30-day plan
- [x] `frontend/src/context/AppContext.jsx`: Global state management
- [x] `frontend/src/api/client.js`: API client wrapper
- [ ] **Test all pages end-to-end** (do they render? Do API calls work?)
- [ ] **Test state flow** (does data persist across pages? Do animations work?)
- [ ] **Test error states** (what if API fails? Empty results?)

### Phase 4 — Integration & Polish (Days 13–15) **[TO DO]**
- [ ] **Run both servers locally**: `uvicorn main:app --reload` + `npm run dev` in frontend/
- [ ] **Test full user journey**: Brain dump → Extract → Match → Roadmap
- [ ] **Test with 5 different student profiles** (data analyst, software dev, HR→data, etc.)
- [ ] **Handle edge cases**: empty input, no skills detected, no matches found, API timeouts
- [ ] **Add loading states** in React (spinners during API calls)
- [ ] **Add error messages** in React (display API errors to user)
- [ ] **Test responsive design** (mobile, tablet, desktop)
- [ ] **Add rate limiting** (optional, for Cloud deployment)

### Phase 5 — Deployment (Days 16–17) **[TO DO]**
- [ ] **Deploy FastAPI backend**: Railway, Heroku, or Render
  - Add `ANTHROPIC_API_KEY` to production environment
  - Ensure ChromaDB is persisted (committed to git or on persistent volume)
- [ ] **Deploy React frontend**: Vercel (1-click from GitHub)
  - Update `.env` with production API URL
- [ ] **Test in production** (real users, real API calls)
- [ ] **Monitor logs** for errors and performance

---

## Key Technical Decisions & Trade-offs

1. **React + FastAPI for MVP.** React provides a modern, animated UX with component reusability. FastAPI separates the NLP logic from the UI and enables easier testing, monitoring, and future API consumers. HTTP overhead is negligible at scale; separating concerns simplifies development.

2. **Vite over Create React App.** Vite offers 10–100x faster hot reload, smaller bundle size, and zero config for modern ES modules. Create React App is slower and overkill for an MVP.

3. **Framer Motion for animations.** Lightweight, declarative animations for page transitions and interactive elements. Better performance than CSS-only animations at scale.

4. **ChromaDB over FAISS.** At 50 docs, speed is identical. ChromaDB auto-persists (DuckDB+Parquet), supports metadata filtering (e.g., "only Junior roles"), and requires zero manual serialization. FAISS would require writing `faiss.write_index()` and `faiss.read_index()` boilerplate.

5. **Skills taxonomy CSV over custom NER model.** Training a custom spaCy NER model requires 500+ annotated examples and a training loop. A taxonomy CSV can be built in a few hours and extended incrementally. This is the right trade-off for a university project timeline.

6. **Hosted LLM (Claude Haiku) for gap generation.** Running Llama-3-8B locally requires 8GB+ VRAM or is unusably slow on CPU. Claude Haiku costs ~$0.001/request — essentially free for demo usage.

7. **Static curated dataset.** Live job scraping from Seek/LinkedIn introduces web scraping complexity, rate limiting, and legal considerations. 30–50 manually curated jobs is sufficient for a compelling demo and removes all data pipeline risk.

8. **AppContext for state management.** React Context is sufficient for a single-user MVP. Redux/Zustand add unnecessary complexity; upgrade only if the app scales to multi-user or complex shared state.

---

## What Is Explicitly Out of Scope for MVP

- **PDF resume upload** — plain text brain dump first; PDF parsing (PyMuPDF/pdfplumber) adds complexity without changing the NLP pipeline
- **User accounts / authentication** — session state (React Context) is sufficient for a demo; add login only if multi-user sessions are needed
- **Real-time job scraping** — static curated CSV is faster and safer to build
- **Email delivery or PDF export** — copy-paste/screenshot is fine for MVP
- **Salary data integration** — interesting but not part of the core value proposition
- **Database (PostgreSQL, MongoDB)** — ChromaDB persistence is enough for MVP
- **Custom NER model training** — taxonomy CSV achieves the same result faster
- **Multiple Australian cities** — Sydney only for MVP focus
- **Advanced styling** — Tailwind + custom CSS variables are sufficient; no design system overhaul yet
- **Analytics / usage tracking** — not needed to validate the MVP

---

## Open Questions & Risks

| # | Question / Risk | Mitigation |
|---|----------------|------------|
| 1 | **CORS headers** — React frontend on different origin than FastAPI backend | FastAPI `CORSMiddleware` is already configured; set `FRONTEND_URL` env var in production |
| 2 | **ChromaDB on cloud deployment** — Persistent volume may be ephemeral | Commit pre-built ChromaDB to git (small at 50 docs) OR use persistent volume on Railway/Heroku |
| 3 | **spaCy model download on cloud** — Model (~40MB) may not be in venv | Install with `pip install -r requirements.txt` (model is auto-downloaded on first import) |
| 4 | **Claude API key management** | Use `.env` locally, environment variables in production; never commit `.env` to git |
| 5 | **Skill extraction quality** — taxonomy may miss domain-specific tools | Start with 200 skills; add missed ones after testing with 5 brain dumps |
| 6 | **Match quality** — cosine similarity may return irrelevant matches for very short brain dumps | Add minimum word count validation (>30 words) and display a confidence warning for low scores (<0.4) |
| 7 | **API rate limits** — Claude Haiku has tier limits | For demo use, Tier 1 limits are fine; consider caching results in production |
| 8 | **React state loss on page refresh** — User data disappears on F5 | Add localStorage persistence to AppContext (optional; session-only is fine for MVP) |

---

## Day 1 Checklist (What to Do First Monday Morning)

1. `mkdir career-compass && cd career-compass`
2. `python -m venv .venv && source .venv/bin/activate` (or `.venv\Scripts\activate` on Windows)
3. Create `requirements.txt` and `pip install -r requirements.txt`
4. `python -m spacy download en_core_web_sm`
5. Open a spreadsheet — spend 2 hours building `data/job_descriptions.csv` with 30 real Sydney jobs from Seek.com.au (this is the highest-leverage task and unblocks everything else)
6. Build `data/skills_taxonomy.csv` (~1 hour — use ChatGPT to generate the initial list, then review)
7. Run `scripts/ingest_jobs.py` and verify ChromaDB has entries
8. Write a quick `test_pipeline.py` that passes "I did SQL projects at UTS with SSRS and Power BI" through all 4 modules
