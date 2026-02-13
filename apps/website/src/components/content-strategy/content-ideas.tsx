'use client'

import { useState } from 'react'
import { trpc } from '@/lib/trpc'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@echo/ui/card'
import { Button } from '@echo/ui/button'
import { Input } from '@echo/ui/input'
import { Label } from '@echo/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@echo/ui/select'
import { Badge } from '@echo/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@echo/ui/tabs'
import { Lightbulb, Target, TrendingUp, Loader2, Copy, CheckCircle, Sparkles, Users } from 'lucide-react'
import { PerformanceGauge } from '@/components/shared/performance-gauge'
import { KeywordPill } from '@/components/shared/keyword-pill'
import { MetricCard } from '@/components/shared/metric-card'

interface ContentIdeasProps {
  userNiche?: string
}

export function ContentIdeas({ userNiche }: ContentIdeasProps) {
  const [topics, setTopics] = useState<string[]>([])
  const [newTopic, setNewTopic] = useState('')
  const [ideaCount, setIdeaCount] = useState(10)
  const [goalType, setGoalType] = useState<'views' | 'engagement' | 'retention' | 'growth'>('views')
  const [copied, setCopied] = useState<string | null>(null)

  // Generate content ideas mutation
  const generateIdeas = trpc.contentStrategy.generateContentIdeas.useMutation()

  // Optimize content for goal mutation
  const optimizeForGoal = trpc.contentStrategy.optimizeForGoal.useMutation()

  const handleAddTopic = () => {
    if (newTopic.trim() && !topics.includes(newTopic.trim())) {
      setTopics([...topics, newTopic.trim()])
      setNewTopic('')
    }
  }

  const handleRemoveTopic = (topic: string) => {
    setTopics(topics.filter(t => t !== topic))
  }

  const handleGenerateIdeas = async () => {
    if (topics.length === 0) return

    await generateIdeas.mutateAsync({
      topics,
      niche: userNiche,
      count: ideaCount
    })
  }

  const handleOptimizeForGoal = async (idea: string) => {
    await optimizeForGoal.mutateAsync({
      content: idea,
      goalType,
      niche: userNiche
    })
  }

  const handleCopy = async (text: string, type: string) => {
    await navigator.clipboard.writeText(text)
    setCopied(type)
    setTimeout(() => setCopied(null), 2000)
  }

  const getGoalIcon = (goal: string) => {
    switch (goal) {
      case 'views': return <TrendingUp className="w-4 h-4" />
      case 'engagement': return <Users className="w-4 h-4" />
      case 'retention': return <Target className="w-4 h-4" />
      case 'growth': return <Sparkles className="w-4 h-4" />
      default: return <Lightbulb className="w-4 h-4" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-primary" />
          Content Ideas Generator
        </h3>
        <p className="text-sm text-muted-foreground">
          Generate creative content ideas tailored to your niche and goals
        </p>
      </div>

      {/* Input Form */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Generate Ideas</CardTitle>
          <CardDescription>
            Add topics and set your content goals to get personalized suggestions
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label>Topics & Interests</Label>
            <div className="flex gap-2 mb-2">
              <Input
                value={newTopic}
                onChange={(e) => setNewTopic(e.target.value)}
                placeholder="e.g., React hooks, cooking tips, fitness..."
                onKeyPress={(e) => e.key === 'Enter' && handleAddTopic()}
              />
              <Button onClick={handleAddTopic} disabled={!newTopic.trim()}>
                Add Topic
              </Button>
            </div>
            {topics.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {topics.map((topic) => (
                  <KeywordPill
                    key={topic}
                    keyword={topic}
                    removable
                    onRemove={() => handleRemoveTopic(topic)}
                  />
                ))}
              </div>
            )}
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="ideaCount">Number of Ideas</Label>
              <Select value={ideaCount.toString()} onValueChange={(value) => setIdeaCount(parseInt(value))}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="5">5 ideas</SelectItem>
                  <SelectItem value="10">10 ideas</SelectItem>
                  <SelectItem value="15">15 ideas</SelectItem>
                  <SelectItem value="20">20 ideas</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="goalType">Content Goal</Label>
              <Select value={goalType} onValueChange={(value: any) => setGoalType(value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="views">Maximize Views</SelectItem>
                  <SelectItem value="engagement">Boost Engagement</SelectItem>
                  <SelectItem value="retention">Improve Retention</SelectItem>
                  <SelectItem value="growth">Channel Growth</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <Button
            onClick={handleGenerateIdeas}
            disabled={topics.length === 0 || generateIdeas.isPending}
            className="w-full"
          >
            {generateIdeas.isPending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Lightbulb className="w-4 h-4" />
            )}
            Generate {ideaCount} Content Ideas
          </Button>
        </CardContent>
      </Card>

      {/* Generated Ideas */}
      {generateIdeas.data && generateIdeas.data.length > 0 && (
        <Tabs defaultValue="ideas" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="ideas">Content Ideas</TabsTrigger>
            <TabsTrigger value="optimization">Goal Optimization</TabsTrigger>
          </TabsList>

          <TabsContent value="ideas" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  Generated Ideas ({generateIdeas.data.length})
                </CardTitle>
                <CardDescription>
                  AI-generated content ideas based on your topics and niche
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {generateIdeas.data.map((idea, index) => (
                    <div
                      key={index}
                      className="p-4 border rounded-lg hover:bg-secondary/50 transition-colors group"
                    >
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center text-sm font-medium text-primary mt-0.5">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          <p className="font-medium mb-2">{idea}</p>
                          <div className="flex items-center justify-between">
                            <div className="flex gap-2">
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => handleCopy(idea, `idea-${index}`)}
                              >
                                {copied === `idea-${index}` ? (
                                  <CheckCircle className="w-4 h-4 text-green-500" />
                                ) : (
                                  <Copy className="w-4 h-4" />
                                )}
                                Copy
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleOptimizeForGoal(idea)}
                                disabled={optimizeForGoal.isPending}
                              >
                                {optimizeForGoal.isPending ? (
                                  <Loader2 className="w-4 h-4 animate-spin" />
                                ) : (
                                  getGoalIcon(goalType)
                                )}
                                Optimize
                              </Button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="optimization" className="space-y-4">
            {optimizeForGoal.data ? (
              <>
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <MetricCard
                    title="Predicted Performance"
                    value={`${optimizeForGoal.data.expectedScore}/100`}
                    icon={getGoalIcon(goalType)}
                  />
                  <MetricCard
                    title="Content Type"
                    value={optimizeForGoal.data.recommendedFormat}
                    icon={<Target className="w-4 h-4" />}
                  />
                  <MetricCard
                    title="Best Upload Time"
                    value={optimizeForGoal.data.optimalTiming}
                    icon={<TrendingUp className="w-4 h-4" />}
                  />
                  <MetricCard
                    title="Target Duration"
                    value={optimizeForGoal.data.recommendedLength}
                    icon={<Sparkles className="w-4 h-4" />}
                  />
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Optimization Recommendations</CardTitle>
                    <CardDescription>
                      Tailored suggestions to achieve your {goalType} goal
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {optimizeForGoal.data.recommendations.map((rec, index) => (
                      <div key={index} className="flex items-start gap-3 p-3 bg-primary/5 rounded-lg">
                        <div className="w-6 h-6 bg-primary/10 rounded-full flex items-center justify-center text-sm font-medium text-primary mt-0.5">
                          {index + 1}
                        </div>
                        <p className="text-sm flex-1">{rec}</p>
                      </div>
                    ))}
                  </CardContent>
                </Card>

                {optimizeForGoal.data.suggestedKeywords && optimizeForGoal.data.suggestedKeywords.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Suggested Keywords</CardTitle>
                      <CardDescription>
                        Keywords to include for better discoverability
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-wrap gap-2">
                        {optimizeForGoal.data.suggestedKeywords.map((keyword, index) => (
                          <KeywordPill
                            key={index}
                            keyword={keyword}
                            copyable
                          />
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </>
            ) : (
              <Card>
                <CardContent className="text-center py-12">
                  <Target className="w-12 h-12 mx-auto text-muted-foreground/50 mb-4" />
                  <h3 className="font-medium mb-2">No optimization data yet</h3>
                  <p className="text-sm text-muted-foreground">
                    Click "Optimize" on any content idea to get goal-specific recommendations
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      )}

      {/* Empty State */}
      {!generateIdeas.data && (
        <Card>
          <CardContent className="text-center py-12">
            <Lightbulb className="w-12 h-12 mx-auto text-muted-foreground/50 mb-4" />
            <h3 className="font-medium mb-2">Ready to brainstorm content ideas?</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Add some topics above to generate personalized content suggestions
            </p>
            <Badge variant="outline" className="text-xs">
              {userNiche ? `Optimized for ${userNiche}` : 'Add your niche for better results'}
            </Badge>
          </CardContent>
        </Card>
      )}
    </div>
  )
}