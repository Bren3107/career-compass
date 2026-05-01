# Job Selection, Home Navigation, and Smart Matching — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add home navigation, job selection with visual feedback, and weak-match warnings. Users select a job and generate a unique per-job roadmap via Claude Haiku.

**Architecture:** Shared Header component (home button) + AppContext state (selectedJob) + modified JobMatches (selection UI + warning) + modified Roadmap (use selectedJob, add guard). No backend changes. Feature isolated to React frontend.

**Tech Stack:** React 18, React Router DOM, Framer Motion (existing), Tailwind CSS (existing)

---

## File Structure

| File | Change | Responsibility |
|------|--------|-----------------|
| `frontend/src/components/Header.jsx` | **Create** | Home button, always visible, navigation to `/` |
| `frontend/src/context/AppContext.jsx` | Modify | Add `selectedJob`, `selectedJobIndex`, `setSelectedJob` to state |
| `frontend/src/App.jsx` | Modify | Import and render `<Header />` above routes |
| `frontend/src/pages/JobMatches.jsx` | Modify | Job card selection, visual highlight, checkmark, weak-match warning, conditional "Generate Roadmap" button |
| `frontend/src/pages/Roadmap.jsx` | Modify | Use `selectedJob` from context, add redirect guard, update reset |

---

## Task 1: Update AppContext — Add Selected Job State

**Files:**
- Modify: `frontend/src/context/AppContext.jsx`

**Current state:** Lines 6-8 contain skills, matches, analysis

**New state to add:** selectedJob, selectedJobIndex

- [ ] **Step 1: Add selectedJob and selectedJobIndex state variables**

Open `frontend/src/context/AppContext.jsx` and add two new useState calls after line 8:

```javascript
import { createContext, useState, useContext, useCallback, useMemo } from 'react'

const AppContext = createContext()

export function AppProvider({ children }) {
  const [skills, setSkills] = useState([])
  const [matches, setMatches] = useState([])
  const [analysis, setAnalysis] = useState(null)
  const [brainDump, setBrainDump] = useState('')
  const [pdfText, setPdfText] = useState('')
  const [selectedJob, setSelectedJob] = useState(null)
  const [selectedJobIndex, setSelectedJobIndex] = useState(null)

  const reset = useCallback(() => {
    setSkills([])
    setMatches([])
    setAnalysis(null)
    setBrainDump('')
    setPdfText('')
    setSelectedJob(null)
    setSelectedJobIndex(null)
  }, [])

  const value = useMemo(() => ({
    skills,
    setSkills,
    matches,
    setMatches,
    analysis,
    setAnalysis,
    brainDump,
    setBrainDump,
    pdfText,
    setPdfText,
    selectedJob,
    setSelectedJob,
    selectedJobIndex,
    setSelectedJobIndex,
    reset,
  }), [skills, matches, analysis, brainDump, pdfText, selectedJob, selectedJobIndex, reset])

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}

export function useApp() {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useApp must be used within an AppProvider')
  }
  return context
}
```

- [ ] **Step 2: Verify the changes are correct**

Check that:
- `selectedJob` and `selectedJobIndex` are initialized to `null`
- Both are added to reset callback
- Both are included in the useMemo value object
- No syntax errors

- [ ] **Step 3: Commit**

```bash
cd "/c/Users/callu/Desktop/ANLP Group Project"
git add frontend/src/context/AppContext.jsx
git commit -m "feat: add selectedJob and selectedJobIndex to AppContext

- Allows tracking which job user selected for roadmap
- Persists selection through navigation
- Cleared on reset to start fresh flow"
```

---

## Task 2: Create Header Component

**Files:**
- Create: `frontend/src/components/Header.jsx`

- [ ] **Step 1: Create the Header component file**

Create new file `frontend/src/components/Header.jsx` with the following content:

