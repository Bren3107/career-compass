# Resume Optimization Feature — Design Spec
**Date:** 2026-05-03

## Overview

A new, self-contained addition to Career Compass that lets users paste a specific job description and instantly see their skill gaps and missing keywords against their extracted resume. Existing Step 1 → 2 → 3 flow is completely untouched.

---

## User Flow

```
Step 1 (BrainDump) — skills extracted
  └─ "Resume Optimization" button (next to "Find My Job Matches")
       │
       ▼
  /optimize page
  ├─ Textarea: paste job description
  ├─ "Analyse" button
  ├─ Results:
  │    ├─ Missing skills (badge list)
  │    └─ Keywords to add to your resume (badge list)
  └─ "Generate Roadmap for this job →" button
       │
       ▼
  /roadmap page (existing)
  ├─ ChatPanel — 4 questions as normal
  └─ 30-day plan generated using the pasted job description
```

---

## What Does NOT Change

- `/` (BrainDump), `/matches`, `/roadmap` — no modifications
- AppContext shape — no new fields
- Existing API endpoints — untouched
- Routing guard pattern — reused as-is

---

## Frontend

### New file: `frontend/src/pages/Optimize.jsx`

**State:**
- `jobDescription` — textarea input
- `loading` — bool
- `error` — string
- `result` — `{ missing_skills: string[], keyword_recommendations: string[] } | null`

**Guard:** If `skills.length === 0`, redirect to `/` (same pattern as Roadmap/Matches pages).

**On "Analyse":** POST `/api/resume-optimize` with `{ job_description, student_skills: skills }`.

**On "Generate Roadmap":** Set `selectedJob` in AppContext to a synthetic object:
```js
{
  title: "Custom Role",
  score: 1.0,
  label: "Custom",
  raw_description: jobDescription,
  skills_required: []
}
```
Then navigate to `/roadmap`. The Roadmap page handles the rest (ChatPanel → generate → 30-day plan).

### Changes to existing files

**`BrainDump.jsx`** — add one button after "Find My Job Matches":
```jsx
<button className="secondary" onClick={() => navigate('/optimize')}>
  Resume Optimization
</button>
```
Only shown when `skills.length > 0` (already inside that conditional block).

**`frontend/src/App.jsx` (or router file)** — add one new route:
```jsx
<Route path="/optimize" element={<Optimize />} />
```

**`frontend/src/api/client.js`** — add one new API call:
```js
resumeOptimize: (jobDescription, studentSkills) =>
  request('/api/resume-optimize', 'POST', {
    job_description: jobDescription,
    student_skills: studentSkills,
  })
```

---

## Backend

### New function: `src/gap_analyzer.py`

```python
def optimize_resume(job_description: str, student_skills: list[str]) -> dict:
    # Returns { missing_skills, keyword_recommendations }
```

Prompt instructs the LLM to:
1. Identify skills/technologies in the job description the student doesn't have → `missing_skills`
2. Identify important keywords/phrases from the JD the student should add to their resume → `keyword_recommendations`

Returns JSON. Same stripping/parsing pattern as `analyze_gaps`.

### New endpoint: `main.py`

```python
POST /api/resume-optimize
Request:  { job_description: str, student_skills: list[str] }
Response: { missing_skills: list[str], keyword_recommendations: list[str] }
```

---

## Files Modified / Created

| File | Change |
|------|--------|
| `frontend/src/pages/Optimize.jsx` | **New** |
| `frontend/src/pages/BrainDump.jsx` | +1 button |
| `frontend/src/App.jsx` | +1 route |
| `frontend/src/api/client.js` | +1 API call |
| `src/gap_analyzer.py` | +1 function |
| `main.py` | +1 endpoint + Pydantic models |

---

## Verification

1. Extract skills on Step 1 → "Resume Optimization" button appears
2. Navigate to `/optimize` → redirects to `/` if no skills (guard works)
3. Paste a job description → click Analyse → missing skills and keywords appear
4. Click "Generate Roadmap" → navigates to `/roadmap` with synthetic job set
5. ChatPanel appears, answer 4 questions → 30-day plan generates correctly
6. Existing "Find My Job Matches" flow still works end-to-end (regression check)
