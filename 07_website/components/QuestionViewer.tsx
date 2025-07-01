'use client'

import { useState } from 'react'
import { Question } from '@/lib/questions'
import AnswerCard from './AnswerCard'
import Navigation from './Navigation'

interface QuestionViewerProps {
  questions: Question[]
  onComplete?: (answers: Record<string, string>) => void
  showResults?: boolean
}

export default function QuestionViewer({ 
  questions, 
  onComplete,
  showResults = false 
}: QuestionViewerProps) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string>>({})
  const [showContext, setShowContext] = useState(false)

  const currentQuestion = questions[currentIndex]
  const isLastQuestion = currentIndex === questions.length - 1

  const handleSelectAnswer = (answerId: string) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [currentQuestion.id]: answerId
    }))
  }

  const handleNext = () => {
    if (isLastQuestion && onComplete) {
      onComplete(selectedAnswers)
    } else {
      setCurrentIndex(prev => Math.min(prev + 1, questions.length - 1))
      setShowContext(false)
    }
  }

  const handlePrevious = () => {
    setCurrentIndex(prev => Math.max(prev - 1, 0))
    setShowContext(false)
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Question Section */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 mb-6">
        {currentQuestion.category && (
          <div className="text-sm font-medium text-blue-600 mb-4">
            {currentQuestion.category}
          </div>
        )}
        
        <h2 className="text-2xl font-medium text-gray-900 mb-6 leading-relaxed">
          {currentQuestion.question}
        </h2>

        {currentQuestion.context && (
          <div className="mt-4">
            <button
              onClick={() => setShowContext(!showContext)}
              className="text-sm text-blue-600 hover:text-blue-700 font-medium transition-colors"
            >
              {showContext ? 'Hide' : 'Show'} Context
            </button>
            
            {showContext && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg text-gray-700 text-sm leading-relaxed">
                {currentQuestion.context}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Answer Options */}
      <div className="space-y-3 mb-8">
        {currentQuestion.options.map((option) => (
          <AnswerCard
            key={option.id}
            option={option}
            isSelected={selectedAnswers[currentQuestion.id] === option.id}
            onSelect={handleSelectAnswer}
            showResult={showResults}
          />
        ))}
      </div>

      {/* Navigation */}
      <Navigation
        currentIndex={currentIndex}
        totalQuestions={questions.length}
        onPrevious={handlePrevious}
        onNext={handleNext}
        canProceed={!!selectedAnswers[currentQuestion.id]}
        isLastQuestion={isLastQuestion}
      />
    </div>
  )
}