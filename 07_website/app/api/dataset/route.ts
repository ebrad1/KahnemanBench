import { NextResponse } from 'next/server'
import { readFile } from 'fs/promises'
import { join } from 'path'
import { DATASET_CONFIG } from '@/lib/datasetConfig'
import { KahnemanDataset } from '@/lib/types'

export async function GET() {
  try {
    // Get the path to the rating dataset
    const datasetPath = join(process.cwd(), '..', '04_rating_datasets', DATASET_CONFIG.activeDataset)
    
    // Read and parse the dataset file
    const fileContent = await readFile(datasetPath, 'utf-8')
    const dataset: KahnemanDataset = JSON.parse(fileContent)
    
    // Add configuration metadata
    const response = {
      ...dataset,
      configInfo: DATASET_CONFIG.currentDatasetInfo
    }
    
    return NextResponse.json(response)
  } catch (error) {
    console.error('Error loading dataset:', error)
    return NextResponse.json(
      { 
        error: 'Failed to load dataset',
        details: error instanceof Error ? error.message : 'Unknown error',
        activeDataset: DATASET_CONFIG.activeDataset
      },
      { status: 500 }
    )
  }
}