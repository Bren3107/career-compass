import { useRef, useEffect, useCallback, useState, useMemo } from 'react'
import { useScroll, useTransform, useSpring, motion, AnimatePresence } from 'framer-motion'
import { useImageSequence } from '../hooks/useImageSequence'
import { ScrollIndicator } from './ScrollIndicator'
import { ScrollProgress } from './ScrollProgress'

// ─── Loading Overlay ────────────────────────────────────────────────
function LoadingOverlay({ progress }) {
  return (
    <motion.div
      className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black"
      initial={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.8, ease: 'easeOut' }}
    >
      {/* Compass spinner */}
      <div className="relative w-20 h-20 mb-8">
        <svg viewBox="0 0 80 80" className="w-full h-full animate-compass-spin">
          <circle
            cx="40" cy="40" r="36"
            fill="none"
            stroke="rgba(59, 130, 246, 0.2)"
            strokeWidth="2"
          />
          <circle
            cx="40" cy="40" r="36"
            fill="none"
            stroke="url(#loadingGradient)"
            strokeWidth="2"
            strokeDasharray="226"
            strokeDashoffset={226 - (226 * progress) / 100}
            strokeLinecap="round"
            className="transition-all duration-300"
          />
          {/* Compass needle */}
          <line
            x1="40" y1="12" x2="40" y2="40"
            stroke="#3B82F6"
            strokeWidth="2.5"
            strokeLinecap="round"
          />
          <line
            x1="40" y1="40" x2="40" y2="68"
            stroke="#A855F7"
            strokeWidth="2.5"
            strokeLinecap="round"
          />
          <circle cx="40" cy="40" r="3" fill="white" />
          <defs>
            <linearGradient id="loadingGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#3B82F6" />
              <stop offset="100%" stopColor="#A855F7" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      {/* Progress bar */}
      <div className="w-64 h-1.5 bg-white/10 rounded-full overflow-hidden mb-4">
        <motion.div
          className="h-full bg-gradient-to-r from-electric-blue to-purple-accent rounded-full"
          initial={{ width: '0%' }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
        />
      </div>

      {/* Text */}
      <p className="text-white/50 text-sm font-inter tracking-wider">
        Loading experience... {progress}%
      </p>
    </motion.div>
  )
}

// ─── CTA Button ─────────────────────────────────────────────────────
function CTAButton({ onClick }) {
  return (
    <motion.button
      onClick={onClick}
      className="
        relative px-8 py-4 rounded-xl font-inter font-semibold text-lg text-white
        bg-gradient-to-r from-electric-blue to-purple-accent
        shadow-lg shadow-electric-blue/25
        transition-all duration-300
        hover:shadow-xl hover:shadow-electric-blue/40
        focus:outline-none focus:ring-2 focus:ring-electric-blue/50 focus:ring-offset-2 focus:ring-offset-black
        pointer-events-auto cursor-pointer
      "
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.98 }}
      aria-label="Start your career journey"
      id="cta-start-journey"
    >
      <span className="relative z-10">Start Your Journey</span>
      {/* Glow effect */}
      <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-electric-blue to-purple-accent opacity-0 hover:opacity-20 blur-xl transition-opacity duration-500" />
    </motion.button>
  )
}

// ─── Helper: create a smooth trapezoidal opacity curve from scroll progress ─
// Returns a MotionValue mapped from scrollYProgress
function useTextOpacity(scrollYProgress, fadeIn, peakStart, peakEnd, fadeOut) {
  return useTransform(
    scrollYProgress,
    [fadeIn, peakStart, peakEnd, fadeOut],
    [0, 1, 1, 0]
  )
}

// ─── Particle Field (CSS-based, lightweight) ────────────────────────
const PARTICLES = Array.from({ length: 20 }, (_, i) => ({
  id: i,
  left: `${10 + (i * 4.2) % 80}%`,
  top: `${5 + (i * 7.3) % 90}%`,
  duration: `${2 + (i % 3)}s`,
  delay: `${i * 0.2}s`,
  scale: 0.5 + (i % 4) * 0.3,
}))

