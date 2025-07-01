'use client'

import { useState, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import ComparisonViewer from '@/components/ComparisonViewer'
import { KahnemanDataset } from '@/lib/types'

const EXPERT_KEY = process.env.NEXT_PUBLIC_EXPERT_KEY || 'kahneman2024'

export default function ExpertPage() {
  const searchParams = useSearchParams()
  const [authenticated, setAuthenticated] = useState(false)
  const [dataset, setDataset] = useState<KahnemanDataset | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const key = searchParams.get('key')
    if (key === EXPERT_KEY) {
      setAuthenticated(true)
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
    // Here you would save to Supabase or your preferred database
    console.log('Expert selections:', selections)
    
    // Calculate accuracy
    const correct = Object.entries(selections).filter(([qId, rId]) => {
      const q = dataset?.questions.find(q => q.question_id === qId)
      const r = q?.responses.find(r => r.response_id === rId)
      return r?.hidden_source === 'real_kahneman'
    }).length

    alert(`Complete! Score: ${correct}/${dataset?.questions.length}`)
  }

  if (!authenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200 max-w-md w-full">
          <h2 className="text-xl font-bold mb-4">Expert Access Required</h2>
          <p className="text-gray-600">
            Please use the correct access link with authentication key.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-2xl font-bold text-gray-900">Expert Evaluation Mode</h1>
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
