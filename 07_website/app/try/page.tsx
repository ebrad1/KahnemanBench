'use client'

import { useState } from 'react'
import ComparisonViewer from '@/components/ComparisonViewer'
import { publicQuestions } from '@/lib/publicQuestions'

export default function TryPage() {
  const [completed, setCompleted] = useState(false)
  const [selections, setSelections] = useState<Record<string, string>>({})

  const handleComplete = (userSelections: Record<string, string>) => {
    setSelections(userSelections)
    setCompleted(true)
    
    // Calculate score
    const correct = Object.entries(userSelections).filter(([questionId, responseId]) => {
      const question = publicQuestions.find(q => q.question_id === questionId)
      const response = question?.responses.find(r => r.response_id === responseId)
      return response?.hidden_source === 'real_kahneman'
    }).length

    console.log(`Score: ${correct}/${publicQuestions.length}`)
  }

  const handleReset = () => {
    setCompleted(false)
    setSelections({})
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Can You Identify Kahneman?
            </h1>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              One of these responses is from Daniel Kahneman himself. The others are AI-generated. 
              Can you tell which is which?
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="py-8">
        {!completed ? (
          <ComparisonViewer 
            questions={publicQuestions}
            onComplete={handleComplete}
            mode="public"
          />
        ) : (
          <div className="max-w-4xl mx-auto px-4">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
              <h2 className="text-2xl font-bold mb-4">Complete!</h2>
              <p className="text-lg text-gray-600 mb-2">
                You correctly identified {Object.entries(selections).filter(([qId, rId]) => {
                  const q = publicQuestions.find(q => q.question_id === qId)
                  const r = q?.responses.find(r => r.response_id === rId)
                  return r?.hidden_source === 'real_kahneman'
                }).length} out of {publicQuestions.length} Kahneman responses.
              </p>
              <p className="text-gray-600 mb-6">
                This demonstrates how AI can sometimes capture the style and substance of human experts, 
                making it increasingly difficult to distinguish between human and AI responses.
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
