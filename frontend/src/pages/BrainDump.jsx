import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { api } from '../api/client'
import { useApp } from '../context/AppContext'
import { StepIndicator } from '../components/StepIndicator'
import { SkillBadge } from '../components/SkillBadge'

const SAMPLE_TEXT =
  'I studied Information Systems at UTS and did a data analysis project where I used SQL to query a large database and built reports in SSRS and Power BI. I\'ve also done some Python scripting for data cleaning with pandas. During my internship at a financial services company I worked with Excel and learned about business requirements gathering and stakeholder communication. I\'m interested in machine learning and have done the fast.ai course on my own. I\'ve used Azure basics and know how Git works from my group projects. I\'m comfortable with presenting findings to non-technical audiences.'

export function BrainDump() {
  const navigate = useNavigate()
  const { skills, setSkills, setBrainDump } = useApp()
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleExtract = async () => {
    if (!text.trim()) {
      setError('Please paste some experience text before extracting skills.')
      return
    }
    if (text.split(' ').length < 30) {
      setError(`Your text is only ${text.split(' ').length} words. Add more detail for better skill extraction (aim for 50+ words).`)
      return
    }

    setLoading(true)
    setError('')
    try {
      const result = await api.extractSkills(text)
      setSkills(result.skills)
      setBrainDump(text)
    } catch (err) {
      setError(`Extraction failed: ${err.message}`)
    } finally {
      setLoading(false)
    }
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
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="page-title">Tell us about yourself</h1>
          <p className="page-subtitle">Paste anything — projects, experience, internships, side work. The more detail, the better.</p>
        </motion.div>

        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={SAMPLE_TEXT}
          style={{ minHeight: '280px', marginBottom: '24px' }}
        />

        <div className="flex-row" style={{ gap: '12px', marginBottom: '32px' }}>
          <button
            className="primary"
            onClick={handleExtract}
            disabled={loading}
            style={{ flex: 3 }}
          >
            {loading ? '⏳ Extracting...' : 'Extract My Skills'}
          </button>
          <button
            className="secondary"
            onClick={() => setText(SAMPLE_TEXT)}
            style={{ flex: 1 }}
          >
            Use Sample
          </button>
        </div>

        {error && <div className="alert warning">{error}</div>}

        {skills.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <hr className="divider" />
            <h2 style={{ fontSize: '1.3rem', marginBottom: '16px' }}>Skills detected ({skills.length})</h2>

            <div style={{ marginBottom: '32px' }}>
              {skills.map((skill) => (
                <SkillBadge key={skill} skill={skill} />
              ))}
            </div>

            <button
              className="primary"
              onClick={() => navigate('/matches')}
              style={{ width: '100%', maxWidth: '300px', display: 'block', margin: '0 auto' }}
            >
              Find My Job Matches →
            </button>
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}
