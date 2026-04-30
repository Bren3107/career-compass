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
        staggerChildren: 0.12,
        delayChildren: 0.2,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5, ease: [0.4, 0, 0.2, 1] },
    },
  }

  const steps = [
    {
      num: '01',
      title: 'Brain Dump',
      desc: 'Share everything — projects, experience, skills, interests. No need to be formal.',
    },
    {
      num: '02',
      title: 'Find Matches',
      desc: 'AI extracts your skills and finds the Sydney jobs that align with your profile.',
    },
    {
      num: '03',
      title: 'Your Roadmap',
      desc: 'Get a personalized 30-day plan to close skill gaps and land your next role.',
    },
  ]

  return (
    <div className="bg-transparent">
      {/* ── Scrollytelling Hero Section ── */}
      <CompassHero onCTAClick={() => navigate('/brain-dump')} />

      {/* ── Below-the-fold Content Section ── */}
      <div className="relative">
        {/* Gradient transition from hero black to page background */}
        <div
          className="h-40"
          style={{
            background: 'linear-gradient(to bottom, #000000 0%, var(--bg) 100%)',
          }}
        />

        {/* Section gradient glow */}
        <div
          className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] pointer-events-none"
          style={{
            background: 'radial-gradient(ellipse at center, rgba(94,106,210,0.06) 0%, transparent 70%)',
            filter: 'blur(60px)',
          }}
        />

        <div className="max-w-4xl mx-auto px-6 pb-24">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-80px' }}
            transition={{ duration: 0.7, ease: [0.4, 0, 0.2, 1] }}
          >
            <p
              className="text-sm font-medium tracking-widest uppercase mb-4"
              style={{ color: 'var(--accent)' }}
            >
              How it works
            </p>
            <h2
              className="text-3xl md:text-4xl font-semibold text-white tracking-tight mb-4"
              style={{ letterSpacing: '-0.03em' }}
            >
              Three steps to your career path
            </h2>
            <p className="text-base max-w-xl mx-auto" style={{ color: 'var(--text-secondary)' }}>
              Transform your experience into a personalized, actionable roadmap
            </p>
          </motion.div>

          {/* Step Cards */}
          <motion.div
            className="grid grid-cols-1 md:grid-cols-3 gap-4"
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-50px' }}
          >
            {steps.map((step) => (
              <motion.div
                key={step.num}
                className="step-card group"
                variants={itemVariants}
              >
                <span
                  className="inline-block text-xs font-semibold tracking-wider mb-4"
                  style={{ color: 'var(--accent)' }}
                >
                  {step.num}
                </span>
                <h3>{step.title}</h3>
                <p>{step.desc}</p>
              </motion.div>
            ))}
          </motion.div>

          {/* CTA */}
          <motion.div
            className="mt-16 text-center"
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <button
              className="primary"
              onClick={() => navigate('/brain-dump')}
              style={{ fontSize: '0.9rem', padding: '12px 28px' }}
            >
              Get Started →
            </button>
          </motion.div>

          {jobCount > 0 && (
            <p className="text-center mt-8 text-sm" style={{ color: 'var(--muted)' }}>
              Matching against {jobCount} Sydney job descriptions
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
