# Career Compass — Claude Code Instructions

## Project Reference Files

| File | Purpose |
|------|---------|
| `career-compass-mvp.md` | Feature spec, tech stack decisions, project structure, implementation roadmap |
| `career-compass-build-notes.md` | Build-time gotchas, known failure points, code patterns to use |

---

## When to Check the Build Notes

Read `career-compass-build-notes.md` before:

- Writing or editing anything in `src/` (extractor, embedder, matcher, gap_analyzer)
- Writing or editing anything in `pages/`
- Writing or editing `scripts/ingest_jobs.py`
- Writing `requirements.txt` or touching dependencies
- Any deployment-related work (Streamlit Cloud, secrets, ChromaDB persistence)

The build notes exist because the MVP plan has several silent failure points that look correct on paper but break at runtime. Do not skip this.

---

## Hard Rules — Non-Negotiable

These are derived from the build notes. Apply them without being asked:

**Skill Extraction**
- Use `spacy.matcher.PhraseMatcher` with `attr="LOWER"` — NOT spaCy's built-in NER
- NER will find zero tech skills silently. PhraseMatcher is the correct approach.

**Embeddings**
- Always call `.tolist()` on numpy embeddings before passing to ChromaDB
- Use `@st.cache_resource` for model loading (SentenceTransformer, spaCy, ChromaDB client)
- Never use `@st.cache_data` on model objects — it will fail with a pickle error

**ChromaDB**
- Convert distance to similarity: `score = 1 - distance` before displaying to user
- Add a `collection.count()` guard in `ingest_jobs.py` to prevent duplicate ingestion
- Do not gitignore `data/chroma_db/` — commit it so Streamlit Cloud has it on cold start

**Streamlit**
- Every page except page 1 must guard against missing session state and call `st.switch_page()` if keys are absent
- Put all NLP pipeline calls inside `if st.button(...)` blocks, not at the top level of the script
- Wrap the gap analyzer API call in `st.spinner()`

**Claude Haiku (gap_analyzer)**
- Request JSON output explicitly in the prompt
- Strip markdown code fences before `json.loads()` — Claude sometimes wraps JSON in ```json blocks
- Always wrap the parse in try/except with a fallback

**API Key**
- Use the `get_secret()` helper from `src/config.py` — it tries `st.secrets` first, then `.env`
- Add an explicit key check at `app.py` startup with `st.stop()` if missing

**Dependencies**
- Python 3.11.x only — ChromaDB has 3.12 issues
- Install `sentence-transformers` first, then everything else
- spaCy model in `requirements.txt` as a pip URL, not in `packages.txt`

**Similarity Thresholds**
- Do NOT use 0.85 as a match threshold — meaningful scores for this task are 0.35–0.65
- Label scores as: ≥0.60 Strong, 0.40–0.59 Moderate, <0.40 Weak

---

## Module Interface Contract

These signatures are locked. Do not change them without confirming with the team:

```python
# src/extractor.py
def extract_skills(text: str) -> list[str]: ...
# returns canonical skill names, deduplicated, lowercased

# src/embedder.py
def embed(text: str) -> list[float]: ...
# returns 384-dim vector as Python list (not numpy array)

# src/matcher.py
def match_jobs(student_vector: list[float], top_k: int = 3) -> list[dict]: ...
# returns list of {title, score, skills_required, raw_description}
# score is cosine SIMILARITY (0–1), not distance

# src/gap_analyzer.py
def analyze_gaps(job: dict, student_skills: list[str]) -> dict: ...
# returns {missing_skills, week1, week2, week3, week4}
```

---

## Tech Stack (from MVP)

- UI: Streamlit (multi-page)
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2`
- Vector store: ChromaDB (persistent, local)
- Skill extraction: spaCy `en_core_web_sm` + PhraseMatcher + `data/skills_taxonomy.csv`
- Gap analysis: Claude Haiku API (`claude-haiku-4-5-20251001`)
- No FastAPI backend — Streamlit imports `src/` directly
- Python 3.11.x

---

## Project Structure (target)

```
career-compass/
├── CLAUDE.md
├── app.py
├── pages/
│   ├── 1_Brain_Dump.py
│   ├── 2_Job_Matches.py
│   └── 3_My_Roadmap.py
├── src/
│   ├── __init__.py
│   ├── config.py           # get_secret() helper
│   ├── extractor.py
│   ├── embedder.py
│   ├── matcher.py
│   └── gap_analyzer.py
├── data/
│   ├── job_descriptions.csv
│   ├── skills_taxonomy.csv
│   └── chroma_db/          # committed to git — do not gitignore
├── scripts/
│   └── ingest_jobs.py
├── .env.example
└── requirements.txt
```
