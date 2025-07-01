'use client'

import { useState } from 'react'
import QuestionViewer from '@/components/QuestionViewer'
import { sampleQuestions } from '@/lib/questions'

export default function TryPage() {
  const [showResults, setShowResults] = useState(false)
  const [answers, setAnswers] = useState<Record<string, string>>({})

  const handleComplete = (completedAnswers: Record<string, string>) => {
    setAnswers(completedAnswers)
    setShowResults(true)
  }

  const handleReset = () => {
    setShowResults(false)
    setAnswers({})
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Try KahnemanBench
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Experience the same questions we use to evaluate AI systems. 
            See if you can identify the cognitive biases at play.
          </p>
        </div>

        {!showResults ? (
          <QuestionViewer 
            questions={sampleQuestions}
            onComplete={handleComplete}
          />
        ) : (
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
              <h2 className="text-2xl font-bold mb-4">Complete!</h2>
              <p className="text-gray-600 mb-6">
                Thank you for trying KahnemanBench. In a real evaluation, we would compare your responses 
                to both Kahneman&apos;s findings and AI model outputs.
              </p>
              <button
                onClick={handleReset}
                className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                Try Again
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}