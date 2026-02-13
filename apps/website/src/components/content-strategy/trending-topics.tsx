'use client'

import { useState } from 'react'
import { trpc } from '@/lib/trpc'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@echo/ui/card'
import { Button } from '@echo/ui/button'
import { Badge } from '@echo/ui/badge'
import { Input } from '@echo/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@echo/ui/select'
import { TrendingUp, Lightbulb, Target, Loader2, RefreshCw } from 'lucide-react'
import { MetricCard } from '@/components/shared/metric-card'
import { KeywordPill } from '@/components/shared/keyword-pill'

interface TrendingTopicsProps {
  userNiche?: string
}

export function TrendingTopics({ userNiche }: TrendingTopicsProps) {
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null)
  const [ideaCount, setIdeaCount] = useState(8)

  // Fetch trending topics
  const { data: trends, isLoading: trendsLoading, refetch: refetchTrends } = trpc.contentStrategy.getTrendingTopics.useQuery({
    niche: userNiche,
    region: 'US'
  })

  // Generate content ideas mutation
  const generateIdeas = trpc.contentStrategy.generateContentIdeas.useMutation()

  const handleGenerateIdeas = async (topic: string) => {
    setSelectedTopic(topic)
    await generateIdeas.mutateAsync({
      topics: [topic],
      niche: userNiche,
      count: ideaCount
    })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-primary" />
            Trending Topics
          </h3>
          <p className="text-sm text-muted-foreground">
            Discover trending topics {userNiche ? `in ${userNiche}` : 'across YouTube'}
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => refetchTrends()}
          disabled={trendsLoading}
        >
          {trendsLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <RefreshCw className="w-4 h-4" />
          )}
          Refresh
        </Button>
      </div>

      {/* Quick Stats */}
      {trends && trends.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard
            title="Total Trends"
            value={trends.length}
            icon={<TrendingUp className="w-4 h-4" />}
          />
          <MetricCard
            title="Avg Trend Score"
            value={Math.round(trends.reduce((sum, t) => sum + t.trendScore, 0) / trends.length)}
            icon={<Target className="w-4 h-4" />}
          />
          <MetricCard
            title="Competition Level"
            value={trends.filter(t => t.competitionLevel === 'low').length > trends.length / 2 ? 'Low' : 'Medium'}
            icon={<Badge className="w-4 h-4" />}
          />
        </div>
      )}

      {/* Trending Topics Grid */}
      <div className="grid gap-4">
        {trendsLoading ? (
          <div className="text-center py-12">
            <Loader2 className="w-6 h-6 animate-spin mx-auto mb-4" />
            <p className="text-muted-foreground">Finding trending topics...</p>
          </div>
        ) : trends && trends.length > 0 ? (
          trends.map((trend) => (
            <Card key={trend.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="space-y-2">
                    <CardTitle className="text-base">{trend.topic}</CardTitle>
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary">{trend.category}</Badge>
                      <Badge 
                        variant={
                          trend.competitionLevel === 'low' ? 'default' :
                          trend.competitionLevel === 'medium' ? 'secondary' : 'outline'
                        }
                      >
                        {trend.competitionLevel} competition
                      </Badge>
                      <Badge variant="outline">
                        Score: {trend.trendScore}/100
                      </Badge>
                    </div>
                  </div>
                  <Button
                    size="sm"
                    onClick={() => handleGenerateIdeas(trend.topic)}
                    disabled={generateIdeas.isPending}
                  >
                    {generateIdeas.isPending && selectedTopic === trend.topic ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Lightbulb className="w-4 h-4" />
                    )}
                    Ideas
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Related Keywords */}
                {trend.relatedKeywords && trend.relatedKeywords.length > 0 && (
                  <div>
                    <p className="text-sm font-medium mb-2">Related Keywords:</p>
                    <div className="flex flex-wrap gap-2">
                      {trend.relatedKeywords.slice(0, 6).map((keyword, index) => (
                        <KeywordPill
                          key={index}
                          keyword={keyword}
                          copyable
                          className="text-xs"
                        />
                      ))}
                    </div>
                  </div>
                )}

                {/* Sample Titles */}
                {trend.sampleTitles && trend.sampleTitles.length > 0 && (
                  <div>
                    <p className="text-sm font-medium mb-2">Example Titles:</p>
                    <div className="space-y-1">
                      {trend.sampleTitles.slice(0, 3).map((title, index) => (
                        <p key={index} className="text-sm text-muted-foreground bg-secondary/50 rounded p-2">
                          "{title}"
                        </p>
                      ))}
                    </div>
                  </div>
                )}

                {/* Generated Content Ideas */}
                {generateIdeas.data && selectedTopic === trend.topic && (
                  <div>
                    <p className="text-sm font-medium mb-2 text-primary">AI-Generated Content Ideas:</p>
                    <div className="space-y-2">
                      {generateIdeas.data.map((idea, index) => (
                        <div key={index} className="flex items-start gap-3 p-3 bg-primary/5 rounded-lg">
                          <div className="w-6 h-6 bg-primary/10 rounded-full flex items-center justify-center text-sm font-medium text-primary mt-0.5">
                            {index + 1}
                          </div>
                          <p className="text-sm flex-1">{idea}</p>
                          <Button size="sm" variant="ghost" onClick={() => navigator.clipboard.writeText(idea)}>
                            Copy
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))
        ) : (
          <Card>
            <CardContent className="text-center py-12">
              <TrendingUp className="w-12 h-12 mx-auto text-muted-foreground/50 mb-4" />
              <h3 className="font-medium mb-2">No trending topics found</h3>
              <p className="text-sm text-muted-foreground mb-4">
                {userNiche 
                  ? `No trends found for ${userNiche}. Try analyzing your niche first.`
                  : 'Upload some videos to get personalized trending topics.'
                }
              </p>
              <Button variant="outline" onClick={() => refetchTrends()}>
                Try Again
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}