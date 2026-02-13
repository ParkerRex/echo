'use client'

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@echo/ui/tabs'
import { TrendingUp, Search, Target, Lightbulb } from 'lucide-react'
import { TrendingTopics } from './trending-topics'
import { KeywordResearch } from './keyword-research'
import { SEOOptimizer } from './seo-optimizer'
import { ContentIdeas } from './content-ideas'

interface ContentStrategyProps {
  userNiche?: string
  initialTitle?: string
  initialDescription?: string
}

export function ContentStrategy({ 
  userNiche, 
  initialTitle = '', 
  initialDescription = '' 
}: ContentStrategyProps) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Content Strategy</h2>
        <p className="text-muted-foreground">
          Discover trends, research keywords, and optimize your content for maximum impact
        </p>
      </div>

      <Tabs defaultValue="trending" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="trending" className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            <span className="hidden sm:inline">Trending</span>
          </TabsTrigger>
          <TabsTrigger value="keywords" className="flex items-center gap-2">
            <Search className="w-4 h-4" />
            <span className="hidden sm:inline">Keywords</span>
          </TabsTrigger>
          <TabsTrigger value="seo" className="flex items-center gap-2">
            <Target className="w-4 h-4" />
            <span className="hidden sm:inline">SEO</span>
          </TabsTrigger>
          <TabsTrigger value="ideas" className="flex items-center gap-2">
            <Lightbulb className="w-4 h-4" />
            <span className="hidden sm:inline">Ideas</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="trending" className="mt-6">
          <TrendingTopics userNiche={userNiche} />
        </TabsContent>

        <TabsContent value="keywords" className="mt-6">
          <KeywordResearch niche={userNiche} />
        </TabsContent>

        <TabsContent value="seo" className="mt-6">
          <SEOOptimizer 
            initialTitle={initialTitle} 
            initialDescription={initialDescription}
            niche={userNiche} 
          />
        </TabsContent>

        <TabsContent value="ideas" className="mt-6">
          <ContentIdeas userNiche={userNiche} />
        </TabsContent>
      </Tabs>
    </div>
  )
}

export * from './trending-topics'
export * from './keyword-research'
export * from './seo-optimizer'
export * from './content-ideas'