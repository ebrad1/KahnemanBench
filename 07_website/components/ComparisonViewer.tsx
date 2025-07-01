'use client'

import { useState, useEffect, useCallback } from 'react'
import { KahnemanQuestion } from '@/lib/types'
import ResponseCard from './ResponseCard'

interface ComparisonViewerProps {
  questions: KahnemanQuestion[]
  onComplete: (selections: Record<string, string>) => void
  mode: 'public' | 'expert'
}

export default function ComparisonViewer({ 
  questions, 
  onComplete,
  mode 
}: ComparisonViewerProps) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [selections, setSelections] = useState<Record<string, string>>({})
  const [showContext, setShowContext] = useState(false)

  const currentQuestion = questions[currentIndex]
  const isLastQuestion = currentIndex === questions.length - 1
  const hasSelection = !!selections[currentQuestion.question_id]

  // Randomize response order for each question (but keep it consistent per session)
  const [responseOrder, setResponseOrder] = useState<Record<string, string[]>>({})
  
  const handleSelectResponse = useCallback((responseId: string) => {
    setSelections(prev => ({
      ...prev,
      [currentQuestion.question_id]: responseId
    }))
  }, [currentQuestion.question_id])

  const handleNext = useCallback(() => {
    if (isLastQuestion) {
      onComplete(selections)
    } else {
      setCurrentIndex(prev => prev + 1)
      setShowContext(false)
    }
  }, [isLastQuestion, onComplete, selections])

  const handlePrevious = useCallback(() => {
    setCurrentIndex(prev => Math.max(0, prev - 1))
    setShowContext(false)
  }, [])

  useEffect(() => {
    const newOrder: Record<string, string[]> = {}
    questions.forEach(q => {
      const ids = q.responses.map(r => r.response_id)
      // Simple shuffle
      for (let i = ids.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [ids[i], ids[j]] = [ids[j], ids[i]]
      }
      newOrder[q.question_id] = ids
    })
    setResponseOrder(newOrder)
  }, [questions])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Only handle if not focused on an input
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return
      }

      const orderedResponses = responseOrder[currentQuestion.question_id]
      if (!orderedResponses) return

      switch (e.key) {
        case 'ArrowLeft':
          e.preventDefault()
          handlePrevious()
          break
        case 'ArrowRight':
          e.preventDefault()
          if (hasSelection) {
            handleNext()
          }
          break
        case '1':
        case '2': 
        case '3':
        case 'a':
        case 'A':
        case 'b':
        case 'B':
        case 'c':
        case 'C':
          e.preventDefault()
          const index = ['1', 'a', 'A'].includes(e.key) ? 0 : 
                       ['2', 'b', 'B'].includes(e.key) ? 1 : 2
          if (index < orderedResponses.length) {
            handleSelectResponse(orderedResponses[index])
          }
          break
        case 'Enter':
          e.preventDefault()
          if (hasSelection) {
            handleNext()
          }
          break
        case 'c':
          if (e.ctrlKey || e.metaKey) break // Allow copy
          e.preventDefault()
          setShowContext(!showContext)
          break
      }
    }

    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [currentIndex, currentQuestion, hasSelection, responseOrder, showContext, handleNext, handleSelectResponse, handlePrevious])

  const orderedResponses = responseOrder[currentQuestion.question_id]
    ? responseOrder[currentQuestion.question_id].map(id => 
        currentQuestion.responses.find(r => r.response_id === id)!
      )
    : currentQuestion.responses

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Question Section */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <div className="max-w-4xl mx-auto">
          {mode === 'expert' && (
            <div className="text-sm text-gray-500 mb-2">
              Question ID: {currentQuestion.question_id}
            </div>
          )}
          
          <h2 className="text-xl font-medium text-gray-900 leading-relaxed mb-4">
            {currentQuestion.question_text}
          </h2>

          {currentQuestion.summarised_context && (
            <div className="mt-4">
              <button
                onClick={() => setShowContext(!showContext)}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium transition-colors inline-flex items-center"
              >
                {showContext ? 'Hide' : 'Show'} Context
                <svg 
                  className={`ml-1 w-4 h-4 transition-transform ${showContext ? 'rotate-180' : ''}`} 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              {showContext && (
                <div className="mt-3 p-4 bg-gray-50 rounded-lg text-sm text-gray-700 leading-relaxed">
                  {currentQuestion.summarised_context}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Instruction */}
      <div className="text-center mb-6">
        <p className="text-gray-600 mb-2">
          Which response sounds most like Daniel Kahneman?
        </p>
        <p className="text-xs text-gray-500">
          Use keyboard shortcuts: A/B/C to select responses, ← → to navigate, Enter to continue, C to toggle context
        </p>
      </div>

      {/* Response Cards */}
      <div className={`grid gap-4 mb-8 ${
        orderedResponses.length === 2 ? 'md:grid-cols-2' : 'md:grid-cols-3'
      }`}>
        {orderedResponses.map((response, index) => (
          <ResponseCard
            key={response.response_id}
            response={response}
            isSelected={selections[currentQuestion.question_id] === response.response_id}
            onSelect={handleSelectResponse}
            responseLabel={`Response ${String.fromCharCode(65 + index)}`}
            showSource={false} // Never show source in public/expert mode
          />
        ))}
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between mb-8">
        <button
          onClick={handlePrevious}
          disabled={currentIndex === 0}
          className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Previous
        </button>

        <div className="flex items-center space-x-3">
          <div className="flex space-x-1">
            {questions.slice(0, 10).map((_, i) => (
              <div
                key={i}
                className={`w-2 h-2 rounded-full transition-all ${
                  i === currentIndex 
                    ? 'bg-blue-600 w-6' 
                    : i < currentIndex 
                    ? selections[questions[i].question_id] ? 'bg-green-400' : 'bg-blue-400'
                    : 'bg-gray-300'
                }`}
                title={`Question ${i + 1}${i < currentIndex ? (selections[questions[i].question_id] ? ' (answered)' : ' (skipped)') : ''}`}
              />
            ))}
            {questions.length > 10 && (
              <span className="text-sm text-gray-500 ml-2">...</span>
            )}
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-600">
              {currentIndex + 1} of {questions.length}
            </div>
            <div className="text-xs text-gray-500">
              {Object.keys(selections).length} answered
            </div>
          </div>
        </div>

        <button
          onClick={handleNext}
          disabled={!hasSelection}
          className={`inline-flex items-center px-4 py-2 text-sm font-medium rounded-lg transition-all ${
            hasSelection
              ? isLastQuestion 
                ? 'text-white bg-green-600 hover:bg-green-700'
                : 'text-white bg-blue-600 hover:bg-blue-700'
              : 'text-gray-400 bg-gray-100 cursor-not-allowed'
          }`}
        >
          {isLastQuestion ? 'Complete' : 'Next'}
          <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  )
}
