/**
 * API client for Career Compass backend.
 * Handles all fetch requests to the FastAPI endpoints.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(endpoint, method = 'GET', body = null) {
  const url = `${API_BASE}${endpoint}`
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
  }

  if (body) {
    options.body = JSON.stringify(body)
  }

  const response = await fetch(url, options)

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `API error: ${response.status}`)
  }

  return await response.json()
}

export const api = {
  // GET /health
  health: () => request('/health'),

  // POST /api/extract-skills
  extractSkills: (text) => request('/api/extract-skills', 'POST', { text }),

  // POST /api/match-jobs
  matchJobs: (skills) => request('/api/match-jobs', 'POST', { skills }),

  // POST /api/analyze-gaps
  analyzeGaps: (job, studentSkills) =>
    request('/api/analyze-gaps', 'POST', {
      job,
      student_skills: studentSkills,
    }),
}
