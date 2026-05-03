# Resume Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a self-contained Resume Optimization feature — paste a job description, see skill gaps + keyword recommendations, then optionally generate a full roadmap.

**Architecture:** New `/api/resume-optimize` backend endpoint feeds a new `/optimize` frontend page. When the user proceeds to roadmap, a synthetic job object is injected into AppContext so the existing Roadmap page works without modification.

**Tech Stack:** FastAPI (Python), OpenAI gpt-4o-mini, React, React Router, AppContext

---

## File Map

| File | Action |
|------|--------|
| `src/gap_analyzer.py` | Add `optimize_resume()` function |
| `main.py` | Add Pydantic models + `/api/resume-optimize` endpoint |
| `frontend/src/api/client.js` | Add `resumeOptimize` call |
| `frontend/src/pages/Optimize.jsx` | **New page** |
| `frontend/src/App.jsx` | Add `/optimize` route |
| `frontend/src/pages/BrainDump.jsx` | Add "Resume Optimization" button |

---

## Task 1: Add `optimize_resume` to `src/gap_analyzer.py`

**Files:**
- Modify: `src/gap_analyzer.py`

- [ ] **Step 1: Add the prompt template and function**

Append to the bottom of `src/gap_analyzer.py` (after `analyze_gaps`):

```python
_OPTIMIZE_PROMPT_TEMPLATE = """You are a resume coach helping a student optimise their resume for a specific job.

The student currently has these skills:
{student_skills}

Here is the job description they are targeting:
{job_description}

Your tasks:
1. Identify the 3-5 most important skills or technologies mentioned in the job description that the student is missing.
2. Identify 5-8 keywords or phrases from the job description the student should add to their resume to pass ATS screening.

Respond ONLY with valid JSON in this exact format — no markdown, no explanation outside the JSON:
{{
  "missing_skills": ["skill1", "skill2", "skill3"],
  "keyword_recommendations": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
}}"""


def optimize_resume(job_description: str, student_skills: list[str]) -> dict:
    """
    Analyse a raw job description against student skills.

    Returns:
        Dict with keys: {missing_skills, keyword_recommendations}
    """
    api_key = get_secret("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    student_skills_str = ", ".join(student_skills) if student_skills else "No skills detected"

    prompt = _OPTIMIZE_PROMPT_TEMPLATE.format(
        student_skills=student_skills_str,
        job_description=job_description,
    )

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = response.choices[0].message.content
    result = _parse_response(raw_text)

    # Ensure expected keys exist even on parse failure
    result.setdefault("missing_skills", [])
    result.setdefault("keyword_recommendations", [])
    return result
```

- [ ] **Step 2: Commit**

```bash
git add src/gap_analyzer.py
git commit -m "feat: add optimize_resume function to gap_analyzer"
```

---

## Task 2: Add endpoint to `main.py`

**Files:**
- Modify: `main.py`

- [ ] **Step 1: Add Pydantic models**

After the existing `AnalyzeGapsResponse` model (around line 103), add:

```python
class ResumeOptimizeRequest(BaseModel):
    job_description: str
    student_skills: list[str]


class ResumeOptimizeResponse(BaseModel):
    missing_skills: list[str]
    keyword_recommendations: list[str]
```

- [ ] **Step 2: Add the endpoint**

Add after the existing `/api/analyze-gaps` endpoint:

```python
@app.post("/api/resume-optimize", response_model=ResumeOptimizeResponse)
async def api_resume_optimize(req: ResumeOptimizeRequest):
    """Analyse a raw job description against student skills for resume optimisation."""
    try:
        from src.gap_analyzer import optimize_resume
        result = optimize_resume(req.job_description, req.student_skills)
        return ResumeOptimizeResponse(
            missing_skills=result.get("missing_skills", []),
            keyword_recommendations=result.get("keyword_recommendations", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume optimisation failed: {e}")
```

- [ ] **Step 3: Verify backend starts without errors**

```bash
uvicorn main:app --reload
```
Expected: server starts, no import errors. Visit `http://localhost:8000/docs` — `/api/resume-optimize` should appear.

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "feat: add /api/resume-optimize endpoint"
```

---

## Task 3: Add API call to `frontend/src/api/client.js`

**Files:**
- Modify: `frontend/src/api/client.js`

- [ ] **Step 1: Add `resumeOptimize` to the `api` export object**

After the `analyzeGaps` entry (line 56-61), add:

```js
  // POST /api/resume-optimize
  resumeOptimize: (jobDescription, studentSkills) =>
    request('/api/resume-optimize', 'POST', {
      job_description: jobDescription,
      student_skills: studentSkills,
    }),
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/api/client.js
git commit -m "feat: add resumeOptimize API call"
```

---

## Task 4: Create `frontend/src/pages/Optimize.jsx`

**Files:**
- Create: `frontend/src/pages/Optimize.jsx`

- [ ] **Step 1: Create the file**

```jsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { api } from '../api/client'
import { useApp } from '../context/AppContext'
import { StepIndicator } from '../components/StepIndicator'
import { SkillBadge } from '../components/SkillBadge'

