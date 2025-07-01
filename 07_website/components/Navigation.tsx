'use client'

interface NavigationProps {
  currentIndex: number
  totalQuestions: number
  onPrevious: () => void
  onNext: () => void
  canProceed: boolean
  isLastQuestion: boolean
}

export default function Navigation({
  currentIndex,
  totalQuestions,
  onPrevious,
  onNext,
  canProceed,
  isLastQuestion
}: NavigationProps) {
  return (
    <div className="flex items-center justify-between">
      <button
        onClick={onPrevious}
        disabled={currentIndex === 0}
        className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
      >
        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Previous
      </button>

      <div className="flex items-center space-x-2">
        {/* Progress dots */}
        <div className="flex space-x-1">
          {Array.from({ length: Math.min(totalQuestions, 10) }).map((_, i) => (
            <div
              key={i}
              className={`w-2 h-2 rounded-full transition-all ${
                i === currentIndex 
                  ? 'bg-blue-600 w-6' 
                  : i < currentIndex 
                  ? 'bg-blue-400' 
                  : 'bg-gray-300'
              }`}
            />
          ))}
        </div>
        <span className="text-sm text-gray-600 ml-3">
          {currentIndex + 1} of {totalQuestions}
        </span>
      </div>

      <button
        onClick={onNext}
        disabled={!canProceed}
        className={`inline-flex items-center px-4 py-2 text-sm font-medium rounded-lg transition-all ${
          canProceed
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
  )
}