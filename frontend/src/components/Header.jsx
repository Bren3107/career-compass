import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export function Header() {
  const navigate = useNavigate()
  const [isHovered, setIsHovered] = useState(false)
  const [isFocused, setIsFocused] = useState(false)

  return (
    <header
      style={{
        padding: '16px 24px',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
      }}
    >
      <button
        onClick={() => navigate('/')}
        aria-label="Career Compass home"
        style={{
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          padding: '8px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          color: 'var(--accent)',
          fontSize: '1rem',
          fontWeight: 500,
          transition: 'opacity 0.2s',
          opacity: isHovered ? '0.8' : '1',
          outline: isFocused ? '2px solid var(--accent)' : '2px solid transparent',
        }}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        title="Go to home page"
      >
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          aria-hidden="true"
        >
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
          <polyline points="9 22 9 12 15 12 15 22" />
        </svg>
        <span>Career Compass</span>
      </button>
    </header>
  )
}
