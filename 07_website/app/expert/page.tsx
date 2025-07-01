'use client'

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import ComparisonViewer from '@/components/ComparisonViewer'
import { KahnemanDataset } from '@/lib/types'

function ExpertPageContent() {
  const searchParams = useSearchParams()
  const [expertCode, setExpertCode] = useState('')
  const [codeEntered, setCodeEntered] = useState(false)
  const [dataset, setDataset] = useState<KahnemanDataset | null>(null)
  const [loading, setLoading] = useState(false)

  // No longer using URL-based authentication - just expert codes for tracking
  useEffect(() => {
    // Auto-populate from URL if provided for convenience
    const code = searchParams.get('code')
    if (code) {
      setExpertCode(code)
      setCodeEntered(true)
    }
  }, [searchParams])

  const handleFileLoad = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setLoading(true)
    try {
      const text = await file.text()
      const data: KahnemanDataset = JSON.parse(text)
      setDataset(data)
    } catch (error) {
      alert('Error loading file: ' + error)
    } finally {
      setLoading(false)
    }
  }

  const handleComplete = async (selections: Record<string, string>) => {
    if (!expertCode) {
      alert('Expert code is required')
      return
    }

    // Save each selection to the API
    const promises = Object.entries(selections).map(async ([questionId, selectedResponseId]) => {
      const question = dataset?.questions.find(q => q.question_id === questionId)
      const correctResponse = question?.responses.find(r => r.hidden_source === 'real_kahneman')
      const isCorrect = selectedResponseId === correctResponse?.response_id

      return fetch('/api/responses', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          expertCode,
          questionId,
          selectedResponseId,
          correctResponseId: correctResponse?.response_id,
          isCorrect
        })
      })
    })

    await Promise.all(promises)
    
    // Calculate accuracy
    const correct = Object.entries(selections).filter(([qId, rId]) => {
      const q = dataset?.questions.find(q => q.question_id === qId)
      const r = q?.responses.find(r => r.response_id === rId)
      return r?.hidden_source === 'real_kahneman'
    }).length

    alert(`Complete! Score: ${correct}/${dataset?.questions.length}\nData saved for expert: ${expertCode}`)
  }

  const handleCodeSubmit = () => {
    if (expertCode.trim()) {
      setCodeEntered(true)
    }
  }

  if (!codeEntered) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200 max-w-md w-full">
          <h2 className="text-xl font-bold mb-4">Expert Evaluation</h2>
          <p className="text-gray-600 mb-4">
            Enter your expert code to begin the evaluation. This will be used to track your responses.
          </p>
          <input
            type="text"
            value={expertCode}
            onChange={(e) => setExpertCode(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleCodeSubmit()}
            placeholder="EXPERT_ALICE_2025"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 mb-4"
            autoFocus
          />
          <button
            onClick={handleCodeSubmit}
            disabled={!expertCode.trim()}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Continue
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">Expert Evaluation Mode</h1>
            <div className="text-sm text-gray-600">
              Expert: <span className="font-medium">{expertCode}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="py-8">
        {!dataset ? (
          <div className="max-w-4xl mx-auto px-4">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
              <h2 className="text-lg font-semibold mb-4">Load Evaluation Dataset</h2>
              <input
                type="file"
                accept=".json"
                onChange={handleFileLoad}
                disabled={loading}
                className="hidden"
                id="file-input"
              />
              <label
                htmlFor="file-input"
                className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors cursor-pointer"
              >
                {loading ? 'Loading...' : 'Select JSON File'}
              </label>
              <p className="mt-4 text-sm text-gray-600">
                Load a rating dataset from 04_rating_datasets/
              </p>
            </div>
          </div>
        ) : (
          <ComparisonViewer
            questions={dataset.questions}
            onComplete={handleComplete}
            mode="expert"
          />
        )}
      </div>
    </div>
  )
}

export default function ExpertPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    }>
      <ExpertPageContent />
    </Suspense>
  )
}
