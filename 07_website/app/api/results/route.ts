import { NextRequest, NextResponse } from 'next/server'

// This would typically fetch from the same storage as the responses endpoint
// For simplicity, we're importing from the responses route logic
// In production, you'd use a shared database or storage service

export async function GET(request: NextRequest) {
  try {
    // Get data from the responses endpoint
    const baseUrl = request.nextUrl.origin
    const responsesUrl = new URL('/api/responses', baseUrl)
    
    const response = await fetch(responsesUrl.toString())
    const data = await response.json()
    
    if (!data.responses || data.responses.length === 0) {
      return NextResponse.json({
        message: 'No expert data available yet',
        totalExperts: 0,
        totalResponses: 0,
        overallAccuracy: 0,
        expertBreakdown: []
      })
    }

    // Calculate statistics
    const experts = Array.from(new Set(data.responses.map((r: any) => r.expertCode)))
    const expertBreakdown = experts.map(expertCode => {
      const expertResponses = data.responses.filter((r: any) => r.expertCode === expertCode)
      const correct = expertResponses.filter((r: any) => r.isCorrect).length
      const total = expertResponses.length
      
      return {
        expertCode,
        totalResponses: total,
        correctResponses: correct,
        accuracy: total > 0 ? correct / total : 0,
        lastSubmission: expertResponses[expertResponses.length - 1]?.timestamp
      }
    })

    const totalResponses = data.responses.length
    const totalCorrect = data.responses.filter((r: any) => r.isCorrect).length
    const overallAccuracy = totalResponses > 0 ? totalCorrect / totalResponses : 0

    return NextResponse.json({
      totalExperts: experts.length,
      totalResponses,
      totalCorrect,
      overallAccuracy,
      expertBreakdown,
      lastUpdated: new Date().toISOString()
    })
  } catch (error) {
    console.error('Error fetching results:', error)
    return NextResponse.json(
      { error: 'Failed to fetch results' },
      { status: 500 }
    )
  }
}