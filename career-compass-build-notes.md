# Career Compass — Build Notes

> A reference doc for the team. Open this when something breaks or before you start each phase.
> Ordered by when you will actually hit each issue.

---

## 1. Before You Write a Line of Code

### Install order matters
`sentence-transformers` pins specific versions of `torch`, `transformers`, and `accelerate`. If you install these packages separately first, you will get silent version conflicts that cause cryptic import errors later.

**Rule:** Install `sentence-transformers` first and let it pull its own dependencies. Then install everything else.

```
# requirements.txt — install in this order conceptually
sentence-transformers==2.7.0
chromadb==0.4.24
spacy==3.7.4
anthropic==0.25.0
streamlit==1.33.0
pandas==2.2.2
python-dotenv==1.0.1
numpy==1.26.4
```

Pin every version after you confirm it works. `chromadb`, `sentence-transformers`, and `anthropic` all ship breaking changes between minor versions.

### Use Python 3.11.x — not 3.12
ChromaDB has known issues with Python 3.12 in several releases. Stick to `3.11.x`. Set this in your virtual environment and document it in the README so every teammate uses the same version.

### CSV editing rule for the whole team
If anyone opens `job_descriptions.csv` or `skills_taxonomy.csv` in **Excel**, Excel will silently re-save it as Windows-1252 encoding. `pandas.read_csv()` will then break with a `UnicodeDecodeError` for anyone on Mac or Linux.

**Rule:** Edit CSVs in VS Code, Google Sheets (export as UTF-8), or any text editor. Never save from Excel. If you must use Excel, save as "CSV UTF-8 (Comma delimited)."

### Data CSV is one person's job
`job_descriptions.csv` and `skills_taxonomy.csv` are the foundation everything else depends on. If two people add rows simultaneously, you will get git merge conflicts on every single line.

**Rule:** Assign one person to build both CSVs. Everyone else builds the code modules. Merge the CSVs once they are stable (~Day 3). This is the highest-leverage coordination decision you can make.

---

## 2. Phase 1 — Data & Ingestion

### spaCy's NER will not find your skills
This is the most important thing in this document. `en_core_web_sm`'s built-in NER model is trained to recognise entities like people (PERSON), countries (GPE), and organisations (ORG). It will not recognise "Python", "dbt", "Power BI", "Fabric", or "SSRS" as named entities — they will be silently ignored.

The MVP says "spaCy NER" but what you actually need is `spaCy.PhraseMatcher`. This matches your taxonomy terms directly against the tokenised text.

```python
# extractor.py — correct approach
import spacy
from spacy.matcher import PhraseMatcher

nlp = spacy.load("en_core_web_sm")
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")  # LOWER = case-insensitive

# Add every skill + alias from taxonomy as a pattern
patterns = [nlp.make_doc(skill) for skill in all_skill_terms]
matcher.add("SKILLS", patterns)

def extract_skills(text: str) -> list[str]:
    doc = nlp(text)
    matches = matcher(doc)
    found = set()
    for match_id, start, end in matches:
        found.add(doc[start:end].text.lower())
    return list(found)
```

The `attr="LOWER"` flag is critical — without it, "python" and "Python" are treated as different tokens.

### Taxonomy alias design
Your `skills_taxonomy.csv` aliases column needs to cover all of these variations or extraction quality will be poor:

- **Case variants:** `SQL`, `sql`, `Sql` — handled by `attr="LOWER"` above
- **Compound terms:** `machine learning`, `machine-learning`, `ML` — add all three as separate aliases
- **Common abbreviations:** `NLP`, `natural language processing`; `BI`, `business intelligence`
- **Tool name variations:** `Power BI`, `PowerBI`, `power bi`; `dbt`, `DBT`

Build your taxonomy in a spreadsheet with a `skill_name` (canonical) and `aliases` (pipe-separated) column. Write a loader that explodes aliases into individual patterns.

### ChromaDB duplicate guard in ingest_jobs.py
If you run `ingest_jobs.py` more than once (you will), you will add duplicate entries to ChromaDB. Cosine similarity scores will become meaningless and you will get duplicate results.

Add this guard at the start of your ingest script:

```python
collection = client.get_or_create_collection("jobs")
if collection.count() > 0:
    print(f"Collection already has {collection.count()} entries. Delete chroma_db/ to re-ingest.")
    exit()
```

### What to embed — a decision you need to make now
The pipeline embeds the student's extracted skill list and compares it against job vectors. For this comparison to be valid, **both sides must be embedded from the same type of text.**

