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
              KahnemanBench Sample
            </h1>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Compare responses to behavioral science questions. One is from Daniel Kahneman, others are AI-generated. 
              Which do you find most compelling?
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
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
              <h2 className="text-2xl font-bold mb-6 text-center">Your Preferences</h2>
              
              {/* Summary of selections */}
              <div className="space-y-4 mb-8">
                {Object.entries(selections).map(([qId, rId]) => {
                  const q = publicQuestions.find(q => q.question_id === qId)
                  const selectedResponse = q?.responses.find(r => r.response_id === rId)
                  const isKahneman = selectedResponse?.hidden_source === 'real_kahneman'
                  
                  return (
                    <div key={qId} className="border border-gray-200 rounded-lg p-4">
                      <h3 className="font-medium text-gray-900 mb-2 text-sm">
                        {q?.question_text}
                      </h3>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Your preference:</span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          isKahneman 
                            ? 'bg-blue-100 text-blue-800' 
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {isKahneman ? 'Kahneman Response' : 'AI Response'}
                        </span>
                      </div>
                    </div>
                  )
                })}
              </div>

              <div className="text-center border-t border-gray-200 pt-6">
                <p className="text-lg text-gray-600 mb-2">
                  You preferred {Object.entries(selections).filter(([qId, rId]) => {
                    const q = publicQuestions.find(q => q.question_id === qId)
                    const r = q?.responses.find(r => r.response_id === rId)
                    return r?.hidden_source === 'real_kahneman'
                  }).length} out of {publicQuestions.length} responses from Daniel Kahneman.
                </p>
                <p className="text-gray-600 mb-6">
                  This demonstrates how AI can sometimes capture the style and substance of human experts, 
                  making preference judgments more nuanced than simple identification tasks.
                </p>
                <button
                  onClick={handleReset}
                  className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Try Again
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
