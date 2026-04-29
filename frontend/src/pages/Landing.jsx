import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'
import { useApp } from '../context/AppContext'
import { CompassHero } from '../components/CompassHero'

export function Landing() {
  const navigate = useNavigate()
  const { reset } = useApp()
  const [jobCount, setJobCount] = useState(0)

  useEffect(() => {
    reset()
    // Fetch job count from health endpoint
    fetch(import.meta.env.VITE_API_URL ? `${import.meta.env.VITE_API_URL}/health` : 'http://localhost:8000/health')
      .then((r) => r.json())
      .then((d) => setJobCount(d.job_count))
      .catch(() => setJobCount(0))
  }, [reset])

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.3,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 24 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6, ease: [0.4, 0, 0.2, 1] },
    },
  }

  return (
    <div className="bg-black">
      {/* ── Scrollytelling Hero Section ── */}
      <CompassHero onCTAClick={() => navigate('/brain-dump')} />

      {/* ── Below-the-fold Content Section ── */}
      <div className="relative bg-gradient-to-b from-black via-[#080C14] to-[#080C14]">
        {/* Gradient transition strip */}
        <div className="h-32 bg-gradient-to-b from-black to-transparent" />

        <motion.div
          className="content-container text-center animated"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.8, ease: [0.4, 0, 0.2, 1] }}
        >
          <h2 className="text-3xl md:text-4xl font-inter font-bold text-white tracking-tight mb-4">
            How It Works
          </h2>
          <p className="text-white/50 font-inter text-lg mb-12 max-w-2xl mx-auto">
            Three simple steps to transform your experience into a job-ready roadmap
          </p>

          {/* Step Cards */}
          <motion.div
            className="grid-2"
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-50px' }}
          >
            <motion.div className="step-card" variants={itemVariants}>
              <div className="text-3xl mb-3">🧠</div>
              <h3>Brain Dump</h3>
              <p>Share everything: your projects, experience, skills, interests. No need to be formal.</p>
            </motion.div>

            <motion.div className="step-card" variants={itemVariants}>
              <div className="text-3xl mb-3">🎯</div>
              <h3>Find Matches</h3>
              <p>AI extracts your skills and finds the Sydney jobs that align with your profile.</p>
            </motion.div>

            <motion.div className="step-card" variants={itemVariants}>
              <div className="text-3xl mb-3">🗺️</div>
              <h3>Your Roadmap</h3>
              <p>Get a personalized 30-day plan to close skill gaps and land your next role.</p>
            </motion.div>
          </motion.div>

          <motion.div
            className="mt-12"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <button
              className="primary"
              onClick={() => navigate('/brain-dump')}
              style={{ fontSize: '1.1rem', padding: '14px 32px' }}
            >
              Get Started →
            </button>
          </motion.div>

          {jobCount > 0 && (
            <p
              style={{
                marginTop: '32px',
                color: 'var(--muted)',
                fontSize: '0.9rem',
              }}
            >
              Matching against {jobCount} Sydney job descriptions
            </p>
          )}
        </motion.div>
      </div>
    </div>
  )
}
