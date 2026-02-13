'use client'

import { useState } from 'react'
import { trpc } from '@/lib/trpc'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@echo/ui/card'
import { Button } from '@echo/ui/button'
import { Input } from '@echo/ui/input'
import { Label } from '@echo/ui/label'
import { Textarea } from '@echo/ui/textarea'
import { Badge } from '@echo/ui/badge'
import { Progress } from '@echo/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@echo/ui/tabs'
import { 
  TrendingUp, 
  Target, 
  Eye, 
  Clock, 
  Users, 
  Heart, 
  Loader2, 
  Sparkles, 
  AlertTriangle,
  CheckCircle,
  BarChart3,
  Zap
} from 'lucide-react'
import { PerformanceGauge } from '@/components/shared/performance-gauge'
import { MetricCard } from '@/components/shared/metric-card'
import { OptimizationBadge } from '@/components/shared/optimization-badge'

interface PredictionAnalyzerProps {
  initialTitle?: string
  initialDescription?: string
  thumbnailUrl?: string
  niche?: string
}

export function PredictionAnalyzer({ 
  initialTitle = '', 
  initialDescription = '', 
  thumbnailUrl = '',
  niche 
}: PredictionAnalyzerProps) {
  const [title, setTitle] = useState(initialTitle)
  const [description, setDescription] = useState(initialDescription)
  const [thumbnail, setThumbnail] = useState(thumbnailUrl)

  // Predict performance mutation
  const predictPerformance = trpc.contentStrategy.predictPerformance.useMutation()

  const handlePredict = async () => {
    if (!title.trim()) return

    await predictPerformance.mutateAsync({
      title,
      thumbnail,
      description,
      niche: niche || ''
    })
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'success'
    if (score >= 60) return 'warning'
    return 'danger'
  }

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
    return num.toString()
  }

  const data = predictPerformance.data

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-primary" />
          Performance Prediction
        </h3>
        <p className="text-sm text-muted-foreground">
          Get AI-powered predictions for your content's potential performance
        </p>
      </div>

      {/* Input Form */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Content Details</CardTitle>
          <CardDescription>
            Enter your content information to get performance predictions
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="title">Video Title *</Label>
            <Input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter your video title..."
              maxLength={100}
            />
            <p className="text-xs text-muted-foreground mt-1">
              {title.length}/100 characters
            </p>
          </div>

          <div>
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter your video description..."
              rows={3}
              maxLength={5000}
            />
            <p className="text-xs text-muted-foreground mt-1">
              {description.length}/5000 characters
            </p>
          </div>

          <div>
            <Label htmlFor="thumbnail">Thumbnail URL (Optional)</Label>
            <Input
              id="thumbnail"
              value={thumbnail}
              onChange={(e) => setThumbnail(e.target.value)}
              placeholder="https://example.com/thumbnail.jpg"
            />
          </div>

          <Button
            onClick={handlePredict}
            disabled={!title.trim() || predictPerformance.isPending}
            className="w-full"
          >
            {predictPerformance.isPending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Sparkles className="w-4 h-4" />
            )}
            Predict Performance
          </Button>
        </CardContent>
      </Card>

      {/* Prediction Results */}
      {data && (
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="metrics">Metrics</TabsTrigger>
            <TabsTrigger value="factors">Factors</TabsTrigger>
            <TabsTrigger value="improvements">Improvements</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            {/* Overall Score */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <Target className="w-4 h-4" />
                  Performance Score
                </CardTitle>
                <CardDescription>
                  Overall predicted performance based on historical data
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-center mb-6">
                  <PerformanceGauge
                    value={data.overallScore}
                    label="Performance Score"
                    size="lg"
                    color={getScoreColor(data.overallScore)}
                  />
                </div>
                <div className="text-center">
                  <p className="text-sm text-muted-foreground mb-2">
                    Your content is predicted to perform in the{' '}
                    <span className="font-medium">
                      {data.overallScore >= 80 ? 'top 20%' : 
                       data.overallScore >= 60 ? 'top 40%' : 
                       data.overallScore >= 40 ? 'average range' : 'bottom 40%'}
                    </span>
                    {niche && ` for ${niche} content`}
                  </p>
                  {data.confidenceLevel && (
                    <Badge variant="outline">
                      {data.confidenceLevel}% confidence
                    </Badge>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Predicted Metrics */}
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              <MetricCard
                title="Expected Views"
                value={formatNumber(data.expectedViews)}
                icon={<Eye className="w-4 h-4" />}
                description="24-hour prediction"
              />
              <MetricCard
                title="Click-through Rate"
                value={`${(data.expectedCTR * 100).toFixed(1)}%`}
                icon={<Target className="w-4 h-4" />}
                description="Predicted CTR"
              />
              <MetricCard
                title="Watch Time"
                value={`${Math.round(data.expectedWatchTime / 60)}m`}
                icon={<Clock className="w-4 h-4" />}
                description="Average duration"
              />
              <MetricCard
                title="Engagement Rate"
                value={`${(data.expectedEngagement * 100).toFixed(1)}%`}
                icon={<Heart className="w-4 h-4" />}
                description="Likes, comments, shares"
              />
            </div>

            {/* Performance Insights */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Key Insights</CardTitle>
                <CardDescription>
                  What makes this prediction
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {data.insights.map((insight, index) => (
                    <div key={index} className="flex items-start gap-3 p-3 bg-secondary/30 rounded-lg">
                      <div className="w-6 h-6 bg-primary/10 rounded-full flex items-center justify-center text-sm font-medium text-primary mt-0.5">
                        {index + 1}
                      </div>
                      <p className="text-sm flex-1">{insight}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="metrics" className="space-y-4">
            <div className="grid md:grid-cols-2 gap-6">
              {/* Performance Breakdown */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Score Breakdown</CardTitle>
                  <CardDescription>
                    Individual component scores
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="text-sm font-medium">Title Quality</span>
                      <span className="text-sm">{data.titleScore}/100</span>
                    </div>
                    <Progress value={data.titleScore} className="h-2" />
                  </div>
                  
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="text-sm font-medium">Description SEO</span>
                      <span className="text-sm">{data.descriptionScore}/100</span>
                    </div>
                    <Progress value={data.descriptionScore} className="h-2" />
                  </div>

                  {data.thumbnailScore && (
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm font-medium">Thumbnail Appeal</span>
                        <span className="text-sm">{data.thumbnailScore}/100</span>
                      </div>
                      <Progress value={data.thumbnailScore} className="h-2" />
                    </div>
                  )}

                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="text-sm font-medium">Timing & Trends</span>
                      <span className="text-sm">{data.timingScore}/100</span>
                    </div>
                    <Progress value={data.timingScore} className="h-2" />
                  </div>

                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="text-sm font-medium">Market Saturation</span>
                      <span className="text-sm">{data.competitionScore}/100</span>
                    </div>
                    <Progress value={data.competitionScore} className="h-2" />
                  </div>
                </CardContent>
              </Card>

              {/* Historical Comparison */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Historical Context</CardTitle>
                  <CardDescription>
                    How this compares to similar content
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-center p-4 bg-secondary/50 rounded-lg">
                    <div className="text-2xl font-bold text-primary mb-1">
                      {data.percentileBetter}%
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Better than similar content
                    </p>
                  </div>

                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm">Similar Content Avg</span>
                      <span className="text-sm font-medium">
                        {formatNumber(data.benchmarkViews)} views
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Top 10% Threshold</span>
                      <span className="text-sm font-medium">
                        {formatNumber(data.topPercentileViews)} views
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Your Prediction</span>
                      <span className="text-sm font-medium text-primary">
                        {formatNumber(data.expectedViews)} views
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="factors" className="space-y-4">
            <div className="grid md:grid-cols-2 gap-6">
              {/* Positive Factors */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    Positive Factors
                  </CardTitle>
                  <CardDescription>
                    What's working in your favor
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {data.positiveFactors.map((factor, index) => (
                      <div key={index} className="flex items-start gap-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                        <CheckCircle className="w-4 h-4 text-green-600 mt-0.5" />
                        <div className="flex-1">
                          <p className="text-sm font-medium text-green-800">{factor.title}</p>
                          <p className="text-xs text-green-600 mt-1">{factor.description}</p>
                          <Badge variant="outline" className="mt-2 text-xs border-green-300 text-green-700">
                            +{factor.impact}% impact
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Risk Factors */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-yellow-500" />
                    Risk Factors
                  </CardTitle>
                  <CardDescription>
                    Potential challenges to consider
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {data.riskFactors.map((factor, index) => (
                      <div key={index} className="flex items-start gap-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <AlertTriangle className="w-4 h-4 text-yellow-600 mt-0.5" />
                        <div className="flex-1">
                          <p className="text-sm font-medium text-yellow-800">{factor.title}</p>
                          <p className="text-xs text-yellow-600 mt-1">{factor.description}</p>
                          <Badge variant="outline" className="mt-2 text-xs border-yellow-300 text-yellow-700">
                            -{factor.impact}% impact
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="improvements" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <Zap className="w-4 h-4" />
                  Optimization Suggestions
                </CardTitle>
                <CardDescription>
                  Actionable steps to improve predicted performance
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {data.optimizationSuggestions.map((suggestion, index) => (
                    <div key={index} className="p-4 border rounded-lg hover:bg-secondary/50 transition-colors">
                      <div className="flex items-start gap-3 mb-3">
                        <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center text-sm font-medium text-primary">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          <h4 className="font-medium text-sm">{suggestion.title}</h4>
                          <p className="text-xs text-muted-foreground mt-1">{suggestion.description}</p>
                        </div>
                        <OptimizationBadge
                          score={suggestion.potentialImprovement}
                          size="sm"
                          variant="score"
                          label="boost"
                        />
                      </div>
                      <div className="ml-11">
                        <Badge variant="outline" className="text-xs">
                          {suggestion.difficulty} difficulty
                        </Badge>
                        <Badge variant="outline" className="text-xs ml-2">
                          {suggestion.category}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Potential Impact</CardTitle>
                <CardDescription>
                  If you implement all suggested optimizations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="text-center p-4 bg-secondary/50 rounded-lg">
                      <div className="text-xl font-bold text-muted-foreground mb-1">
                        {data.overallScore}
                      </div>
                      <p className="text-sm text-muted-foreground">Current Score</p>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div className="text-center p-4 bg-primary/10 rounded-lg">
                      <div className="text-xl font-bold text-primary mb-1">
                        {data.optimizedScore}
                      </div>
                      <p className="text-sm text-muted-foreground">Optimized Score</p>
                    </div>
                  </div>
                </div>
                <div className="mt-4 text-center">
                  <Badge className="bg-green-100 text-green-800 border-green-300">
                    +{data.optimizedScore - data.overallScore} point improvement
                  </Badge>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}

      {/* Empty State */}
      {!data && (
        <Card>
          <CardContent className="text-center py-12">
            <BarChart3 className="w-12 h-12 mx-auto text-muted-foreground/50 mb-4" />
            <h3 className="font-medium mb-2">Ready to predict performance?</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Enter your content details above to get AI-powered performance predictions
            </p>
            <Badge variant="outline" className="text-xs">
              {niche ? `Optimized for ${niche}` : 'Works better with niche information'}
            </Badge>
          </CardContent>
        </Card>
      )}
    </div>
  )
}