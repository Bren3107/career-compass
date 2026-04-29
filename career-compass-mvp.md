# MVP Plan: The Career Compass

> **Context:** Students in the 2026 Sydney market have real skills but cannot articulate them in ways that match job descriptions. They write vague "brain dumps" and don't know which specific skills they're missing to land specific roles. This NLP tool solves the translation problem: unstructured student life → market-aligned career roadmap.

---

## Project Overview

**The Career Compass** is a lightweight, end-to-end NLP web app (Python + Streamlit) that accepts a student's unstructured "brain dump" of life experience, extracts latent skills using NLP, semantically matches those skills against a curated dataset of 50 Sydney job descriptions, identifies the 2–3 skill gaps preventing a "match," and generates a personalised 30-day learning roadmap.

**MVP Complete =** A student can paste their brain dump → see their Top 3 job matches with similarity scores → see the exact skills they're missing → receive a 30-day plan to close the gap. Runnable locally, deployable to Streamlit Cloud.

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
| **UI** | Streamlit | Pure Python, zero HTML/CSS, multi-page support, 1-command deploy | FastAPI + React (overkill for MVP), Gradio (less flexible layout) |
| **Embedding Model** | `sentence-transformers/all-MiniLM-L6-v2` | 384-dim, ~14k sentences/sec on CPU, MTEB ~56, community standard for semantic search | `all-mpnet-base-v2` (3.5x slower, marginal accuracy gain), OpenAI embeddings (API cost + latency) |
| **Vector Store** | ChromaDB | Auto-persists (DuckDB+Parquet), metadata filtering, zero config for <10k docs | FAISS (no built-in persistence, same speed at 50 docs, higher complexity), Pinecone (cloud cost) |
| **Skill Extraction** | spaCy + skills taxonomy CSV | No training data needed, fast, deterministic, easy to extend taxonomy | Custom NER model (needs 500+ labeled examples), Llama-3-8B locally (8GB+ VRAM, slow) |
| **Gap Generation LLM** | Claude Haiku API (`claude-haiku-4-5-20251001`) | ~$0.001/request, fast, reliable, structured output, no local GPU needed | GPT-4o-mini (equivalent cost, second choice), Llama local (slow, fragile setup) |
| **Backend** | None (Streamlit imports `src/` directly) | Eliminates HTTP layer, CORS, Docker complexity for MVP | FastAPI (adds 2 days setup, zero MVP benefit — add in Phase 2 if API is needed) |
| **Data Storage** | CSV + ChromaDB persistence | No database server to manage; job data is static for MVP | SQLite (overcomplicated), PostgreSQL (far too heavy) |
| **Python Version** | 3.11+ | Required by latest sentence-transformers and ChromaDB | — |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT UI (3 pages)                    │
│  Page 1: Brain Dump Input                                    │
│  Page 2: Job Matches + Similarity Scores                     │
│  Page 3: Skill Gap + 30-Day Roadmap                          │
└────────────────────────┬────────────────────────────────────┘
                         │ direct Python imports
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     src/ NLP PIPELINE                        │
│                                                              │
│  brain_dump.txt                                              │
│       │                                                      │
│       ▼                                                      │
│  [extractor.py]  ──── skills_taxonomy.csv                   │
│  spaCy POS/NER + keyword matching                            │
│  Output: ["SQL", "SSRS", "ERP", "Python"]                   │
│       │                                                      │
│       ▼                                                      │
│  [embedder.py]                                               │
│  all-MiniLM-L6-v2 → 384-dim student vector                  │
│       │                                                      │
│       ▼                                                      │
│  [matcher.py]  ◄──── ChromaDB (job embeddings)              │
│  Cosine similarity → Top 3 jobs + scores                     │
│       │                                                      │
│       ▼                                                      │
│  [gap_analyzer.py]                                           │
│  RAG: retrieve job requirements                              │
│  Prompt Claude Haiku API → gap list + 30-day plan            │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     DATA LAYER                               │
│  data/job_descriptions.csv   (30-50 curated Sydney jobs)    │
│  data/skills_taxonomy.csv    (~200 skills + aliases)        │
│  data/chroma_db/             (persisted ChromaDB vectors)   │
└─────────────────────────────────────────────────────────────┘
```

**Key Data Flow:**
1. User pastes brain dump text → `extractor.py` returns skill list
2. Skill list is joined into a single text → `embedder.py` returns 384-dim vector
3. Vector is queried against ChromaDB → returns Top 3 job matches with metadata
4. Top match's raw requirements text + student's skill list → `gap_analyzer.py`
5. Claude Haiku returns structured gap analysis + 30-day roadmap
6. Results are stored in `st.session_state` and displayed across pages

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
├── app.py                      # Streamlit landing page + navigation
├── pages/
│   ├── 1_Brain_Dump.py         # Text area input + skill extraction trigger
│   ├── 2_Job_Matches.py        # Top 3 matches with score visualisation
│   └── 3_My_Roadmap.py         # Skill gap display + 30-day learning plan
├── src/
│   ├── __init__.py
│   ├── extractor.py            # spaCy + taxonomy skill extraction
│   ├── embedder.py             # all-MiniLM-L6-v2 wrapper (cached with @st.cache_resource)
│   ├── matcher.py              # ChromaDB query + cosine similarity scoring
│   └── gap_analyzer.py         # RAG context builder + Claude Haiku API call
├── data/
│   ├── job_descriptions.csv    # 30-50 curated Sydney job descriptions
│   ├── skills_taxonomy.csv     # ~200 skills with categories + aliases
│   └── chroma_db/              # ChromaDB persisted vector store (git-ignored)
├── scripts/
│   └── ingest_jobs.py          # One-time: embed all jobs and store in ChromaDB
├── .env.example                # ANTHROPIC_API_KEY=your_key_here
├── requirements.txt
└── README.md
```

