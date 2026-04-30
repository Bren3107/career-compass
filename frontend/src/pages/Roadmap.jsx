import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { api } from '../api/client'
import { useApp } from '../context/AppContext'
import { StepIndicator } from '../components/StepIndicator'
import { SkillBadge } from '../components/SkillBadge'

export function Roadmap() {
  const navigate = useNavigate()
  const { skills, matches, analysis, setAnalysis, reset } = useApp()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showRoadmap, setShowRoadmap] = useState(!!analysis)

  const topJob = matches && matches[0]

  // Guard: redirect if no matches
  useEffect(() => {
    if (!matches || matches.length === 0) {
      navigate('/matches')
    }
  }, [matches, navigate])

  const handleGenerateRoadmap = async () => {
    setLoading(true)
    setError('')
    try {
      const result = await api.analyzeGaps(topJob, skills)
      setAnalysis(result)
      setShowRoadmap(true)
    } catch (err) {
      setError(`Roadmap generation failed: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = () => {
    if (!analysis || !topJob) return

    const planText = `Career Compass — 30-Day Roadmap

Target Role: ${topJob.title}
Match Score: ${Math.round(topJob.score * 100)}% (${topJob.label})

Skills to Develop:
${analysis.missing_skills.map((s) => `  - ${s}`).join('\n')}

Week 1:
${analysis.week1}

Week 2:
${analysis.week2}

Week 3:
${analysis.week3}

Week 4:
${analysis.week4}
`

    const element = document.createElement('a')
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(planText))
    element.setAttribute('download', 'career-compass-roadmap.txt')
    element.style.display = 'none'
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  if (!topJob) return null

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.4 }}
    >
      <div className="content-container">
        <StepIndicator currentStep={3} />

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <p
            className="text-sm font-medium tracking-widest uppercase mb-3 text-center"
            style={{ color: 'var(--accent)' }}
          >
            Step 03
          </p>
          <h1 className="page-title">Your Personalised Roadmap</h1>
          <p className="page-subtitle">A 30-day plan to close skill gaps and land your next role</p>
          <p className="text-center text-sm" style={{ color: 'var(--text-secondary)' }}>
            Analysing skill gaps for{' '}
            <strong className="text-white">{topJob.title}</strong>{' '}
            <span style={{ color: 'var(--muted)' }}>
              ({topJob.label} — {Math.round(topJob.score * 100)}% match)
            </span>
          </p>
        </motion.div>

        {!showRoadmap && (
          <div className="text-center mt-10">
            <button className="primary" onClick={handleGenerateRoadmap} disabled={loading}>
              {loading ? 'Generating Roadmap...' : 'Generate My Roadmap'}
            </button>
          </div>
        )}

        {error && <div className="alert warning">{error}</div>}

        {showRoadmap && analysis && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            <hr className="divider" />
            <h2 className="text-base font-semibold mb-4" style={{ letterSpacing: '-0.02em' }}>
              Skills to develop
            </h2>

            {analysis.missing_skills && analysis.missing_skills.length > 0 ? (
              <div className="mb-8">
                {analysis.missing_skills.map((skill) => (
                  <SkillBadge key={skill} skill={skill} />
                ))}
              </div>
            ) : (
              <div className="alert info">
                No specific skill gaps identified — you may already be a strong match!
              </div>
            )}

            <hr className="divider" />
            <h2 className="text-base font-semibold mb-6" style={{ letterSpacing: '-0.02em' }}>
              Your 30-Day Learning Plan
            </h2>

            {['Week 1', 'Week 2', 'Week 3', 'Week 4'].map((week, idx) => {
              const contentKey = `week${idx + 1}`
              const content = analysis[contentKey]

              return (
                <details key={week} className="expander" open>
                  <summary className="expander-header">
                    <span className="flex items-center gap-2">
                      <span
                        className="w-1.5 h-1.5 rounded-full inline-block"
                        style={{ backgroundColor: 'var(--accent)' }}
                      />
                      {week}
                    </span>
                    <svg
                      width="12"
                      height="12"
                      viewBox="0 0 12 12"
                      fill="none"
                      className="text-white/30"
                    >
                      <path
                        d="M3 4.5L6 7.5L9 4.5"
                        stroke="currentColor"
                        strokeWidth="1.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  </summary>
                  <div className="expander-content">
                    <p style={{ whiteSpace: 'pre-wrap', lineHeight: '1.8' }}>{content}</p>
                  </div>
                </details>
              )
            })}

            <hr className="divider" />

            <div className="flex justify-center gap-3">
              <button className="secondary" onClick={() => navigate('/matches')}>
                ← Back to Matches
              </button>
              <button className="primary" onClick={handleDownload}>
                Download Plan
              </button>
            </div>

            <hr className="divider" />

            <div className="text-center">
              <button
                className="secondary"
                onClick={() => {
                  reset()
                  navigate('/')
                }}
              >
                Start Over
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}