You have two options:

| Option | Student vector | Job vector | Trade-off |
|--------|---------------|------------|-----------|
| **A — Skills only** | Join extracted skills as a string | Join `skills_required` field as a string | Vectors are aligned. Quality depends entirely on extraction quality. If taxonomy misses skills, the vector is incomplete. |
| **B — Full text** | Embed raw brain dump | Embed `raw_description` field | Captures semantics taxonomy misses. Vectors may be in slightly different distributions. |

**Recommendation: Option A for the MVP.** It is simpler and the mismatch risk is lower. But document the decision — your NLP lecturer will ask about it.

Whichever you choose: ChromaDB expects a Python `list`, not a numpy array. Call `.tolist()` on the embedding before storing:

```python
embedding = model.encode(text).tolist()  # not .encode(text) alone
```

---

## 3. Phase 2 — NLP Pipeline

### Negation blind spot
The extractor will match "I have **no** experience in Python" and return `["python"]` as a skill. spaCy's PhraseMatcher does not check context.

For the MVP, accept this limitation and document it. If you want to handle it: check for a negation dependency (`token.dep_ == "neg"`) within a 3-token window of each match and discard those matches. Not worth implementing for a demo unless your lecturer specifically raises it.

### Cosine distance vs cosine similarity — ChromaDB gotcha
ChromaDB's default `query_embeddings()` returns **distance**, not similarity. With cosine distance: `0 = identical, 2 = opposite`.

If you display "83% match" to the user, you need to convert:

```python
# results from collection.query(...)
distances = results["distances"][0]  # e.g. [0.17, 0.34, 0.51]
similarities = [1 - d for d in distances]  # e.g. [0.83, 0.66, 0.49]
```

Without this conversion, your similarity scores will be backwards — a distance of 0.17 (very similar) would display as 17% match.

### The 0.85 similarity threshold is wrong for this model
The `Additional Context.md` file states: "If the score is >0.85, the tool confirms alignment." This threshold is based on sentence-pair similarity benchmarks, not document matching.

In practice, with `all-MiniLM-L6-v2` comparing a student brain dump against job descriptions, **meaningful similarities typically fall in the 0.35–0.65 range**. A score of 0.65 is a strong match. A score above 0.80 between two different documents is unusual and may indicate the job description is nearly identical to the input.

Do not hard-code 0.85 as a pass/fail threshold. Instead, display the raw score and add a label:
- `>= 0.60` → "Strong match"
- `0.40–0.59` → "Moderate match"
- `< 0.40` → "Weak match"

Calibrate these thresholds after testing with real brain dumps on your actual dataset.

### Prompt design for gap_analyzer.py
The MVP doesn't specify the prompt. This matters more than it looks — if Claude returns free-form markdown and you try to parse it as JSON, your app will crash.

**Use structured JSON output.** Here is a prompt template that works reliably with Claude Haiku:

```python
PROMPT = """You are a career coach. A student has the following skills:
{student_skills}

They are being matched to this job role:
Job Title: {job_title}
Required Skills: {job_skills}
Full Description: {job_description}

Identify the 2-3 most important skills the student is missing for this role.
Then write a 30-day learning plan to close those gaps.

Respond ONLY with valid JSON in this exact format:
{{
  "missing_skills": ["skill1", "skill2", "skill3"],
  "week1": "What to focus on and why",
  "week2": "What to focus on and why",
  "week3": "What to focus on and why",
  "week4": "What to focus on and why"
}}
"""
```

Parse defensively — Claude sometimes wraps JSON in markdown code blocks:

```python
import json, re

def parse_gap_response(text: str) -> dict:
    # Strip markdown code fences if present
    text = re.sub(r"```(?:json)?", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback: return raw text as unstructured response
        return {"missing_skills": [], "week1": text, "week2": "", "week3": "", "week4": ""}
```

### Add an explicit API key check at startup
If `ANTHROPIC_API_KEY` is missing, the `anthropic` client raises a generic authentication error that is hard to debug. Add this to `app.py`:

```python
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY", None)
if not api_key:
    st.error("ANTHROPIC_API_KEY not found. Add it to your .env file or Streamlit Secrets.")
    st.stop()
```

---

## 4. Phase 3 — Streamlit UI

### Guard every page against missing session state
In a multi-page Streamlit app, if a user navigates directly to page 2 or refreshes the page, `st.session_state` will be empty and your app will throw a `KeyError`.

Add this at the top of every page except page 1:

```python
# pages/2_Job_Matches.py
if "extracted_skills" not in st.session_state or not st.session_state["extracted_skills"]:
    st.warning("Please complete Step 1 first.")
    st.switch_page("pages/1_Brain_Dump.py")
    st.stop()
