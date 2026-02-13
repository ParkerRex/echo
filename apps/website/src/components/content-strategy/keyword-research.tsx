'use client'

import { useState } from 'react'
import { trpc } from '@/lib/trpc'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@echo/ui/card'
import { Button } from '@echo/ui/button'
import { Input } from '@echo/ui/input'
import { Label } from '@echo/ui/label'
import { Badge } from '@echo/ui/badge'
import { Search, Target, TrendingUp, Loader2, Lightbulb } from 'lucide-react'
import { KeywordPill } from '@/components/shared/keyword-pill'
import { MetricCard } from '@/components/shared/metric-card'
import { OptimizationBadge } from '@/components/shared/optimization-badge'

interface KeywordResearchProps {
  initialTopic?: string
  niche?: string
}

export function KeywordResearch({ initialTopic = '', niche }: KeywordResearchProps) {
  const [topic, setTopic] = useState(initialTopic)
  const [selectedKeyword, setSelectedKeyword] = useState<string | null>(null)

  // Get keyword suggestions
  const keywordSuggestions = trpc.contentStrategy.getKeywordSuggestions.useQuery(
    { topic, niche },
    { enabled: !!topic }
  )

  // Get personalized keywords
  const personalizedKeywords = trpc.contentStrategy.getPersonalizedKeywords.useQuery(
    { topic },
    { enabled: !!topic }
  )

  // Analyze keyword competition
  const analyzeCompetition = trpc.contentStrategy.analyzeKeywordCompetition.useQuery(
    { keyword: selectedKeyword || '' },
    { enabled: !!selectedKeyword }
  )

  const handleSearch = () => {
    if (topic.trim()) {
      keywordSuggestions.refetch()
      personalizedKeywords.refetch()
    }
  }

  const handleKeywordClick = (keyword: string) => {
    setSelectedKeyword(keyword)
  }

  const getCompetitionColor = (level: string) => {
    switch (level) {
      case 'low': return 'success'
      case 'medium': return 'warning'
      case 'high': return 'danger'
      default: return 'default'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Search className="w-5 h-5 text-primary" />
          Keyword Research
        </h3>
        <p className="text-sm text-muted-foreground">
          Find high-performing keywords for better discoverability
        </p>
      </div>

      {/* Search Input */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Research Keywords</CardTitle>
          <CardDescription>
            Enter a topic to discover keyword opportunities
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <div className="flex-1">
              <Label htmlFor="topic">Topic or Keyword</Label>
              <Input
                id="topic"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g., React tutorial, cooking tips, fitness workout"
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>
            <div className="flex items-end">
              <Button 
                onClick={handleSearch}
                disabled={!topic.trim() || keywordSuggestions.isFetching}
              >
                {keywordSuggestions.isFetching ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Search className="w-4 h-4" />
                )}
                Research
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Keyword Results */}
      {keywordSuggestions.data && keywordSuggestions.data.length > 0 && (
        <div className="grid lg:grid-cols-2 gap-6">
          {/* General Keywords */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Target className="w-4 h-4" />
                Keyword Opportunities
              </CardTitle>
              <CardDescription>
                Keywords with good search volume and competition balance
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {keywordSuggestions.data.map((keyword, index) => (
                  <div
                    key={index}
                    className="p-3 border rounded-lg hover:bg-secondary/50 cursor-pointer transition-colors"
                    onClick={() => handleKeywordClick(keyword.keyword)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">{keyword.keyword}</span>
                      <div className="flex items-center gap-2">
                        <OptimizationBadge
                          score={100 - keyword.difficulty}
                          size="sm"
                          variant="score"
                        />
                        <Badge variant={getCompetitionColor(keyword.competition) as any}>
                          {keyword.competition}
                        </Badge>
                      </div>
                    </div>
                    <div className="flex items-center justify-between text-sm text-muted-foreground">
                      <span>Volume: {keyword.searchVolume.toLocaleString()}</span>
                      <span>Trend: {keyword.trend}</span>
                    </div>
                    {keyword.relatedKeywords.length > 0 && (
                      <div className="mt-2">
                        <div className="flex flex-wrap gap-1">
                          {keyword.relatedKeywords.slice(0, 3).map((related, i) => (
                            <KeywordPill
                              key={i}
                              keyword={related}
                              className="text-xs"
                              onClick={() => handleKeywordClick(related)}
                            />
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Personalized Keywords */}
          {personalizedKeywords.data && personalizedKeywords.data.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <Lightbulb className="w-4 h-4" />
                  Personalized for You
                </CardTitle>
                <CardDescription>
                  Keywords based on your content style and niche
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {personalizedKeywords.data.map((keyword, index) => (
                    <div
                      key={index}
                      className="p-3 border rounded-lg hover:bg-primary/5 cursor-pointer transition-colors border-primary/20"
                      onClick={() => handleKeywordClick(keyword.keyword)}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium">{keyword.keyword}</span>
                        <div className="flex items-center gap-2">
                          <Badge variant="default" className="bg-primary/10 text-primary">
                            Match
                          </Badge>
                          <OptimizationBadge
                            score={100 - keyword.difficulty}
                            size="sm"
                            variant="score"
                          />
                        </div>
                      </div>
                      <div className="flex items-center justify-between text-sm text-muted-foreground">
                        <span>Volume: {keyword.searchVolume.toLocaleString()}</span>
                        <span>Competition: {keyword.competition}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Keyword Analysis */}
      {selectedKeyword && analyzeCompetition.data && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              Competition Analysis: "{selectedKeyword}"
            </CardTitle>
            <CardDescription>
              Detailed analysis of this keyword's competitive landscape
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-4 gap-4 mb-6">
              <MetricCard
                title="Competition"
                value={analyzeCompetition.data.competition}
                badge={{
                  text: analyzeCompetition.data.competition,
                  variant: getCompetitionColor(analyzeCompetition.data.competition) as any
                }}
              />
              <MetricCard
                title="Search Results"
                value={analyzeCompetition.data.searchResults.toLocaleString()}
                icon={<Search className="w-4 h-4" />}
              />
              <MetricCard
                title="Avg Views"
                value={analyzeCompetition.data.avgViews > 1000 
                  ? `${Math.round(analyzeCompetition.data.avgViews / 1000)}k`
                  : analyzeCompetition.data.avgViews
                }
                icon={<TrendingUp className="w-4 h-4" />}
              />
              <MetricCard
                title="Difficulty"
                value={`${analyzeCompetition.data.difficulty}%`}
                badge={{
                  text: analyzeCompetition.data.difficulty > 70 ? 'Hard' : 
                        analyzeCompetition.data.difficulty > 40 ? 'Medium' : 'Easy',
                  variant: analyzeCompetition.data.difficulty > 70 ? 'destructive' :
                          analyzeCompetition.data.difficulty > 40 ? 'secondary' : 'default'
                }}
              />
            </div>

            {analyzeCompetition.data.topChannelTypes.length > 0 && (
              <div>
                <h4 className="font-medium mb-3">Top Channel Types</h4>
                <div className="flex flex-wrap gap-2">
                  {analyzeCompetition.data.topChannelTypes.map((type, index) => (
                    <Badge key={index} variant="outline">
                      {type}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Empty States */}
      {topic && keywordSuggestions.data && keywordSuggestions.data.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <Search className="w-12 h-12 mx-auto text-muted-foreground/50 mb-4" />
            <h3 className="font-medium mb-2">No keywords found</h3>
            <p className="text-sm text-muted-foreground">
              Try a different topic or check your spelling
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}