```javascript
import { useNavigate } from 'react-router-dom'

export function Header() {
  const navigate = useNavigate()

  return (
    <header
      style={{
        padding: '16px 24px',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
      }}
    >
      <button
        onClick={() => navigate('/')}
        style={{
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          padding: '8px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          color: 'var(--accent)',
          fontSize: '1rem',
          fontWeight: 500,
          transition: 'opacity 0.2s',
        }}
        onMouseEnter={(e) => (e.currentTarget.style.opacity = '0.8')}
        onMouseLeave={(e) => (e.currentTarget.style.opacity = '1')}
        title="Go to home page"
      >
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
          <polyline points="9 22 9 12 15 12 15 22" />
        </svg>
        <span>Career Compass</span>
      </button>
    </header>
  )
}
```

- [ ] **Step 2: Verify the component renders correctly**

Check that:
- Component imports useNavigate from react-router-dom
- Renders a button in header with home icon + "Career Compass" text
- Button has hover effect (opacity change)
- onClick navigates to "/" (home page)
- Styling uses CSS variables for consistency

- [ ] **Step 3: Commit**

```bash
cd "/c/Users/callu/Desktop/ANLP Group Project"
git add frontend/src/components/Header.jsx
git commit -m "feat: create Header component with home button

- Displays at top-left with home icon and Career Compass logo
- Clicking navigates to landing page
- Styled with hover effects, uses CSS variables"
```

---

## Task 3: Integrate Header into App.jsx

**Files:**
- Modify: `frontend/src/App.jsx`

**Current structure:** Lines 1-23 define routes, lines 25-34 define App component

- [ ] **Step 1: Import Header component**

At the top of `frontend/src/App.jsx`, after the existing imports (line 8), add:

```javascript
import { Header } from './components/Header'
```

Full imports section should now be:

```javascript
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import { AppProvider } from './context/AppContext'
import { LinearBackground } from './components/LinearBackground'
import { Header } from './components/Header'
import { Landing } from './pages/Landing'
import { BrainDump } from './pages/BrainDump'
import { JobMatches } from './pages/JobMatches'
import { Roadmap } from './pages/Roadmap'
```

- [ ] **Step 2: Add Header to the App component layout**

Modify the return statement in the App function (lines 26-34) to include `<Header />`:

```javascript
export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <LinearBackground />
        <Header />
        <AnimatedRoutes />
      </BrowserRouter>
    </AppProvider>
  )
}
```

**Key:** Header renders **inside BrowserRouter** (so useNavigate works) but **outside AnimatedRoutes** (so it persists across page changes).

- [ ] **Step 3: Verify the structure**

Check that:
- Header is imported
- Header is rendered above AnimatedRoutes
- Header is inside BrowserRouter
- No syntax errors

- [ ] **Step 4: Commit**

```bash
cd "/c/Users/callu/Desktop/ANLP Group Project"
git add frontend/src/App.jsx
git commit -m "feat: integrate Header component into App layout

- Header renders persistently above all page content
- Positioned inside BrowserRouter but outside AnimatedRoutes
- Home button always accessible from any page"
```

---

## Task 4: Update JobMatches — Job Selection UI and Weak Match Warning

**Files:**
- Modify: `frontend/src/pages/JobMatches.jsx`

**Current structure:** Lines 1-20 are imports/setup, lines 23-35 is the API call handler, lines 43-162 is the render

- [ ] **Step 1: Import setSelectedJob and setSelectedJobIndex from context**

Update line 11 to include new context methods:

```javascript
const { skills, matches, setMatches, setSelectedJob, setSelectedJobIndex } = useApp()
```

Full line should be:

```javascript
const navigate = useNavigate()
  const { skills, matches, setMatches, setSelectedJob, setSelectedJobIndex } = useApp()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showMatches, setShowMatches] = useState(matches.length > 0)
  const [selectedIndex, setSelectedIndex] = useState(null)
```

**Important:** Add `[selectedIndex, setSelectedIndex]` state to track which job is visually selected (this is for local UI state, separate from context).

- [ ] **Step 2: Add handler for job card clicks**

Insert this new handler function after the `getBadgeClass` function (after line 41):

```javascript
  const handleSelectJob = (job, index) => {
    setSelectedIndex(index)
    setSelectedJob(job)
    setSelectedJobIndex(index)
  }
```

- [ ] **Step 3: Add weak match warning logic**

Insert this check after the `getBadgeClass` function and before the return statement:

```javascript
  const hasStrongMatches = matches.length > 0 && matches.some(job => job.score >= 0.60)
```

