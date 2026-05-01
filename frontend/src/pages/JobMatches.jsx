import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { api } from '../api/client'
import { useApp } from '../context/AppContext'
import { StepIndicator } from '../components/StepIndicator'
import { SkillBadge } from '../components/SkillBadge'

export function JobMatches() {
  const navigate = useNavigate()
  const { skills, matches, setMatches, setSelectedJob, setSelectedJobIndex } = useApp()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showMatches, setShowMatches] = useState(matches.length > 0)
  const [selectedIndex, setSelectedIndex] = useState(null)

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

  const handleSelectJob = (job, index) => {
    setSelectedIndex(index)
    setSelectedJob(job)
    setSelectedJobIndex(index)
  }

  const hasStrongMatches = matches.length > 0 && matches.some(job => job.score >= 0.60)

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
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <p
            className="text-sm font-medium tracking-widest uppercase mb-3 text-center"
            style={{ color: 'var(--accent)' }}
          >
            Step 02
          </p>
          <h1 className="page-title">Your Top Job Matches</h1>
          <p className="page-subtitle">Roles that align with your skills and experience</p>
          <p className="text-center text-sm mb-2" style={{ color: 'var(--text-secondary)' }}>
            Matching your <strong className="text-white">{skills.length} detected skills</strong> against the Sydney job market
          </p>
          {!hasStrongMatches && matches.length > 0 && (
            <div className="alert info" style={{ marginBottom: '24px' }}>
              No strong matches found. Showing all available roles — you may need to upskill in specific areas.
            </div>
          )}
        </motion.div>

        {!showMatches && (
          <div className="text-center mt-10">
            <button className="primary" onClick={handleFindMatches} disabled={loading}>
              {loading ? 'Finding Matches...' : 'Find My Matches'}
            </button>
          </div>
        )}

        {error && <div className="alert warning">{error}</div>}

        {showMatches && matches.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            {matches.map((job, idx) => {
              const scorePct = Math.round(job.score * 100)
              const badgeClass = getBadgeClass(job.score)

              return (
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
                          aria-hidden="true"
                        >
                          <polyline points="20 6 9 17 4 12" />
                        </svg>
                      )}
                    </div>
                  </div>

                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${scorePct}%` }} />
                  </div>
                  <p className="text-xs mb-3" style={{ color: 'var(--muted)' }}>
                    {scorePct}% similarity
                  </p>

                  {(job.seniority || job.company_type || job.location) && (
                    <p className="text-xs mb-4" style={{ color: 'var(--text-secondary)' }}>
                      {[job.seniority, job.company_type, job.location].filter(Boolean).join(' · ')}
                    </p>
                  )}

                  <details className="mt-3">
                    <summary
                      className="cursor-pointer font-medium text-sm"
                      style={{ color: 'var(--accent)' }}
                    >
                      Required skills
                    </summary>
                    <div
                      className="mt-3 pt-3"
                      style={{ borderTop: '1px solid var(--border)' }}
                    >
                      {job.skills_required ? (
                        job.skills_required.split(',').map((skill, i) => (
                          <SkillBadge key={i} skill={skill.trim()} />
                        ))
                      ) : (
                        <p className="text-sm" style={{ color: 'var(--muted)' }}>Not specified.</p>
                      )}
                    </div>
                  </details>
                </motion.div>
              )
            })}

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
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}
