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