- [ ] **Step 4: Update the render to show warning and add selection UI**

In the render, find where it shows `<p className="text-center text-sm mb-2" ...>` (around line 66-68) and add the warning **right after** that paragraph:

```javascript
          {!hasStrongMatches && matches.length > 0 && (
            <div className="alert info" style={{ marginBottom: '24px' }}>
              No strong matches found. Showing all available roles — you may need to upskill in specific areas.
            </div>
          )}
```

- [ ] **Step 5: Make job cards clickable with visual feedback**

In the job card rendering loop (line 87-145), update the card wrapper div to be clickable:

Replace:
```javascript
                <motion.div
                  key={idx}
                  className="compass-card"
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: idx * 0.1 }}
                >
```

With:
```javascript
                <motion.div
                  key={idx}
                  className="compass-card"
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: idx * 0.1 }}
                  onClick={() => handleSelectJob(job, idx)}
                  style={{
                    cursor: 'pointer',
                    border: selectedIndex === idx ? '2px solid var(--accent)' : '1px solid var(--border)',
                    transition: 'all 0.2s',
                  }}
                  onMouseEnter={(e) => {
                    if (selectedIndex !== idx) {
                      e.currentTarget.style.border = '2px solid var(--accent-dim)'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (selectedIndex !== idx) {
                      e.currentTarget.style.border = '1px solid var(--border)'
                    }
                  }}
                >
```

- [ ] **Step 6: Add checkmark icon to selected job**

In the card header (around line 99-107), add a checkmark to the right of the badge:

Replace:
```javascript
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <span className="text-xs font-medium mr-2" style={{ color: 'var(--muted)' }}>
                        #{idx + 1}
                      </span>
                      <h3 className="inline text-base font-semibold text-white" style={{ letterSpacing: '-0.02em' }}>
                        {job.title}
                      </h3>
                    </div>
                    <span className={`match-badge ${badgeClass}`}>{job.label}</span>
                  </div>
```

With:
```javascript
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <span className="text-xs font-medium mr-2" style={{ color: 'var(--muted)' }}>
                        #{idx + 1}
                      </span>
                      <h3 className="inline text-base font-semibold text-white" style={{ letterSpacing: '-0.02em' }}>
                        {job.title}
                      </h3>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`match-badge ${badgeClass}`}>{job.label}</span>
                      {selectedIndex === idx && (
                        <svg
                          width="20"
                          height="20"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="var(--accent)"
                          strokeWidth="2"
                        >
                          <polyline points="20 6 9 17 4 12" />
                        </svg>
                      )}
                    </div>
                  </div>
```

- [ ] **Step 7: Add "Generate Roadmap" button that appears only when job is selected**

Find the button group at the end of showMatches section (around line 150-157). Update it to:

```javascript
            <hr className="divider" />

            <div className="flex justify-center gap-3">
              <button className="secondary" onClick={() => navigate('/brain-dump')}>
                ← Back
              </button>
              {selectedIndex !== null && (
                <button className="primary" onClick={() => navigate('/roadmap')}>
                  Generate Roadmap for {matches[selectedIndex].title} →
                </button>
              )}
            </div>
```

**Important:** Only show the "Generate Roadmap" button if `selectedIndex !== null`.

- [ ] **Step 8: Verify the changes**

Check that:
- Warning appears if no strong matches (score >= 0.60)
- Job cards are clickable
- Selected job has 2px accent border
- Non-selected cards show dim border on hover
- Checkmark icon appears on selected job
- "Generate Roadmap" button only shows when a job is selected
- Button text shows the job title
- No syntax errors

- [ ] **Step 9: Commit**

```bash
cd "/c/Users/callu/Desktop/ANLP Group Project"
git add frontend/src/pages/JobMatches.jsx
git commit -m "feat: add job selection UI with visual feedback and weak match warning

- Jobs are now clickable with visual border highlight
- Selected job shows checkmark icon
- Weak match warning appears if no jobs score >= 0.60
- Generate Roadmap button only appears when job is selected
- Button text shows selected job title"
```

---

## Task 5: Update Roadmap — Use Selected Job and Add Guard

