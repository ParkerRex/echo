'use client'

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@echo/ui/tabs'
import { FlaskConical, BarChart3 } from 'lucide-react'
import { TestCreator } from './test-creator'
import { TestResults } from './test-results'

interface ABTestingProps {
  videoId?: string
  initialTitle?: string
  initialDescription?: string
  initialThumbnail?: string
}

export function ABTesting({ 
  videoId, 
  initialTitle = '', 
  initialDescription = '', 
  initialThumbnail = '' 
}: ABTestingProps) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">A/B Testing</h2>
        <p className="text-muted-foreground">
          Test different versions of your content to optimize performance
        </p>
      </div>

      <Tabs defaultValue="results" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="results" className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            <span className="hidden sm:inline">Test Results</span>
          </TabsTrigger>
          <TabsTrigger value="create" className="flex items-center gap-2">
            <FlaskConical className="w-4 h-4" />
            <span className="hidden sm:inline">Create Test</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="results" className="mt-6">
          <TestResults />
        </TabsContent>

        <TabsContent value="create" className="mt-6">
          <TestCreator 
            videoId={videoId}
            initialTitle={initialTitle} 
            initialDescription={initialDescription}
            initialThumbnail={initialThumbnail}
          />
        </TabsContent>
      </Tabs>
    </div>
  )
}

export * from './test-creator'
export * from './test-results'