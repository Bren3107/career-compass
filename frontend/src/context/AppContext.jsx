import { createContext, useState, useContext, useCallback, useMemo } from 'react'

const AppContext = createContext()

export function AppProvider({ children }) {
  const [skills, setSkills] = useState([])
  const [matches, setMatches] = useState([])
  const [analysis, setAnalysis] = useState(null)
  const [brainDump, setBrainDump] = useState('')
  const [pdfText, setPdfText] = useState('')

  const reset = useCallback(() => {
    setSkills([])
    setMatches([])
    setAnalysis(null)
    setBrainDump('')
    setPdfText('')
  }, [])

  const value = useMemo(() => ({
    skills,
    setSkills,
    matches,
    setMatches,
    analysis,
    setAnalysis,
    brainDump,
    setBrainDump,
    pdfText,
    setPdfText,
    reset,
  }), [skills, matches, analysis, brainDump, pdfText, reset])

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}

export function useApp() {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useApp must be used within an AppProvider')
  }
  return context
}

