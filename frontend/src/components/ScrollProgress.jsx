import { useScroll, motion, useTransform } from 'framer-motion'
import { useEffect, useState } from 'react'

/**
 * Debug scroll progress bar at top of viewport.
 * Only shows when ?debug=true is in the URL.
 */
export function ScrollProgress({ containerRef }) {
  const [showDebug, setShowDebug] = useState(false)

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    setShowDebug(params.get('debug') === 'true')
  }, [])

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start start', 'end end'],
  })

  const width = useTransform(scrollYProgress, [0, 1], ['0%', '100%'])

  if (!showDebug) return null

  return (
    <div className="fixed top-0 left-0 right-0 h-1 z-[100] bg-white/10">
      <motion.div
        className="h-full bg-gradient-to-r from-electric-blue to-purple-accent"
        style={{ width }}
      />
      <motion.div
        className="absolute top-2 right-4 text-white/60 text-xs font-mono bg-black/60 px-2 py-1 rounded"
      >
        <ScrollPercentage scrollYProgress={scrollYProgress} />
      </motion.div>
    </div>
  )
}

function ScrollPercentage({ scrollYProgress }) {
  const [percent, setPercent] = useState(0)

  useEffect(() => {
    const unsubscribe = scrollYProgress.on('change', (v) => {
      setPercent(Math.round(v * 100))
    })
    return unsubscribe
  }, [scrollYProgress])

  return <span>{percent}%</span>
}
