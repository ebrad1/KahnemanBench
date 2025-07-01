import Link from 'next/link'

export default function ExpertPage() {
  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">
            Expert Analysis Dashboard
          </h1>
          
          <div className="mb-8">
            <p className="text-gray-600 leading-relaxed">
              This section will provide detailed analysis of KahnemanBench evaluation results, 
              including model performance comparisons, statistical analysis, and insights into 
              AI behavioral science capabilities.
            </p>
          </div>
          
          {/* TODO: Implement analysis features */}
          <div className="space-y-6">
            <div className="border border-gray-200 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-3">Model Performance Overview</h2>
              <p className="text-gray-600 mb-4">
                TODO: Display aggregated scores across all models, showing both generation 
                quality and evaluation accuracy metrics.
              </p>
              <div className="bg-yellow-50 border border-yellow-200 rounded p-4">
                <p className="text-yellow-800 text-sm">
                  📊 Chart showing model rankings and score distributions will be implemented here
                </p>
              </div>
            </div>
            
            <div className="border border-gray-200 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-3">Detailed Results Browser</h2>
              <p className="text-gray-600 mb-4">
                TODO: Interactive table for browsing rating results with filtering 
                and sorting capabilities.
              </p>
              <div className="bg-yellow-50 border border-yellow-200 rounded p-4">
                <p className="text-yellow-800 text-sm">
                  📋 Data table with results from <code>05_rating_results/</code> will be implemented here
                </p>
              </div>
            </div>
            
            <div className="border border-gray-200 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-3">Statistical Analysis</h2>
              <p className="text-gray-600 mb-4">
                TODO: Statistical significance tests, confidence intervals, and 
                correlation analysis between different evaluation metrics.
              </p>
              <div className="bg-yellow-50 border border-yellow-200 rounded p-4">
                <p className="text-yellow-800 text-sm">
                  📈 Statistical analysis dashboard will be implemented here
                </p>
              </div>
            </div>
            
            <div className="border border-gray-200 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-3">Export & Reports</h2>
              <p className="text-gray-600 mb-4">
                TODO: Generate downloadable reports and export functionality 
                for research and publication purposes.
              </p>
              <div className="bg-yellow-50 border border-yellow-200 rounded p-4">
                <p className="text-yellow-800 text-sm">
                  📋 Report generation tools will be implemented here
                </p>
              </div>
            </div>
          </div>
          
          {/* Navigation back to home */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <Link 
              href="/" 
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              ← Back to Home
            </Link>
          </div>
        </div>
      </div>
    </main>
  )
}