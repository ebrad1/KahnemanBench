import { NextRequest, NextResponse } from 'next/server'
import { addResponse, getExpertResponses, getAllResponses, ResponseSubmission } from '@/lib/storage'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    const submission: ResponseSubmission = {
      expertCode: body.expertCode,
      questionId: body.questionId,
      selectedResponseId: body.selectedResponseId,
      correctResponseId: body.correctResponseId,
      isCorrect: body.isCorrect,
      timestamp: new Date().toISOString(),
      datasetName: body.datasetName
    }

    // Validate required fields
    if (!submission.expertCode || !submission.questionId || !submission.selectedResponseId) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      )
    }

    // Save to file storage (handles updates automatically)
    await addResponse(submission)
    
    console.log(`Expert ${submission.expertCode} submitted response for ${submission.questionId}: ${submission.isCorrect ? 'CORRECT' : 'INCORRECT'}`)
    
    // Get expert's total submissions for response
    const expertResponses = await getExpertResponses(submission.expertCode)
    console.log(`Total submissions for ${submission.expertCode}: ${expertResponses.length}`)

    return NextResponse.json({
      success: true,
      submissionCount: expertResponses.length
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
  try {
    const expertCode = request.nextUrl.searchParams.get('expertCode')
    
    if (expertCode) {
      const expertData = await getExpertResponses(expertCode)
      return NextResponse.json({
        expertCode,
        responses: expertData,
        totalSubmissions: expertData.length,
        correctSubmissions: expertData.filter(r => r.isCorrect).length,
        accuracy: expertData.length > 0 ? expertData.filter(r => r.isCorrect).length / expertData.length : 0
      })
    }

    // Return all data if no expertCode specified
    const allResponses = await getAllResponses()
    const uniqueExperts = Array.from(new Set(allResponses.map(r => r.expertCode)))
    return NextResponse.json({
      totalResponses: allResponses.length,
      uniqueExperts,
      responses: allResponses
    })
  } catch (error) {
    console.error('Error loading responses:', error)
    return NextResponse.json(
      { error: 'Failed to load responses' },
      { status: 500 }
    )
  }
}