---

## Implementation Roadmap

### Phase 1 — Foundation (Days 1–3)
- [ ] Create project directory + virtual environment (`python -m venv .venv`)
- [ ] Write `requirements.txt` (streamlit, sentence-transformers, chromadb, spacy, anthropic, python-dotenv, pandas)
- [ ] Download spaCy model: `python -m spacy download en_core_web_sm`
- [ ] Build `data/job_descriptions.csv` with 30–50 Sydney jobs (manual curation from Seek.com.au/LinkedIn — target roles: BI Engineer, Data Analyst, ML Engineer, Data Engineer, AI UX Designer, Business Analyst)
- [ ] Build `data/skills_taxonomy.csv` with ~200 skills across categories (SQL, Python, dbt, Fabric, Tableau, Power BI, Azure, AWS, FastAPI, etc.)
- [ ] Write and run `scripts/ingest_jobs.py` to embed all jobs and persist ChromaDB
- [ ] Verify ChromaDB collection is populated with `collection.count()`

### Phase 2 — Core NLP Pipeline (Days 4–7)
- [ ] `src/extractor.py`: load spaCy `en_core_web_sm`, load taxonomy CSV, match tokens against aliases → return deduplicated skill list
- [ ] `src/embedder.py`: load `all-MiniLM-L6-v2` with `@st.cache_resource`, expose `embed(text: str) -> np.ndarray`
- [ ] `src/matcher.py`: query ChromaDB with student vector, return top-k results with `{title, score, skills_required, raw_description}`
- [ ] `src/gap_analyzer.py`: build RAG prompt (job requirements + student skills), call `anthropic.messages.create()` with Claude Haiku, parse response for `missing_skills` and `learning_plan`
- [ ] Manual test of full pipeline in a Jupyter notebook or `scripts/test_pipeline.py`

### Phase 3 — Streamlit UI (Days 8–10)
- [ ] `app.py`: landing page with project description and "Start" button
- [ ] `pages/1_Brain_Dump.py`: multi-line text area, submit button → calls `extractor.py` → shows extracted skill tags → stores in `session_state` → "Find My Matches" button
- [ ] `pages/2_Job_Matches.py`: reads session state → calls `matcher.py` → displays Top 3 job cards with role title, similarity score (progress bar, e.g. "83% match"), required skills list → "Generate My Roadmap" button
- [ ] `pages/3_My_Roadmap.py`: reads session state → calls `gap_analyzer.py` → displays missing skills as coloured tags → displays 30-day plan (Week 1/2/3/4 breakdown) → "Download Plan" button (text copy)

