/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'electric-blue': '#3B82F6',
        'purple-accent': '#A855F7',
        'hero-black': '#000000',
      },
      fontFamily: {
        'inter': ['Inter', 'system-ui', 'sans-serif'],
        'geist': ['Geist', 'system-ui', 'sans-serif'],
      },
      keyframes: {
        'glow-pulse': {
          '0%, 100%': { boxShadow: '0 0 20px rgba(59, 130, 246, 0.3), 0 0 40px rgba(168, 85, 247, 0.2)' },
          '50%': { boxShadow: '0 0 30px rgba(59, 130, 246, 0.5), 0 0 60px rgba(168, 85, 247, 0.3)' },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'bounce-down': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(8px)' },
        },
        'compass-spin': {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      animation: {
        'glow-pulse': 'glow-pulse 3s ease-in-out infinite',
        'float': 'float 3s ease-in-out infinite',
        'bounce-down': 'bounce-down 2s ease-in-out infinite',
        'compass-spin': 'compass-spin 2s linear infinite',
        'shimmer': 'shimmer 2s linear infinite',
      },
    },
  },
  plugins: [],
}