```

```python
# pages/3_My_Roadmap.py
if "top_matches" not in st.session_state or not st.session_state["top_matches"]:
    st.warning("Please complete Step 2 first.")
    st.switch_page("pages/2_Job_Matches.py")
    st.stop()
```

### @st.cache_resource vs @st.cache_data
These are different and using the wrong one will cause bugs:

| Decorator | What it caches | Use for |
|-----------|---------------|---------|
| `@st.cache_resource` | One instance shared across ALL sessions | Model loading: `SentenceTransformer`, `spacy.load()`, ChromaDB client |
| `@st.cache_data` | Separate cache per unique set of arguments | Data processing: embedding a specific text, querying for a specific input |

**Model loading must use `@st.cache_resource`.** If you use `@st.cache_data` on a SentenceTransformer, Streamlit will try to serialise the model object and fail with a cryptic pickle error.

```python
# embedder.py
@st.cache_resource
def load_model():
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

@st.cache_resource
def load_spacy():
    return spacy.load("en_core_web_sm")

@st.cache_resource
def load_chroma():
    client = chromadb.PersistentClient(path="data/chroma_db")
    return client.get_collection("jobs")
```

### Put heavy processing inside button callbacks
Streamlit re-runs the entire script on every user interaction (typing, clicking, selecting). If your NLP pipeline runs at the top level of the script, it will re-run every time the user types a character.

```python
# WRONG — runs on every keystroke
brain_dump = st.text_area("Paste your experience here")
skills = extract_skills(brain_dump)  # runs constantly

# CORRECT — runs only when button is clicked
brain_dump = st.text_area("Paste your experience here")
if st.button("Extract My Skills"):
    skills = extract_skills(brain_dump)
    st.session_state["extracted_skills"] = skills
```

### Add a spinner for the LLM call
The gap analysis API call takes 2–5 seconds. Without a loading indicator, the UI looks frozen and users click the button again (triggering another API call).

```python
with st.spinner("Generating your personalised roadmap..."):
    gap_result = analyze_gaps(
        st.session_state["top_matches"][0],
        st.session_state["extracted_skills"]
    )
st.session_state["gap_analysis"] = gap_result
```

---

## 5. Phase 4 — Deployment

### spaCy model in requirements.txt for Streamlit Cloud
`packages.txt` is for Linux apt packages (e.g., system libraries). spaCy models are Python packages and go in `requirements.txt`.

The model name `en_core_web_sm` is not a valid pip package name. Use the direct download URL:

```
# requirements.txt
en-core-web-sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.4/en_core_web_sm-3.7.4-py3-none-any.whl
```

Match the version to your local spaCy version. Find it with: `python -m spacy info`

### ChromaDB persistence on Streamlit Cloud
Streamlit Cloud has an ephemeral filesystem — any files written at runtime are wiped on restart. Your `data/chroma_db/` folder will be gone after every dyno sleep.

**Simplest fix: commit `data/chroma_db/` to git.** At 50 job descriptions, the ChromaDB files will be around 1–3MB total. Remove `data/chroma_db/` from `.gitignore` and commit after running `ingest_jobs.py` locally.

If you prefer to re-ingest on startup instead, add this to `app.py`:

```python
@st.cache_resource
def ensure_chroma_populated():
    client = chromadb.PersistentClient(path="data/chroma_db")
    try:
        collection = client.get_collection("jobs")
        if collection.count() == 0:
            raise ValueError("Empty")
    except:
        with st.spinner("Setting up job database (first run only)..."):
            from scripts.ingest_jobs import run_ingest
            run_ingest()
    return client
```

### API key helper for local vs cloud
Locally you use `.env` + `python-dotenv`. On Streamlit Cloud you use `st.secrets`. Write one helper so you do not have to change code between environments:

```python
# src/config.py
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_secret(key: str) -> str:
    try:
        return st.secrets[key]
    except Exception:
        val = os.getenv(key)
        if not val:
            raise ValueError(f"Secret '{key}' not found in st.secrets or .env")
        return val
