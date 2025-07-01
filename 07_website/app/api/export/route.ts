import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    const format = request.nextUrl.searchParams.get('format') || 'json'
    const expertCode = request.nextUrl.searchParams.get('expertCode')
    
    // Get data from the responses endpoint
    const baseUrl = request.nextUrl.origin
    const responsesUrl = new URL('/api/responses', baseUrl)
    if (expertCode) {
      responsesUrl.searchParams.set('expertCode', expertCode)
    }
    
    const response = await fetch(responsesUrl.toString())
    const data = await response.json()
    
    if (format === 'csv') {
      // Convert to CSV format
      const responses = expertCode ? data.responses : data.responses || []
      
      if (responses.length === 0) {
        return new NextResponse('No data available for export', { status: 404 })
      }
      
      const headers = [
        'Expert Code',
        'Question ID', 
        'Selected Response ID',
        'Correct Response ID',
        'Is Correct',
        'Timestamp'
      ]
      
      const csvRows = [
        headers.join(','),
        ...responses.map((r: any) => [
          r.expertCode,
          r.questionId,
          r.selectedResponseId,
          r.correctResponseId,
          r.isCorrect,
          r.timestamp
        ].join(','))
      ]
      
      const csvContent = csvRows.join('\n')
      const filename = expertCode 
        ? `kahneman_expert_${expertCode}_${new Date().toISOString().split('T')[0]}.csv`
        : `kahneman_all_experts_${new Date().toISOString().split('T')[0]}.csv`
      
      return new NextResponse(csvContent, {
        headers: {
          'Content-Type': 'text/csv',
          'Content-Disposition': `attachment; filename="${filename}"`
        }
      })
    }
    
    // Default JSON format
    const filename = expertCode 
      ? `kahneman_expert_${expertCode}_${new Date().toISOString().split('T')[0]}.json`
      : `kahneman_all_experts_${new Date().toISOString().split('T')[0]}.json`
    
    const exportData = {
      exportedAt: new Date().toISOString(),
      exportFormat: 'json',
      ...(expertCode ? { expertCode } : {}),
      data
    }
    
    return new NextResponse(JSON.stringify(exportData, null, 2), {
      headers: {
        'Content-Type': 'application/json',
        'Content-Disposition': `attachment; filename="${filename}"`
      }
    })
  } catch (error) {
    console.error('Error exporting data:', error)
    return NextResponse.json(
      { error: 'Failed to export data' },
      { status: 500 }
    )
  }
}