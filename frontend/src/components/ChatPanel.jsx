import { useEffect, useRef, useState } from 'react'
import { PromptInput, PromptInputTextarea, PromptInputActions, PromptInputAction } from './ui/prompt-input'
import { Button } from './ui/button'
import { ArrowUp } from 'lucide-react'

const QUESTIONS = [
  "What's your main career goal for the next 6 months? (e.g. land a data analyst role, switch industries, get promoted)",
  "How much time do you have to prepare before you want to be job-ready? (e.g. 2 weeks, 1 month, 3 months)",
  "How do you learn best? (e.g. hands-on projects, video courses, reading docs, structured bootcamp)",
  "How many hours per week can you realistically dedicate to upskilling?",
]

export function ChatPanel({ skills, onComplete }) {
  const [messages, setMessages] = useState(() => [
    {
      role: 'ai',
      text: `Great! I found ${skills.length} skill${skills.length !== 1 ? 's' : ''} in your profile. Let me ask a few quick questions so I can personalise your job matches and roadmap.`,
    },
    { role: 'ai', text: QUESTIONS[0] },
  ])
  const [currentQ, setCurrentQ] = useState(0)
  const [answers, setAnswers] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isComplete, setIsComplete] = useState(false)
  const [isWaiting, setIsWaiting] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = () => {
    if (!inputValue.trim() || isWaiting || isComplete) return

    const userMsg = { role: 'user', text: inputValue }
    setMessages((prev) => [...prev, userMsg])

    const newAnswers = [...answers, inputValue]
    setAnswers(newAnswers)
    setInputValue('')

    if (currentQ < QUESTIONS.length - 1) {
      setIsWaiting(true)

      setTimeout(() => {
        const nextQ = QUESTIONS[currentQ + 1]
        setMessages((prev) => [...prev, { role: 'ai', text: nextQ }])
        setCurrentQ(currentQ + 1)
        setIsWaiting(false)
      }, 400)
    } else {
      setIsComplete(true)
      const chatContext = [
        `Career goal: ${newAnswers[0]}`,
        `Preparation timeline: ${newAnswers[1]}`,
        `Preferred learning style: ${newAnswers[2]}`,
        `Hours per week available: ${newAnswers[3]}`,
      ].join('\n')

      setTimeout(() => {
        onComplete(chatContext)
      }, 300)
    }
  }

  return (
    <div className="mt-8 rounded-2xl border border-[var(--surface-secondary)] bg-[var(--surface)] p-6">
      <h3 className="mb-4 text-lg font-semibold text-[var(--text)]">Tell me a bit more...</h3>

      <div className="mb-4 max-h-[400px] overflow-y-auto space-y-3 pb-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`rounded-2xl px-4 py-3 text-sm ${
                msg.role === 'user'
                  ? 'max-w-xs bg-[var(--accent)] text-white rounded-br-none'
                  : 'w-full bg-[var(--surface-secondary)] text-[var(--text-secondary)] rounded-bl-none'
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
        {isWaiting && (
          <div className="flex justify-start">
            <div className="bg-[var(--surface-secondary)] text-[var(--text-secondary)] rounded-2xl rounded-bl-none px-4 py-3 text-sm">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-[var(--text-secondary)] rounded-full animate-pulse" />
                <div className="w-2 h-2 bg-[var(--text-secondary)] rounded-full animate-pulse delay-100" />
                <div className="w-2 h-2 bg-[var(--text-secondary)] rounded-full animate-pulse delay-200" />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <PromptInput
        value={inputValue}
        onValueChange={setInputValue}
        onSubmit={handleSubmit}
        disabled={isComplete || isWaiting}
        className="bg-[var(--surface-secondary)] border-[var(--surface-secondary)]"
      >
        <PromptInputTextarea
          placeholder="Type your answer..."
          disabled={isComplete || isWaiting}
          className="text-[var(--text)] placeholder-[var(--text-secondary)]"
        />

        <PromptInputActions className="flex items-center justify-end gap-2 pt-2">
          <PromptInputAction tooltip="Send message">
            <Button
              variant="default"
              size="icon"
              className="h-8 w-8 rounded-full bg-[var(--accent)] hover:bg-[var(--accent-dim)]"
              onClick={handleSubmit}
              disabled={isComplete || isWaiting || !inputValue.trim()}
            >
              <ArrowUp className="size-5" />
            </Button>
          </PromptInputAction>
        </PromptInputActions>
      </PromptInput>
    </div>
  )
}