### Phase 4 — Polish & Demo Prep (Days 11–14)
- [ ] Add pre-filled sample brain dump (the one from the brief: "I did a project on SQL at UTS...") as placeholder text
- [ ] Add `@st.cache_resource` to model loading so re-runs are fast
- [ ] Test with 5 different student profiles (data analyst, software dev, HR background pivoting to data, etc.)
- [ ] Handle edge cases: empty brain dump, no skills detected, ChromaDB not yet ingested
- [ ] Deploy to Streamlit Community Cloud (connect GitHub repo, add `ANTHROPIC_API_KEY` to Streamlit Secrets)
- [ ] Add ChromaDB re-ingest on startup if `chroma_db/` not found (for Streamlit Cloud ephemeral filesystem)

---

## Key Technical Decisions & Trade-offs

1. **No FastAPI for MVP.** Streamlit imports `src/` modules directly — no HTTP overhead, no CORS setup, no Docker. FastAPI adds ~2 days of setup with zero user-visible benefit at MVP stage. Add it in Phase 2 only if you need a public API.

2. **ChromaDB over FAISS.** At 50 docs, speed is identical. ChromaDB auto-persists (DuckDB+Parquet), supports metadata filtering (e.g., "only Junior roles"), and requires zero manual serialization. FAISS would require writing `faiss.write_index()` and `faiss.read_index()` boilerplate.

3. **Skills taxonomy CSV over custom NER model.** Training a custom spaCy NER model requires 500+ annotated examples and a training loop. A taxonomy CSV can be built in a few hours and extended incrementally. This is the right trade-off for a university project timeline.

4. **Hosted LLM (Claude Haiku) for gap generation.** Running Llama-3-8B locally requires 8GB+ VRAM or is unusably slow on CPU. Claude Haiku costs ~$0.001/request — essentially free for demo usage. This also makes Streamlit Cloud deployment trivial (no GPU, no model download).

5. **Static curated dataset.** Live job scraping from Seek/LinkedIn introduces web scraping complexity, rate limiting, and legal considerations. 30–50 manually curated jobs is sufficient for a compelling demo and removes all data pipeline risk.

6. **Streamlit `session_state` as the "database."** User data is ephemeral per session — no database server needed. Only the job description embeddings (ChromaDB) need to persist.

---

## What Is Explicitly Out of Scope for MVP

- **PDF resume upload** — plain text brain dump first; PDF parsing (PyMuPDF/pdfplumber) adds complexity without changing the NLP pipeline
- **User accounts / authentication** — session state is sufficient for a demo
- **Real-time job scraping** — static curated CSV is faster and safer to build
- **Email delivery or PDF export** — copy-paste is fine for MVP
- **Salary data integration** — interesting but not part of the core value proposition
- **FastAPI backend** — direct module imports are cleaner for MVP
- **Custom NER model training** — taxonomy CSV achieves the same result faster
- **Multiple Australian cities** — Sydney only for MVP focus
- **Mobile-responsive design** — Streamlit handles basic responsiveness; no custom CSS needed yet

---

## Open Questions & Risks

| # | Question / Risk | Mitigation |
|---|----------------|------------|
| 1 | **Streamlit Cloud ephemeral filesystem** — ChromaDB files may be lost on dyno restart | Add logic in `scripts/ingest_jobs.py` to re-ingest if `chroma_db/` is empty; or commit the pre-built ChromaDB files to git (small at 50 docs) |
| 2 | **spaCy model download on Streamlit Cloud** | Add `packages.txt` with `en_core_web_sm` or download in `app.py` startup |
| 3 | **Claude API key management** | Use `.env` locally, `st.secrets` on Streamlit Cloud; provide `.env.example` |
| 4 | **Skill extraction quality** — taxonomy may miss domain-specific tools | Start with 200 skills; add missed ones after testing with 5 brain dumps |
| 5 | **Match quality** — cosine similarity may return irrelevant matches for very short brain dumps | Add minimum word count validation (>50 words) and display a confidence warning for low scores (<0.5) |
| 6 | **API rate limits** — Claude Haiku is fast but has tier limits | For demo use, Tier 1 limits are fine; cache `gap_analyzer` results in `session_state` so repeated page visits don't re-call the API |

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