```

### Pre-warm before demo day
On Streamlit Cloud, first load after a cold start downloads the `sentence-transformers` model (~90MB) and `torch`. This can take 30–60 seconds. During this time the UI shows a blank loading screen.

**Rule:** Open the deployed app 10 minutes before any demo or presentation. Keep the tab open so it does not sleep.

---

## 6. NLP Academic Gaps

Your lecturer will likely ask these questions. Be ready with answers, or ideally build the answers into the project.

### You need evaluation metrics
There are no evaluation metrics defined anywhere in the current plan. Without them, you cannot claim your skill extractor "works" — you can only say it runs.

**Minimum to add before submission:**

1. Pick 5 representative brain dumps (different backgrounds — data analyst, developer, HR person pivoting to data, etc.)
2. Manually label the expected skills for each one
3. Run your extractor and compute precision and recall:
   - **Precision** = skills correctly extracted / all skills extracted (measures false positives)
   - **Recall** = skills correctly extracted / all expected skills (measures false negatives)
4. Report these numbers in your report. Even if the numbers are not great, showing you measured is what matters.

### You need a TF-IDF baseline
For an NLP course, using semantic embeddings requires justification. The justification is: "semantic embeddings outperform TF-IDF for this task."

Add a simple comparison using `sklearn`:

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# TF-IDF baseline matcher
def tfidf_match(student_text, job_descriptions):
    corpus = [student_text] + job_descriptions
    tfidf = TfidfVectorizer()
    matrix = tfidf.fit_transform(corpus)
    scores = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
    return scores
```

Show 2–3 examples where TF-IDF returns a wrong match but semantic embeddings return the right one. This demonstrates you understand why the technique was chosen — not just that it was chosen.

### Impact Translation is missing from the MVP
`Additional Context.md` lists "Impact Translation" as one of three core goals: rewriting technical university tasks into business outcome stories that recruiters value. This feature does not appear anywhere in the MVP.

Confirm with your team: is this intentional (cut for scope) or was it forgotten? If the assessor expects it, it needs to be added. If it is cut, note it explicitly in your report as "out of scope for MVP."

---

## 7. Module Interface Contract

Agree on these function signatures **before** splitting the work. Mismatched interfaces are the most common source of integration pain in group projects.

```python
# src/extractor.py
def extract_skills(text: str) -> list[str]:
    """
    Input:  raw brain dump text (any length)
    Output: list of canonical skill names from taxonomy (deduplicated, lowercased)
    Example output: ["python", "sql", "power bi", "dbt"]
    """

# src/embedder.py
def embed(text: str) -> list[float]:
    """
    Input:  any text string (skill list joined by ', ' or raw text)
    Output: 384-dimensional embedding as a Python list (not numpy array)
    Note:   model is cached with @st.cache_resource — call load_model() separately
    """

# src/matcher.py
def match_jobs(student_vector: list[float], top_k: int = 3) -> list[dict]:
    """
    Input:  student embedding vector, number of results to return
    Output: list of dicts, each with keys:
            { "title": str, "score": float, "skills_required": str, "raw_description": str }
    Note:   score is cosine SIMILARITY (0–1), not distance
    """

# src/gap_analyzer.py
def analyze_gaps(job: dict, student_skills: list[str]) -> dict:
    """
    Input:  job dict from matcher output, student skill list from extractor
    Output: dict with keys:
            { "missing_skills": list[str], "week1": str, "week2": str, "week3": str, "week4": str }
    Note:   caches result in st.session_state to avoid repeat API calls
    """
```

Write these signatures as empty stubs on Day 1 so the team can build against them in parallel without blocking each other.

---

## Quick Reference — Most Likely to Bite You

| # | Issue | When | Fix |
|---|-------|------|-----|
| 1 | spaCy NER finds no skills | Day 4 | Use PhraseMatcher, not NER |
| 2 | Session state KeyError on page nav | Day 8 | Guard every page with st.switch_page |
| 3 | ChromaDB scores backwards | Day 5 | Convert distance → similarity with `1 - d` |
| 4 | Duplicate entries in ChromaDB | Day 3 | Add count() guard in ingest_jobs.py |
| 5 | Model loading crashes with cache_data | Day 8 | Use @st.cache_resource for models |
| 6 | spaCy model 404 on Streamlit Cloud | Day 12 | Use full pip URL in requirements.txt |
| 7 | App frozen during LLM call | Day 9 | Wrap in st.spinner() |
| 8 | CSV encoding error on Mac/Linux | Day 1 | Never save CSVs from Excel |
| 9 | ChromaDB gone after Streamlit restart | Day 12 | Commit chroma_db/ to git |
| 10 | 0.85 similarity threshold never met | Day 5 | Use 0.60 as strong match threshold |