function ParticleField({ scrollYProgress }) {
  const opacity = useTransform(scrollYProgress, [0, 0.5, 1], [0, 0.4, 0.3])

  return (
    <motion.div
      className="absolute inset-0 pointer-events-none z-[5]"
      style={{ opacity }}
    >
      {PARTICLES.map((p) => (
        <div
          key={p.id}
          className="absolute w-1 h-1 rounded-full bg-electric-blue/40"
          style={{
            left: p.left,
            top: p.top,
            animation: `float ${p.duration} ease-in-out ${p.delay} infinite`,
            transform: `scale(${p.scale})`,
          }}
        />
      ))}
    </motion.div>
  )
}

// ─── Main CompassHero Component ─────────────────────────────────────
export function CompassHero({ onCTAClick }) {
  const containerRef = useRef(null)
  const canvasRef = useRef(null)
  const lastDrawnFrameRef = useRef(-1)
  const rafRef = useRef(null)
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false)

  // Check for reduced motion preference
  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)')
    setPrefersReducedMotion(mq.matches)
    const handler = (e) => setPrefersReducedMotion(e.matches)
    mq.addEventListener('change', handler)
    return () => mq.removeEventListener('change', handler)
  }, [])

  // Image sequence
  const { getFrame, progress, isLoaded, totalFrames } = useImageSequence(
    '/compass-sequence/',
    240,
    'frame_',
    '.jpg'
  )

  // Scroll tracking
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start start', 'end end'],
  })

  // Map scroll to frame index (0-indexed, 0 to 239)
  const rawFrameIndex = useTransform(scrollYProgress, [0, 1], [0, totalFrames - 1])

  // Smooth spring for buttery frame transitions
  const smoothFrameIndex = useSpring(rawFrameIndex, {
    stiffness: 300,
    damping: 30,
    mass: 0.5,
  })

  // ─── Text Opacities (ALL via useTransform — zero React re-renders) ───
  const text1Opacity = useTextOpacity(scrollYProgress, 0.0, 0.04, 0.12, 0.17)
  const text2Opacity = useTextOpacity(scrollYProgress, 0.18, 0.23, 0.35, 0.42)
  const text3aOpacity = useTextOpacity(scrollYProgress, 0.43, 0.47, 0.58, 0.67)
  const text3bOpacity = useTextOpacity(scrollYProgress, 0.45, 0.49, 0.58, 0.67)
  const text3cOpacity = useTextOpacity(scrollYProgress, 0.47, 0.51, 0.58, 0.67)
  const text4Opacity = useTextOpacity(scrollYProgress, 0.68, 0.73, 0.85, 0.92)
  const ctaOpacity = useTextOpacity(scrollYProgress, 0.88, 0.93, 1.0, 1.0)
  const scrollIndicatorOpacity = useTransform(scrollYProgress, [0, 0.08], [1, 0])

  // Lock scroll during loading
  useEffect(() => {
    if (!isLoaded) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [isLoaded])

  // ─── Canvas Drawing ──────────────────────────────────────────
  const drawFrame = useCallback(
    (index) => {
      const canvas = canvasRef.current
      if (!canvas) return

      const ctx = canvas.getContext('2d')
      if (!ctx) return

      const frame = getFrame(index)
      if (!frame) return

      const roundedIndex = Math.round(index)
      if (roundedIndex === lastDrawnFrameRef.current) return
      lastDrawnFrameRef.current = roundedIndex

      // Match canvas resolution to display size * devicePixelRatio
      const dpr = window.devicePixelRatio || 1
      const displayWidth = canvas.clientWidth
      const displayHeight = canvas.clientHeight

      if (canvas.width !== displayWidth * dpr || canvas.height !== displayHeight * dpr) {
        canvas.width = displayWidth * dpr
        canvas.height = displayHeight * dpr
        ctx.scale(dpr, dpr)
      }

      // Fill black background first (prevents any flash)
      ctx.fillStyle = '#000000'
      ctx.fillRect(0, 0, displayWidth, displayHeight)

      // Draw with object-fit: contain behavior
      const imgAspect = frame.naturalWidth / frame.naturalHeight
      const canvasAspect = displayWidth / displayHeight

      let drawWidth, drawHeight, offsetX, offsetY

      if (imgAspect > canvasAspect) {
        drawWidth = displayWidth
        drawHeight = displayWidth / imgAspect
        offsetX = 0
        offsetY = (displayHeight - drawHeight) / 2
      } else {
        drawHeight = displayHeight
        drawWidth = displayHeight * imgAspect
        offsetX = (displayWidth - drawWidth) / 2
        offsetY = 0
      }

      ctx.drawImage(frame, offsetX, offsetY, drawWidth, drawHeight)
    },
    [getFrame]
  )

  // Animation loop — subscribe to the spring MotionValue
  useEffect(() => {
    if (!isLoaded) return

    // If prefers reduced motion, just draw the last frame
    if (prefersReducedMotion) {
      drawFrame(totalFrames - 1)
      return
    }

    const unsubscribe = smoothFrameIndex.on('change', (v) => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
      rafRef.current = requestAnimationFrame(() => {
        drawFrame(v)
      })
    })

    // Draw initial frame
    drawFrame(0)

    return () => {
      unsubscribe()
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
    }
  }, [isLoaded, smoothFrameIndex, drawFrame, prefersReducedMotion, totalFrames])

  // Handle resize
  useEffect(() => {
    const handleResize = () => {
      lastDrawnFrameRef.current = -1
      const currentFrame = Math.round(smoothFrameIndex.get())
      drawFrame(currentFrame)
    }
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [drawFrame, smoothFrameIndex])

  return (
    <>
      {/* Loading overlay with AnimatePresence for exit animation */}
      <AnimatePresence>
        {!isLoaded && <LoadingOverlay progress={progress} />}
      </AnimatePresence>

      {/* Debug scroll progress */}
      <ScrollProgress containerRef={containerRef} />

      {/* Main scroll container */}
      <section
        ref={containerRef}
        className="relative bg-black h-[400vh] md:h-[450vh] lg:h-[500vh]"
        aria-label="Career Compass hero animation"
      >
        {/* Sticky viewport */}
        <div className="sticky top-0 h-screen w-full overflow-hidden bg-black">
          {/* Canvas */}
          <canvas
            ref={canvasRef}
            className="absolute inset-0 w-full h-full"
            role="img"
            aria-label="Animated compass visualization showing skills and career opportunities activating as you scroll"
          />

          {/* CSS Particle overlay */}
          <ParticleField scrollYProgress={scrollYProgress} />

          {/* ── Text Stage 1: "Lost in possibilities?" ── */}
          <motion.div
            className="absolute inset-0 flex items-center justify-center z-10 pointer-events-none"
            style={{ opacity: text1Opacity }}
          >
            <div className="backdrop-blur-sm bg-black/30 rounded-2xl px-6 py-4 md:px-10 md:py-6 border border-white/5">
              <h1 className="text-4xl sm:text-5xl md:text-7xl font-inter font-bold text-white tracking-tight text-center leading-tight">
                Lost in{' '}
                <span className="bg-gradient-to-r from-electric-blue to-purple-accent bg-clip-text text-transparent">
                  possibilities
                </span>
                ?
              </h1>
            </div>
          </motion.div>

          {/* ── Text Stage 2: "Turn your experiences..." ── */}
          <motion.div
            className="absolute inset-y-0 left-4 md:left-12 lg:left-20 flex items-center z-10 pointer-events-none max-w-lg"
            style={{ opacity: text2Opacity }}
          >
            <div className="backdrop-blur-sm bg-black/30 rounded-2xl px-6 py-4 md:px-10 md:py-6 border border-white/5">
              <h2 className="text-2xl sm:text-3xl md:text-5xl font-inter font-bold text-white tracking-tight leading-snug">
                Turn your experiences into{' '}
                <span className="bg-gradient-to-r from-electric-blue to-purple-accent bg-clip-text text-transparent">
                  opportunities
                </span>
              </h2>
            </div>
          </motion.div>

          {/* ── Text Stage 3: Feature lines (staggered) ── */}
          <div className="absolute inset-y-0 right-4 md:right-12 lg:right-20 flex flex-col justify-center items-end gap-4 md:gap-6 z-10 pointer-events-none max-w-md">
            <motion.div
              className="backdrop-blur-sm bg-black/30 rounded-xl px-5 py-3 border border-white/5"
              style={{ opacity: text3aOpacity }}
            >
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-electric-blue shadow-lg shadow-electric-blue/50" />
                <span className="text-lg sm:text-xl md:text-2xl font-inter font-semibold text-white">
                  AI-powered skill extraction
                </span>
              </div>
            </motion.div>

            <motion.div
              className="backdrop-blur-sm bg-black/30 rounded-xl px-5 py-3 border border-white/5"
              style={{ opacity: text3bOpacity }}
            >
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-purple-accent shadow-lg shadow-purple-accent/50" />
                <span className="text-lg sm:text-xl md:text-2xl font-inter font-semibold text-white">
                  Sydney job market matching
                </span>
              </div>
            </motion.div>

            <motion.div
              className="backdrop-blur-sm bg-black/30 rounded-xl px-5 py-3 border border-white/5"
              style={{ opacity: text3cOpacity }}
            >
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-gradient-to-r from-electric-blue to-purple-accent shadow-lg shadow-electric-blue/50" />
                <span className="text-lg sm:text-xl md:text-2xl font-inter font-semibold text-white">
                  Personalized 30-day roadmaps
                </span>
              </div>
            </motion.div>
          </div>

          {/* ── Text Stage 4: "Your career path starts here" ── */}
          <motion.div
            className="absolute inset-0 flex items-center justify-center z-10 pointer-events-none"
            style={{ opacity: text4Opacity }}
          >
            <div className="backdrop-blur-sm bg-black/30 rounded-2xl px-6 py-4 md:px-10 md:py-6 border border-white/5">
              <h2 className="text-3xl sm:text-4xl md:text-6xl font-inter font-extrabold text-white tracking-tight text-center leading-tight">
                Your career path{' '}
                <span className="bg-gradient-to-r from-electric-blue via-purple-accent to-electric-blue bg-clip-text text-transparent">
                  starts here
                </span>
              </h2>
            </div>
          </motion.div>

          {/* ── Text Stage 5: CTA ── */}
          <motion.div
            className="absolute inset-0 flex flex-col items-center justify-center gap-6 z-10"
            style={{ opacity: ctaOpacity }}
          >
            <div className="backdrop-blur-sm bg-black/20 rounded-2xl px-8 py-8 border border-white/5 flex flex-col items-center gap-6">
              <CTAButton onClick={onCTAClick} />
              <p className="text-white/40 text-sm font-inter tracking-wide">
                Trusted by{' '}
                <span className="text-white/60 font-semibold">500+</span>{' '}
                Sydney students
              </p>
            </div>
          </motion.div>

          {/* ── Scroll indicator ── */}
          <motion.div
            className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 z-20"
            style={{ opacity: scrollIndicatorOpacity }}
            aria-hidden="true"
          >
            <span className="text-white/50 text-sm font-inter tracking-widest uppercase">
              Scroll to explore
            </span>
            <div className="animate-bounce-down">
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="text-white/40"
              >
                <path d="M7 13l5 5 5-5" />
                <path d="M7 7l5 5 5-5" />
              </svg>
            </div>
          </motion.div>
        </div>
      </section>
    </>
  )
}
