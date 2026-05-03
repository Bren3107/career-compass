import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import { AppProvider } from './context/AppContext'
import { LinearBackground } from './components/LinearBackground'
import { Header } from './components/Header'
import { Landing } from './pages/Landing'
import { BrainDump } from './pages/BrainDump'
import { JobMatches } from './pages/JobMatches'
import { Roadmap } from './pages/Roadmap'
import { Optimize } from './pages/Optimize'

function AnimatedRoutes() {
  const location = useLocation()

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<Landing />} />
        <Route path="/brain-dump" element={<BrainDump />} />
        <Route path="/matches" element={<JobMatches />} />
        <Route path="/roadmap" element={<Roadmap />} />
        <Route path="/optimize" element={<Optimize />} />
      </Routes>
    </AnimatePresence>
  )
}

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <LinearBackground />
        <Header />
        <AnimatedRoutes />
      </BrowserRouter>
    </AppProvider>
  )
}

