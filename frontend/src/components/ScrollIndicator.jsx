import { motion } from 'framer-motion'

/**
 * Animated scroll indicator chevron.
 * Fades out as user begins scrolling (controlled by parent via `visible` prop).
 */
export function ScrollIndicator({ visible = true }) {
  return (
    <motion.div
      className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 z-20"
      initial={{ opacity: 0 }}
      animate={{ opacity: visible ? 1 : 0 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
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
  )
}
