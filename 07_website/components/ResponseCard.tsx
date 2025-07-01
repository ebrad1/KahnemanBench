'use client'

import { KahnemanResponse } from '@/lib/types'

interface ResponseCardProps {
  response: KahnemanResponse
  isSelected: boolean
  onSelect: (responseId: string) => void
  responseLabel: string
  showSource?: boolean
}

export default function ResponseCard({ 
  response, 
  isSelected, 
  onSelect, 
  responseLabel,
  showSource = false 
}: ResponseCardProps) {
  return (
    <div 
      className={`
        bg-white rounded-lg border-2 p-6 cursor-pointer transition-all
        ${isSelected 
          ? 'border-blue-500 shadow-lg' 
          : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
        }
      `}
      onClick={() => onSelect(response.response_id)}
    >
      <div className="mb-4 flex items-center justify-between">
        <h3 className="font-medium text-gray-900">{responseLabel}</h3>
        <div className={`
          w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all
          ${isSelected 
            ? 'border-blue-500 bg-blue-500' 
            : 'border-gray-300'
          }
        `}>
          {isSelected && (
            <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          )}
        </div>
      </div>
      
      <div className="text-gray-700 text-sm leading-relaxed whitespace-pre-wrap max-h-96 overflow-y-auto">
        {response.response_text}
      </div>

      {showSource && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          <span className={`text-xs font-medium ${
            response.hidden_source === 'real_kahneman' 
              ? 'text-green-600' 
              : 'text-blue-600'
          }`}>
            {response.hidden_source === 'real_kahneman' ? 'Kahneman' : 'AI Generated'}
          </span>
        </div>
      )}
    </div>
  )
}
