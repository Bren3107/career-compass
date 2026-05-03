import { createContext, useState, useContext, useCallback, useMemo } from 'react'

const AppContext = createContext()

export function AppProvider({ children }) {
  const [skills, setSkills] = useState([])
  const [matches, setMatches] = useState([])
  const [analysis, setAnalysis] = useState(null)
  const [brainDump, setBrainDump] = useState('')
  const [pdfText, setPdfText] = useState('')
  const [selectedJob, setSelectedJob] = useState(null)
  const [selectedJobIndex, setSelectedJobIndex] = useState(null)
  const [chatContext, setChatContext] = useState(null)

  const reset = useCallback(() => {
    setSkills([])
    setMatches([])
    setAnalysis(null)
    setBrainDump('')
    setPdfText('')
    setSelectedJob(null)
    setSelectedJobIndex(null)
    setChatContext(null)
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
    selectedJob,
    setSelectedJob,
    selectedJobIndex,
    setSelectedJobIndex,
    chatContext,
    setChatContext,
    reset,
  }), [skills, matches, analysis, brainDump, pdfText, selectedJob, selectedJobIndex, chatContext, reset])

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}

export function useApp() {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useApp must be used within an AppProvider')
  }
  return context
}