**Files:**
- Modify: `frontend/src/pages/Roadmap.jsx`

**Current structure:** Lines 1-7 are imports, lines 10-37 are handlers, lines 40-72 is download logic, lines 74-210 is render

- [ ] **Step 1: Update context destructuring to get selectedJob**

Update line 11:

```javascript
const { skills, matches, analysis, setAnalysis, reset, selectedJob } = useApp()
```

Should now be:

```javascript
const navigate = useNavigate()
  const { skills, matches, analysis, setAnalysis, reset, selectedJob } = useApp()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showRoadmap, setShowRoadmap] = useState(!!analysis)
```

- [ ] **Step 2: Remove the old topJob assignment and add selectedJob guard**

Remove this line (currently line 16):
```javascript
const topJob = matches && matches[0]
```

Replace the existing guard (lines 19-23) with:

```javascript
  // Guard: redirect if no selectedJob
  useEffect(() => {
    if (!selectedJob) {
      navigate('/matches')
    }
  }, [selectedJob, navigate])
```

- [ ] **Step 3: Update the handleGenerateRoadmap function to use selectedJob**

Replace the existing function (lines 25-37) with:

```javascript
  const handleGenerateRoadmap = async () => {
    setLoading(true)
    setError('')
    try {
      const result = await api.analyzeGaps(selectedJob, skills)
      setAnalysis(result)
      setShowRoadmap(true)
    } catch (err) {
      setError(`Roadmap generation failed: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }
```

**Note:** Only change is `topJob` → `selectedJob`

- [ ] **Step 4: Update the handleDownload function to use selectedJob**

Replace line 42 in the current function:
```javascript
Target Role: ${topJob.title}
Match Score: ${Math.round(topJob.score * 100)}% (${topJob.label})
```

With:
```javascript
Target Role: ${selectedJob.title}
Match Score: ${Math.round(selectedJob.score * 100)}% (${selectedJob.label})
```

- [ ] **Step 5: Update the return statement guard**

Replace line 72:
```javascript
if (!topJob) return null
```

With:
```javascript
if (!selectedJob) return null
```

- [ ] **Step 6: Update all references to topJob in the render to use selectedJob**

Find these lines and replace `topJob` with `selectedJob`:
- Line 99: `Analysing skill gaps for {' '}<strong className="text-white">{selectedJob.title}`
- Line 100-101: `<span style={{ color: 'var(--muted)' }}>({selectedJob.label} — {Math.round(selectedJob.score * 100)}% match)`

- [ ] **Step 7: Update the "Start Over" button to clear selectedJob**

The reset button (around line 197-203) should already work since we updated reset() in Task 1 to clear selectedJob. Verify the button still has:

```javascript
                onClick={() => {
                  reset()
                  navigate('/')
                }}
```

- [ ] **Step 8: Verify the changes**

Check that:
- selectedJob is imported from context
- Guard redirects to /matches if no selectedJob
- handleGenerateRoadmap uses selectedJob (not matches[0])
- Download uses selectedJob
- All UI references show selectedJob title and score
- No syntax errors

- [ ] **Step 9: Commit**

```bash
cd "/c/Users/callu/Desktop/ANLP Group Project"
git add frontend/src/pages/Roadmap.jsx
git commit -m "feat: use selectedJob instead of topJob for job-specific roadmaps

- Roadmap now generates analysis for user-selected job, not always top match
- Each job selection generates unique 30-day plan via Claude Haiku
- Added guard to redirect if no job selected
- User can go back and select different job for different roadmap"
```

---

## Task 6: End-to-End Testing

**Files:**
- Test: Manual browser testing (no automation framework)

- [ ] **Step 1: Start the frontend dev server**

```bash
cd "/c/Users/callu/Desktop/ANLP Group Project/frontend"
npm run dev
```

Expected output: "VITE ... ready in XXX ms" and a local URL like `http://localhost:5173`

- [ ] **Step 2: Start the FastAPI backend**

In a separate terminal:

```bash
cd "/c/Users/callu/Desktop/ANLP Group Project"
python -m uvicorn main:app --reload
```

Expected output: "Application startup complete"

- [ ] **Step 3: Test Header home button on all pages**

