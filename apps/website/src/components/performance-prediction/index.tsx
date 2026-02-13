'use client'

import { PredictionAnalyzer } from './prediction-analyzer'

interface PerformancePredictionProps {
  initialTitle?: string
  initialDescription?: string
  thumbnailUrl?: string
  niche?: string
}

export function PerformancePrediction({ 
  initialTitle = '', 
  initialDescription = '', 
  thumbnailUrl = '',
  niche 
}: PerformancePredictionProps) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Performance Prediction</h2>
        <p className="text-muted-foreground">
          Get AI-powered predictions for your content's potential performance
        </p>
      </div>

      <PredictionAnalyzer
        initialTitle={initialTitle}
        initialDescription={initialDescription}
        thumbnailUrl={thumbnailUrl}
        niche={niche}
      />
    </div>
  )
}

export * from './prediction-analyzer'