export function Optimize() {
  const navigate = useNavigate()
  const { skills, setSelectedJob, setChatContext } = useApp()
  const [jobDescription, setJobDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  // Guard: no skills means user hasn't done Step 1 yet
  if (skills.length === 0) {
    navigate('/brain-dump')
    return null
  }

  const handleAnalyse = async () => {
    if (!jobDescription.trim()) {
      setError('Please paste a job description.')
      return
    }
    if (jobDescription.trim().split(/\s+/).length < 20) {
      setError('Job description is too short. Paste the full job posting for best results.')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)
    try {
      const data = await api.resumeOptimize(jobDescription, skills)
      setResult(data)
    } catch (err) {
      setError(`Analysis failed: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateRoadmap = () => {
    setSelectedJob({
      title: 'Custom Role',
      score: 1.0,
      label: 'Custom',
      raw_description: jobDescription,
      skills_required: result?.missing_skills?.join(', ') ?? '',
    })
    setChatContext(null) // reset so ChatPanel shows fresh
    navigate('/roadmap')
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.4 }}
    >
      <div className="content-container">
        <StepIndicator currentStep={1} />

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <p
            className="text-sm font-medium tracking-widest uppercase mb-3 text-center"
            style={{ color: 'var(--accent)' }}
          >
            Resume Optimizer
          </p>
          <h1 className="page-title">Optimise for a Specific Role</h1>
          <p className="page-subtitle">
            Paste a job description to see your skill gaps and the keywords you should add to your resume.
          </p>
        </motion.div>

        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', fontWeight: 500 }}>
            Job Description
          </label>
          <textarea
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste the full job posting here..."
            style={{ minHeight: '220px', marginBottom: '12px' }}
          />
        </div>

        <div className="flex-row" style={{ gap: '10px', marginBottom: '32px' }}>
          <button
            className="primary"
            onClick={handleAnalyse}
            disabled={loading || !jobDescription.trim()}
            style={{ flex: 1 }}
          >
            {loading ? 'Analysing...' : 'Analyse My Resume'}
          </button>
          <button className="secondary" onClick={() => navigate('/brain-dump')}>
            ← Back
          </button>
        </div>

        {error && <div className="alert warning">{error}</div>}

        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <hr className="divider" />

            <h2 style={{ fontSize: '1.1rem', marginBottom: '16px', fontWeight: 600 }}>
              Missing skills
              <span className="ml-2 text-sm font-normal" style={{ color: 'var(--muted)' }}>
                {result.missing_skills.length}
              </span>
            </h2>
            {result.missing_skills.length > 0 ? (
              <div style={{ marginBottom: '32px' }}>
                {result.missing_skills.map((skill) => (
                  <SkillBadge key={skill} skill={skill} />
                ))}
              </div>
            ) : (
              <div className="alert info" style={{ marginBottom: '32px' }}>
                No major skill gaps found — your profile is a strong match!
              </div>
            )}

            <h2 style={{ fontSize: '1.1rem', marginBottom: '16px', fontWeight: 600 }}>
              Keywords to add to your resume
              <span className="ml-2 text-sm font-normal" style={{ color: 'var(--muted)' }}>
                {result.keyword_recommendations.length}
              </span>
            </h2>
            {result.keyword_recommendations.length > 0 ? (
              <div style={{ marginBottom: '32px' }}>
                {result.keyword_recommendations.map((kw) => (
                  <SkillBadge key={kw} skill={kw} />
                ))}
              </div>
            ) : (
              <div className="alert info" style={{ marginBottom: '32px' }}>
                No additional keywords identified.
              </div>
            )}

            <hr className="divider" />

            <div className="text-center">
              <button
                className="primary"
                onClick={handleGenerateRoadmap}
                style={{ padding: '12px 28px' }}
              >
                Generate Roadmap for this Job →
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/Optimize.jsx
git commit -m "feat: add Optimize page for resume gap analysis"
```

---

## Task 5: Add `/optimize` route to `frontend/src/App.jsx`

**Files:**
- Modify: `frontend/src/App.jsx`

- [ ] **Step 1: Add import and route**

Add import after the `Roadmap` import (line 9):

```js
import { Optimize } from './pages/Optimize'
```

Add route inside `<Routes>` after the `/roadmap` route (line 20):

```jsx
<Route path="/optimize" element={<Optimize />} />
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/App.jsx
git commit -m "feat: register /optimize route"
```

---

## Task 6: Add "Resume Optimization" button to `BrainDump.jsx`

**Files:**
- Modify: `frontend/src/pages/BrainDump.jsx`

- [ ] **Step 1: Add the button**

Find the "Find My Job Matches →" button block (inside the `skills.length > 0` section). Replace:

```jsx
            <div className="text-center">
              <button
                className="primary"
                onClick={() => navigate('/matches')}
                style={{ padding: '12px 28px' }}
              >
                Find My Job Matches →
              </button>
            </div>
```

With:

```jsx
            <div className="flex-row" style={{ gap: '12px', justifyContent: 'center' }}>
              <button
                className="primary"
                onClick={() => navigate('/matches')}
                style={{ padding: '12px 28px' }}
              >
                Find My Job Matches →
              </button>
              <button
                className="secondary"
                onClick={() => navigate('/optimize')}
                style={{ padding: '12px 28px' }}
              >
                Resume Optimization
              </button>
            </div>
```

- [ ] **Step 2: Verify in browser**

1. Extract skills on `/brain-dump`
2. Confirm both buttons appear side by side
3. Click "Resume Optimization" → lands on `/optimize`
4. Paste a job description → click "Analyse My Resume" → missing skills and keywords appear
5. Click "Generate Roadmap for this Job →" → `/roadmap` loads with ChatPanel
6. Complete chat → 30-day plan generates
7. Go back to `/brain-dump` → "Find My Job Matches →" still works as before (regression check)

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/BrainDump.jsx
git commit -m "feat: add Resume Optimization button to BrainDump"
```

---

## Task 7: Push feature branch

- [ ] **Push to remote**

```bash
git push origin feature/new-features
```