- Navigate to http://localhost:5173
- Click "Extract My Skills" after entering sample text (or using PDF upload)
- Verify Header is visible at top-left with home icon and "Career Compass" text
- Click home button → should return to Landing page
- Repeat on /matches and /roadmap pages

- [ ] **Step 4: Test job matching and weak match warning**

- On BrainDump page, use sample text or upload a resume
- Click "Extract My Skills"
- Click "Find My Job Matches"
- **If no strong matches (score >= 0.60):** verify warning appears: "No strong matches found. Showing all available roles..."
- **If strong matches exist:** verify no warning appears
- Verify all job cards are displayed regardless of score

- [ ] **Step 5: Test job selection UI**

- On JobMatches page with results displayed
- Click on first job card
  - Expected: card gets 2px accent-colored border
  - Expected: checkmark icon appears in top-right of card
  - Expected: "Generate Roadmap for [Job Title]" button appears at bottom
- Hover over unselected cards
  - Expected: border becomes dim accent color
  - Expected: clicking removes highlight from first job, adds to hovered card
- Verify only one job can be selected at a time

- [ ] **Step 6: Test job-specific roadmap generation**

- With Job A selected, click "Generate Roadmap for [Job A]"
- Verify navigation to /roadmap page
- Verify page title shows "Analysing skill gaps for [Job A]"
- Click "Generate My Roadmap" button
- Verify roadmap loads with skills and 4-week plan specific to Job A
- Click "Back to Matches"
- Verify back on JobMatches page (Job A still selected)
- Click on different job (Job B)
  - Expected: Job B becomes selected (checkmark, border)
- Click "Generate Roadmap for [Job B]"
- Verify roadmap page loads with Job B title
- Verify the 4-week plan is **different** from Job A's plan (Claude analyzed different job)
- Click "Download Plan" on Job B roadmap
- Verify downloaded file contains Job B title and different content than Job A

- [ ] **Step 7: Test reset flow**

- On Roadmap page for any job
- Click "Start Over"
- Verify navigation to Landing page
- Verify no selected job remains (can verify by going back to matches and seeing no selection)

- [ ] **Step 8: Test error states (optional but recommended)**

- Try navigating directly to /roadmap (without selecting a job)
  - Expected: redirects to /matches
- On JobMatches, click "Find My Matches" with no valid skills (edge case, should not happen)
  - Expected: error message or empty results
- Network failure simulation (browser DevTools):
  - Try clicking match button with network offline
  - Expected: error message appears

- [ ] **Step 9: Commit the feature (after all testing passes)**

```bash
cd "/c/Users/callu/Desktop/ANLP Group Project"
git add -A
git commit -m "test: manual end-to-end testing of job selection feature

Verified:
- Header home button works on all pages
- Job cards are selectable with visual feedback (border, checkmark)
- Weak match warning appears when no strong matches
- Generate Roadmap button only shows when job selected
- Each job selection generates unique roadmap via Claude Haiku
- Users can select multiple jobs and get different analyses
- Reset flow clears selection state"
```

---

## Self-Review Checklist

**Spec Coverage:** ✅
- [ ] Header with home button in top-left ← Task 2-3
- [ ] Job selection with visual feedback ← Task 4
- [ ] "Generate Roadmap" button requires click ← Task 4, Step 7
- [ ] Weak match warning (no threshold filtering) ← Task 4, Step 3-4
- [ ] Unique roadmaps per job using selectedJob ← Task 5
- [ ] End-to-end testing ← Task 6

**Placeholder Scan:** ✅
- No "TBD", "TODO", "add later"
- All code shown in full
- All commands and expected output specified

**Type/Name Consistency:** ✅
- `selectedJob` state consistent across AppContext, JobMatches, Roadmap
- `selectedJobIndex` used in both context and JobMatches
- `handleSelectJob` handler clear and consistent
- Function signatures match throughout

**File Paths:** ✅
- All exact paths provided (`frontend/src/components/Header.jsx`, etc.)
- No placeholders or generic paths

**Scope:** ✅
- 5 files (1 new, 4 modified)
- 6 tasks, each 2-5 minutes
- All changes isolated to frontend React layer
- No backend changes needed
- Can be tested in single development session