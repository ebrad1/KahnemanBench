'use client'

interface AnswerOption {
  id: string
  text: string
  isCorrect?: boolean
}

interface AnswerCardProps {
  option: AnswerOption
  isSelected: boolean
  onSelect: (id: string) => void
  showResult?: boolean
}

export default function AnswerCard({ 
  option, 
  isSelected, 
  onSelect, 
  showResult 
}: AnswerCardProps) {
  const handleClick = () => {
    if (!showResult) {
      onSelect(option.id)
    }
  }

  const getCardStyles = () => {
    const baseStyles = "p-4 rounded-lg border-2 cursor-pointer transition-all duration-200"
    
    if (showResult && option.isCorrect) {
      return `${baseStyles} border-green-500 bg-green-50`
    }
    
    if (showResult && isSelected && !option.isCorrect) {
      return `${baseStyles} border-red-500 bg-red-50`
    }
    
    if (isSelected) {
      return `${baseStyles} border-blue-500 bg-blue-50 shadow-md`
    }
    
    return `${baseStyles} border-gray-200 hover:border-gray-300 hover:shadow-sm bg-white`
  }

  return (
    <div 
      className={getCardStyles()}
      onClick={handleClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          handleClick()
        }
      }}
    >
      <div className="flex items-start">
        <div className="flex-shrink-0 mr-3">
          <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all ${
            isSelected 
              ? 'border-blue-500 bg-blue-500' 
              : 'border-gray-300'
          }`}>
            {isSelected && (
              <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            )}
          </div>
        </div>
        <div className="flex-grow">
          <p className="text-gray-800 leading-relaxed">{option.text}</p>
        </div>
      </div>
    </div>
  )
}