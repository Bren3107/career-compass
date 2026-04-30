/**
 * LinearBackground — Premium dark background inspired by Linear.app's 2022 releases page.
 *
 * Layering order (back → front):
 *   1. Solid #0D0D0D base
 *   2. SVG repeating dot pattern (subtle white dots at low opacity)
 *   3. Radial gradient orbs (blue, purple, indigo, cyan) for depth + color
 *   4. Noise texture overlay (fractalNoise SVG filter for realism)
 *   5. Radial vignette (focus attention toward center)
 *
 * All effects are pure CSS / inline SVG — zero JavaScript animation.
 * Fixed-positioned at z-index -50 so it sits behind every layer of content.
 */
export function LinearBackground() {
  return (
    <div
      className="fixed inset-0 overflow-hidden pointer-events-none"
      style={{ zIndex: -50 }}
      aria-hidden="true"
    >
      {/* ── Layer 1: Solid dark base ───────────────────────────── */}
      <div className="absolute inset-0 bg-[#000212]" />

      {/* ── Layer 2: SVG dot pattern ──────────────────────────── */}
      <svg
        className="absolute inset-0 w-full h-full"
        style={{ opacity: 0.35 }}
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <pattern
            id="linear-dot-pattern"
            x="0"
            y="0"
            width="32"
            height="32"
            patternUnits="userSpaceOnUse"
          >
            <circle cx="2" cy="2" r="0.8" fill="rgba(255,255,255,0.06)" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#linear-dot-pattern)" />
      </svg>

      {/* ── Layer 3: Gradient orbs ────────────────────────────── */}
      {/* Primary blue glow — top-left, extends off-canvas for natural falloff */}
      <div
        className="absolute rounded-full
          -top-40 left-[10%]
          w-[400px] h-[400px]
          md:w-[600px] md:h-[600px]
          lg:w-[800px] lg:h-[800px]"
        style={{
          background: 'radial-gradient(circle, rgba(94,106,210,0.08) 0%, transparent 70%)',
          filter: 'blur(120px)',
        }}
      />

      {/* Purple glow — mid-right */}
      <div
        className="absolute rounded-full
          top-[30%] -right-20
          w-[350px] h-[350px]
          md:w-[500px] md:h-[500px]
          lg:w-[600px] lg:h-[600px]"
        style={{
          background: 'radial-gradient(circle, rgba(94,106,210,0.06) 0%, transparent 70%)',
          filter: 'blur(100px)',
        }}
      />

      {/* Indigo glow — bottom-center */}
      <div
        className="absolute rounded-full
          bottom-[20%] left-[40%]
          w-[400px] h-[400px]
          md:w-[550px] md:h-[550px]
          lg:w-[700px] lg:h-[700px]"
        style={{
          background: 'radial-gradient(circle, rgba(59,130,246,0.05) 0%, transparent 70%)',
          filter: 'blur(120px)',
        }}
      />

      {/* Secondary cyan accent — lower-left for variety */}
      <div
        className="absolute rounded-full
          top-[60%] left-[15%]
          w-[250px] h-[250px]
          md:w-[350px] md:h-[350px]
          lg:w-[400px] lg:h-[400px]"
        style={{
          background: 'radial-gradient(circle, rgba(94,106,210,0.04) 0%, transparent 70%)',
          filter: 'blur(80px)',
        }}
      />

      {/* ── Layer 4: Noise texture overlay ────────────────────── */}
      <div
        className="absolute inset-0 mix-blend-overlay"
        style={{
          opacity: 0.02,
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
          backgroundSize: '256px 256px',
        }}
      />

      {/* ── Layer 5: Radial vignette ──────────────────────────── */}
      <div
        className="absolute inset-0"
        style={{
          background:
            'radial-gradient(ellipse at center, transparent 0%, transparent 40%, rgba(0,0,0,0.5) 100%)',
        }}
      />
    </div>
  )
}
