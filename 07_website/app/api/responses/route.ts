import { NextRequest, NextResponse } from 'next/server'

interface ResponseSubmission {
  expertCode: string
  questionId: string
  selectedResponseId: string
  correctResponseId: string
  isCorrect: boolean
  timestamp: string
}

// In-memory storage for expert responses (in production, use a database)
const expertResponses: ResponseSubmission[] = []

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    const submission: ResponseSubmission = {
      expertCode: body.expertCode,
      questionId: body.questionId,
      selectedResponseId: body.selectedResponseId,
      correctResponseId: body.correctResponseId,
      isCorrect: body.isCorrect,
      timestamp: new Date().toISOString()
    }

    // Validate required fields
    if (!submission.expertCode || !submission.questionId || !submission.selectedResponseId) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      )
    }

    expertResponses.push(submission)
    
    console.log(`Expert ${submission.expertCode} submitted response for ${submission.questionId}: ${submission.isCorrect ? 'CORRECT' : 'INCORRECT'}`)
    console.log(`Total submissions: ${expertResponses.length}`)

    return NextResponse.json({
      success: true,
      submissionCount: expertResponses.filter(r => r.expertCode === submission.expertCode).length
    })
  } catch (error) {
    console.error('Error saving response:', error)
    return NextResponse.json(
      { error: 'Failed to save response' },
      { status: 500 }
    )
  }
}

export async function GET(request: NextRequest) {
  const expertCode = request.nextUrl.searchParams.get('expertCode')
  
  if (expertCode) {
    const expertData = expertResponses.filter(r => r.expertCode === expertCode)
    return NextResponse.json({
      expertCode,
      responses: expertData,
      totalSubmissions: expertData.length,
      correctSubmissions: expertData.filter(r => r.isCorrect).length,
      accuracy: expertData.length > 0 ? expertData.filter(r => r.isCorrect).length / expertData.length : 0
    })
  }

  // Return all data if no expertCode specified
  const uniqueExperts = Array.from(new Set(expertResponses.map(r => r.expertCode)))
  return NextResponse.json({
    totalResponses: expertResponses.length,
    uniqueExperts,
    responses: expertResponses
  })
}