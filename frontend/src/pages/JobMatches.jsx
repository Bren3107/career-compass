import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { api } from '../api/client'
import { useApp } from '../context/AppContext'
import { StepIndicator } from '../components/StepIndicator'
import { SkillBadge } from '../components/SkillBadge'

export function JobMatches() {
  const navigate = useNavigate()
  const { skills, matches, setMatches } = useApp()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showMatches, setShowMatches] = useState(matches.length > 0)

  // Guard: redirect to BrainDump if no skills
  useEffect(() => {
    if (!skills || skills.length === 0) {
      navigate('/brain-dump')
    }
  }, [skills, navigate])

  const handleFindMatches = async () => {
    setLoading(true)
    setError('')
    try {
      const result = await api.matchJobs(skills)
      setMatches(result.matches)
      setShowMatches(true)
    } catch (err) {
      setError(`Job matching failed: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const getBadgeClass = (score) => {
    if (score >= 0.6) return 'strong'
    if (score >= 0.4) return 'moderate'
    return 'weak'
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.4 }}
    >
      <div className="content-container">
        <StepIndicator currentStep={2} />

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="page-title">Your Top Job Matches</h1>
          <p className="page-subtitle">Roles that align with your skills and experience</p>
          <p style={{ textAlign: 'center', color: 'var(--muted)' }}>
            Matching your <strong>{skills.length} detected skills</strong> against the Sydney job market...
          </p>
        </motion.div>

        {!showMatches && (
          <div style={{ textAlign: 'center', marginTop: '40px' }}>
            <button className="primary" onClick={handleFindMatches} disabled={loading}>
              {loading ? '⏳ Finding Matches...' : 'Find My Matches'}
            </button>
          </div>
        )}

        {error && <div className="alert warning">{error}</div>}

        {showMatches && matches.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, staggerChildren: 0.1, delayChildren: 0.2 }}
          >
            {matches.map((job, idx) => {
              const scorePct = Math.round(job.score * 100)
              const badgeClass = getBadgeClass(job.score)

              return (
                <motion.div
                  key={idx}
                  className="compass-card"
                  initial={{ opacity: 0, y: 24 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5 }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                    <h3 style={{ margin: '0 0 4px 0', fontSize: '1.2rem' }}>
                      #{idx + 1} — {job.title}
                    </h3>
                    <span className={`match-badge ${badgeClass}`}>{job.label}</span>
                  </div>

                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${scorePct}%` }} />
                  </div>
                  <p style={{ fontSize: '0.9rem', color: 'var(--muted)', marginBottom: '12px' }}>
                    {scorePct}% similarity
                  </p>

                  {job.seniority || job.company_type || job.location ? (
                    <p
                      style={{
                        fontSize: '0.85rem',
                        color: 'var(--muted)',
                        marginBottom: '16px',
                      }}
                    >
                      {[job.seniority, job.company_type, job.location].filter(Boolean).join(' · ')}
                    </p>
                  ) : null}

                  <details style={{ marginTop: '12px' }}>
                    <summary style={{ cursor: 'pointer', fontWeight: 600, color: 'var(--accent)' }}>
                      Required skills
                    </summary>
                    <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid var(--border)' }}>
                      {job.skills_required ? (
                        job.skills_required.split(',').map((skill, i) => (
                          <SkillBadge key={i} skill={skill.trim()} />
                        ))
                      ) : (
                        <p>Not specified.</p>
                      )}
                    </div>
                  </details>
                </motion.div>
              )
            })}

            <hr className="divider" />

            <div className="flex-row" style={{ gap: '12px', justifyContent: 'center' }}>
              <button className="secondary" onClick={() => navigate('/brain-dump')} style={{ flex: 1, maxWidth: '200px' }}>
                ← Back
              </button>
              <button className="primary" onClick={() => navigate('/roadmap')} style={{ flex: 1, maxWidth: '200px' }}>
                Generate My Roadmap →
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}
