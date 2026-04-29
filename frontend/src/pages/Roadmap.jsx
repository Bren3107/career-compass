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
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="page-title">Your Personalised Roadmap</h1>
          <p className="page-subtitle">A 30-day plan to close skill gaps and land your next role</p>
          <p style={{ textAlign: 'center', color: 'var(--muted)' }}>
            Analysing skill gaps for <strong>{topJob.title}</strong> ({topJob.label} — {Math.round(topJob.score * 100)}% match)
          </p>
        </motion.div>

        {!showRoadmap && (
          <div style={{ textAlign: 'center', marginTop: '40px' }}>
            <button className="primary" onClick={handleGenerateRoadmap} disabled={loading}>
              {loading ? '⏳ Generating Roadmap...' : 'Generate My Roadmap'}
            </button>
          </div>
        )}

        {error && <div className="alert warning">{error}</div>}

        {showRoadmap && analysis && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
          >
            <hr className="divider" />
            <h2 style={{ fontSize: '1.3rem', marginBottom: '16px' }}>Skills to develop</h2>

            {analysis.missing_skills && analysis.missing_skills.length > 0 ? (
              <div style={{ marginBottom: '32px' }}>
                {analysis.missing_skills.map((skill) => (
                  <SkillBadge key={skill} skill={skill} />
                ))}
              </div>
            ) : (
              <div className="alert info">No specific skill gaps identified — you may already be a strong match!</div>
            )}

            <hr className="divider" />
            <h2 style={{ fontSize: '1.3rem', marginBottom: '24px' }}>Your 30-Day Learning Plan</h2>

            {['Week 1', 'Week 2', 'Week 3', 'Week 4'].map((week, idx) => {
              const contentKey = `week${idx + 1}`
              const content = analysis[contentKey]

              return (
                <details key={week} className="expander" open>
                  <summary className="expander-header">
                    {week}
                    <span>▼</span>
                  </summary>
                  <div className="expander-content">
                    <p style={{ whiteSpace: 'pre-wrap', lineHeight: '1.8' }}>{content}</p>
                  </div>
                </details>
              )
            })}

            <hr className="divider" />

            <div className="flex-row" style={{ gap: '12px', justifyContent: 'center' }}>
              <button className="secondary" onClick={() => navigate('/matches')} style={{ flex: 1, maxWidth: '200px' }}>
                ← Back to Matches
              </button>
              <button className="primary" onClick={handleDownload} style={{ flex: 1, maxWidth: '200px' }}>
                📥 Download Plan
              </button>
            </div>

            <hr className="divider" />

            <div style={{ textAlign: 'center' }}>
              <button
                className="secondary"
                onClick={() => {
                  reset()
                  navigate('/')
                }}
                style={{ width: '100%', maxWidth: '200px' }}
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
