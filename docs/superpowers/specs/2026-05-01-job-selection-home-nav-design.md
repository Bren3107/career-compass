# Design: Job Selection, Home Navigation, and Smart Matching

**Date:** 2026-05-01  
**Scope:** Three integrated features for Career Compass React + FastAPI app  
**Author:** Claude Code

---

## Overview

This design adds three user-facing improvements:
1. **Home Navigation** — persistent home button in header across all pages
2. **Job Selection** — users select a specific job to analyze, with visual feedback
3. **Smart Matching** — warning when no strong matches found; all matches displayed

The critical insight: roadmaps are **job-specific**. Each selected job generates a unique 30-day plan via Claude Haiku, so users can explore "what if I target job A vs job B?"

---

## Feature 1: Shared Header with Home Button

### Component: `Header.jsx`
- Location: `frontend/src/components/Header.jsx`
- Renders at top-left: home icon + "Career Compass" logo (clickable)
- Click navigates to `/` (Landing page)
- Styled consistently with existing design system
- Small, focused component (~40–50 lines)

### Integration: `App.jsx`
- Header renders **outside** `AnimatedRoutes` but inside `BrowserRouter`
- Ensures header persists during page transitions
- Structure:
  ```
  <BrowserRouter>
    <LinearBackground />
    <Header />          ← NEW
    <AnimatedRoutes />
  </BrowserRouter>
  ```

### Behavior
- Always visible, always clickable
- No state dependency (stateless component)
- Clicking resets app to Landing (user can start over anytime)

---

## Feature 2: Job Selection with Unique Roadmaps

### State: `AppContext`
Add two new pieces of state:
- `selectedJob` — the full job object selected by user (or `null`)
- `selectedJobIndex` — index in matches array (for future features like "next/prev job")

Updated context structure:
```javascript
{
  skills,
  matches,
  selectedJob,              // ← NEW
  selectedJobIndex,         // ← NEW
  setSelectedJob,           // ← NEW
  analysis,
  ...
}
```

### Component: `JobMatches.jsx` (Modified)

#### Job Card Clickability
- Each job card becomes clickable (`onClick` handler)
- Clicking sets `selectedJob` in context
- Click handler:
  ```javascript
  const handleSelectJob = (job, index) => {
    setSelectedJob(job)
    setSelectedJobIndex(index)
  }
  ```

#### Visual Feedback for Selected Job
- Selected job card displays: `border-2 border-accent` (or similar)
- Selected job card shows checkmark icon in top-right
- Non-selected cards have no border
- Only one job can be selected at a time
- Selecting the same job again keeps it selected (no toggle deselect)

#### Generate Roadmap Button
- Button appears **only when a job is selected**
- Text: `"Generate Roadmap for [Job Title] →"`
- Button placement: below the job cards, in the button group (after the matches list)
- Clicking navigates to `/roadmap` with `selectedJob` in context

#### Weak Match Warning
- Added below "Matching your X detected skills..." subtitle
- Only shown if **no jobs have `score >= 0.60`**
- Message: `"No strong matches found. Showing all available roles — you may need to upskill in specific areas."`
- Alert styling: info-level (not warning, not error)

### Component: `Roadmap.jsx` (Modified)

#### Use Selected Job, Not Top Job
- Replace: `const topJob = matches && matches[0]`
- With: `const { selectedJob } = useApp()`
- All references to `topJob` change to `selectedJob`

#### Guard Against Missing Selection
- Add effect: if `!selectedJob`, redirect to `/matches`
- Prevents page load without a valid job context

#### Job-Specific Analysis
- Call: `api.analyzeGaps(selectedJob, skills)` (unchanged API contract)
- Backend generates **unique plan for this job**
- No caching of analysis across job selections

#### Reset Flow
- When user clicks "Start Over", `reset()` clears `selectedJob`
- User returns to Landing, can restart fresh flow

---

## Feature 3: Smart Matching (Weak Match Warning)

### Logic in `JobMatches.jsx`
```javascript
const hasStrongMatches = matches.some(job => job.score >= 0.60)
```

### Display
- Warning appears above job cards if `!hasStrongMatches`
- Shows **all matches** (no filtering on frontend)
- Message is informational, not blocking

### Backend (No Changes)
- `main.py` already returns `top_k=6` (or however many exist)
- No threshold filtering on backend
- Frontend chooses to warn based on score distribution

---

## Data Flow

### Happy Path: Select Job A → Generate Roadmap
```
1. User on JobMatches, clicks "Find Matches"
   → GET /api/match-jobs returns 6 jobs with scores
2. JobMatches renders jobs, shows warning if no strong matches
3. User clicks Job A card
   → setSelectedJob(jobA), visual highlight appears
4. User clicks "Generate Roadmap for Job A"
   → Navigate to /roadmap with selectedJob in context
5. Roadmap page loads, renders "Analysing skill gaps for Job A"
6. User clicks "Generate My Roadmap"
   → POST /api/analyze-gaps with selectedJob
   → Claude Haiku returns unique plan for Job A
```

### Alternate: Back to Matches → Select Job B → Different Roadmap
```
1. User on Roadmap for Job A
2. Clicks "Back to Matches"
   → Returns to JobMatches, Job A still highlighted
3. User clicks Job B card
   → setSelectedJob(jobB), highlight moves to Job B
4. Clicks "Generate Roadmap for Job B"
   → Navigate to Roadmap
5. Roadmap page shows "Analysing skill gaps for Job B"
6. Clicks "Generate My Roadmap"
   → POST /api/analyze-gaps with selectedJob (Job B)
   → Completely different plan generated
```

---

## Error Handling

### JobMatches
- Guard: if no skills extracted, redirect to BrainDump (existing)
- No new error states introduced

### Roadmap
- Guard: if no selectedJob, redirect to JobMatches
- If API fails, show error alert (existing pattern)

---

## Testing Checklist

- [ ] Header home button appears on all pages
- [ ] Clicking home button returns to Landing
- [ ] Job cards become highlighted when clicked
- [ ] Only one job highlighted at a time
- [ ] Checkmark icon visible on selected job
- [ ] "Generate Roadmap for [Job]" button appears when job selected
- [ ] Weak match warning appears if no score >= 0.60
- [ ] Clicking "Generate Roadmap" navigates to Roadmap page
- [ ] Roadmap analysis uses the selected job (not always top job)
- [ ] Going back and selecting Job B generates different roadmap than Job A
- [ ] Roadmap guards against missing selectedJob

---

## Files to Modify

| File | Change |
|------|--------|
| `frontend/src/App.jsx` | Add `<Header />` to layout |
| `frontend/src/components/Header.jsx` | **NEW** — home button component |
| `frontend/src/context/AppContext.jsx` | Add `selectedJob`, `selectedJobIndex` state |
| `frontend/src/pages/JobMatches.jsx` | Job card selection, warning, button logic |
| `frontend/src/pages/Roadmap.jsx` | Use `selectedJob` instead of `matches[0]`, add guard |
| `main.py` | No changes |
| `src/*.py` | No changes |

---

## Implementation Order

1. Update `AppContext` (add state)
2. Create `Header.jsx` component
3. Update `App.jsx` (integrate Header)
4. Update `JobMatches.jsx` (selection + warning)
5. Update `Roadmap.jsx` (use selectedJob, add guard)
6. Manual test end-to-end flow

---

## Success Criteria

- ✅ User can return to home from any page via header button
- ✅ User can select different jobs and get unique roadmaps
- ✅ User sees warning if no strong matches exist
- ✅ All matches displayed (no filtering)
- ✅ No breaking changes to API contracts