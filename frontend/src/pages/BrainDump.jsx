import { useState, useRef } from 'react'
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
  const { skills, setSkills, setBrainDump, pdfText, setPdfText } = useApp()
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const fileInputRef = useRef(null)

  const handleExtract = async () => {
    const sourceText = text || pdfText
    if (!sourceText.trim()) {
      setError('Please paste some experience text or upload a resume PDF.')
      return
    }
    if (sourceText.split(' ').length < 30) {
      setError(`Your text is only ${sourceText.split(' ').length} words. Add more detail for better skill extraction (aim for 50+ words).`)
      return
    }

    setLoading(true)
    setError('')
    try {
      const result = await api.extractSkills(sourceText)
      setSkills(result.skills)
      setBrainDump(sourceText)
    } catch (err) {
      setError(`Extraction failed: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handlePdfUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Please upload a PDF file.')
      return
    }

    setLoading(true)
    setError('')
    try {
      const result = await api.extractFromPdf(file)
      setPdfText(result.text)
      setSkills(result.skills)
      setText('') // Clear text input if PDF is used
      // Scroll to show extracted text
      setTimeout(() => {
        document.querySelector('[data-pdf-result]')?.scrollIntoView({ behavior: 'smooth' })
      }, 100)
    } catch (err) {
      setError(`PDF upload failed: ${err.message}`)
      setPdfText('')
    } finally {
      setLoading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const currentSource = text || pdfText
  const hasContent = currentSource.trim().length > 0
  const wordCount = currentSource.split(' ').length

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
            Step 01
          </p>
          <h1 className="page-title">Tell us about yourself</h1>
          <p className="page-subtitle">
            Paste your experience or upload your resume (PDF). The more detail, the better.
          </p>
        </motion.div>

        {/* Text Input Section */}
        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', fontWeight: 500 }}>
            Option 1: Paste Your Experience
          </label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={SAMPLE_TEXT}
            disabled={pdfText.length > 0}
            style={{
              minHeight: '180px',
              marginBottom: '12px',
              opacity: pdfText.length > 0 ? 0.5 : 1,
              cursor: pdfText.length > 0 ? 'not-allowed' : 'text',
            }}
          />
          <button
            className="secondary"
            onClick={() => setText(SAMPLE_TEXT)}
            disabled={pdfText.length > 0}
            style={{ marginBottom: '20px' }}
          >
            Use Sample Text
          </button>
        </div>

        {/* PDF Upload Section */}
        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', fontWeight: 500 }}>
            Option 2: Upload Your Resume (PDF)
          </label>
          <div
            style={{
              border: '2px dashed var(--accent)',
              borderRadius: '8px',
              padding: '20px',
              textAlign: 'center',
              backgroundColor: 'rgba(99, 102, 241, 0.05)',
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
            onClick={() => fileInputRef.current?.click()}
            onDragOver={(e) => {
              e.preventDefault()
              e.currentTarget.style.backgroundColor = 'rgba(99, 102, 241, 0.15)'
            }}
            onDragLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'rgba(99, 102, 241, 0.05)'
            }}
            onDrop={(e) => {
              e.preventDefault()
              e.currentTarget.style.backgroundColor = 'rgba(99, 102, 241, 0.05)'
              if (e.dataTransfer.files[0]) {
                handlePdfUpload({ target: { files: e.dataTransfer.files } })
              }
            }}
          >
            <p style={{ margin: 0, color: 'var(--text-secondary)' }}>
              📄 Drag and drop your PDF here, or click to select
            </p>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={handlePdfUpload}
            style={{ display: 'none' }}
            disabled={loading}
          />
        </div>

        {pdfText && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            data-pdf-result
            style={{
              backgroundColor: 'rgba(34, 197, 94, 0.1)',
              border: '1px solid rgba(34, 197, 94, 0.3)',
              borderRadius: '8px',
              padding: '12px',
              marginBottom: '20px',
              fontSize: '0.85rem',
              color: 'var(--text-secondary)',
            }}
          >
            ✓ PDF uploaded successfully. {wordCount} words extracted.
            <button
              className="secondary"
              onClick={() => {
                setPdfText('')
                setSkills([])
              }}
              style={{ marginLeft: '12px', padding: '4px 8px', fontSize: '0.8rem' }}
            >
              Clear PDF
            </button>
          </motion.div>
        )}

        <div className="flex-row" style={{ gap: '10px', marginBottom: '32px' }}>
          <button
            className="primary"
            onClick={handleExtract}
            disabled={loading || !hasContent}
            style={{ flex: 1 }}
          >
            {loading ? 'Processing...' : 'Extract My Skills'}
          </button>
        </div>

        {error && <div className="alert warning">{error}</div>}

        {skills.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <hr className="divider" />
            <h2 style={{ fontSize: '1.1rem', marginBottom: '16px', fontWeight: 600 }}>
              Skills detected
              <span className="ml-2 text-sm font-normal" style={{ color: 'var(--muted)' }}>
                {skills.length}
              </span>
            </h2>

            <div style={{ marginBottom: '32px' }}>
              {skills.map((skill) => (
                <SkillBadge key={skill} skill={skill} />
              ))}
            </div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-center"
            >
              <button
                className="primary"
                onClick={() => navigate('/matches')}
                style={{ padding: '12px 28px' }}
              >
                Find My Job Matches →
              </button>
            </motion.div>
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}
