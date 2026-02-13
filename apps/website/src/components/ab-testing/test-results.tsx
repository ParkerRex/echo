'use client'

import { useState } from 'react'
import { trpc } from '@/lib/trpc'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@echo/ui/card'
import { Button } from '@echo/ui/button'
import { Badge } from '@echo/ui/badge'
import { Progress } from '@echo/ui/progress'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@echo/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@echo/ui/tabs'
import { 
  FlaskConical, 
  TrendingUp, 
  TrendingDown, 
  Target, 
  Clock, 
  Users, 
  Eye, 
  Heart,
  Play,
  Trophy,
  AlertTriangle,
  CheckCircle,
  Pause,
  Square
} from 'lucide-react'
import { MetricCard } from '@/components/shared/metric-card'
import { PerformanceGauge } from '@/components/shared/performance-gauge'
import { OptimizationBadge } from '@/components/shared/optimization-badge'

interface TestResultsProps {
  testId?: string
}

export function TestResults({ testId }: TestResultsProps) {
  const [selectedMetric, setSelectedMetric] = useState<'ctr' | 'watchTime' | 'engagement' | 'conversions'>('ctr')

  // Get active tests
  const { data: activeTests, isLoading: testsLoading } = trpc.contentStrategy.getActiveABTests.useQuery()

  // Get test results for specific test
  const { data: testResults, isLoading: resultsLoading } = trpc.contentStrategy.getABTestResults.useQuery(
    { testId: testId || '' },
    { enabled: !!testId }
  )

  // Control test mutations
  const pauseTest = trpc.contentStrategy.pauseABTest.useMutation()
  const stopTest = trpc.contentStrategy.stopABTest.useMutation()
  const declareWinner = trpc.contentStrategy.declareABTestWinner.useMutation()

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <Play className="w-4 h-4 text-green-500" />
      case 'paused': return <Pause className="w-4 h-4 text-yellow-500" />
      case 'completed': return <CheckCircle className="w-4 h-4 text-blue-500" />
      case 'cancelled': return <Square className="w-4 h-4 text-gray-500" />
      default: return <Clock className="w-4 h-4" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'default'
      case 'paused': return 'secondary'
      case 'completed': return 'outline'
      case 'cancelled': return 'destructive'
      default: return 'secondary'
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 95) return 'success'
    if (confidence >= 80) return 'warning'
    return 'danger'
  }

  const formatPercentage = (value: number) => `${(value * 100).toFixed(1)}%`
  const formatDuration = (seconds: number) => `${Math.round(seconds / 60)}:${(seconds % 60).toString().padStart(2, '0')}`

  if (testsLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-6 bg-secondary rounded w-48 mb-2"></div>
          <div className="h-4 bg-secondary rounded w-96"></div>
        </div>
        <div className="grid gap-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="animate-pulse">
              <div className="h-32 bg-secondary rounded"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <FlaskConical className="w-5 h-5 text-primary" />
            A/B Test Results
          </h3>
          <p className="text-sm text-muted-foreground">
            Monitor and analyze your content experiments
          </p>
        </div>
        {activeTests && activeTests.length > 0 && (
          <Badge variant="outline">
            {activeTests.length} active test{activeTests.length !== 1 ? 's' : ''}
          </Badge>
        )}
      </div>

      {/* Active Tests Overview */}
      {activeTests && activeTests.length > 0 && (
        <div className="grid gap-4">
          {activeTests.map((test) => (
            <Card key={test.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-base flex items-center gap-2">
                      {test.name}
                      {getStatusIcon(test.status)}
                    </CardTitle>
                    <CardDescription className="flex items-center gap-4 mt-1">
                      <span>Testing: {test.testType}</span>
                      <Badge variant={getStatusColor(test.status) as any}>
                        {test.status}
                      </Badge>
                      <span className="text-xs">
                        {test.daysRemaining} days remaining
                      </span>
                    </CardDescription>
                  </div>
                  <div className="flex gap-2">
                    {test.status === 'running' && (
                      <>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => pauseTest.mutate({ testId: test.id })}
                        >
                          <Pause className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => stopTest.mutate({ testId: test.id })}
                        >
                          <Square className="w-4 h-4" />
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-4 gap-4 mb-4">
                  <MetricCard
                    title="Participants"
                    value={test.totalParticipants?.toLocaleString() || '0'}
                    icon={<Users className="w-4 h-4" />}
                  />
                  <MetricCard
                    title="Best CTR"
                    value={formatPercentage(test.bestCTR || 0)}
                    icon={<Eye className="w-4 h-4" />}
                    trend={test.ctrTrend}
                  />
                  <MetricCard
                    title="Confidence"
                    value={`${test.confidence || 0}%`}
                    icon={<Target className="w-4 h-4" />}
                    badge={{
                      text: test.confidence >= 95 ? 'High' : test.confidence >= 80 ? 'Medium' : 'Low',
                      variant: getConfidenceColor(test.confidence || 0) as any
                    }}
                  />
                  <MetricCard
                    title="Progress"
                    value={`${test.progress || 0}%`}
                    icon={<Clock className="w-4 h-4" />}
                  />
                </div>

                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span>Test Progress</span>
                    <span>{test.progress || 0}% complete</span>
                  </div>
                  <Progress value={test.progress || 0} className="h-2" />
                </div>

                {test.hasWinner && test.winningVariant && (
                  <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <Trophy className="w-4 h-4 text-green-600" />
                      <span className="font-medium text-green-800">We have a winner!</span>
                    </div>
                    <p className="text-sm text-green-700">
                      "{test.winningVariant.name}" is performing {test.improvementPercentage}% better
                    </p>
                    {test.canDeclareWinner && (
                      <Button
                        size="sm"
                        className="mt-2"
                        onClick={() => declareWinner.mutate({ 
                          testId: test.id, 
                          winningVariantId: test.winningVariant.id 
                        })}
                      >
                        Declare Winner & Apply Changes
                      </Button>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Detailed Results */}
      {testResults && (
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="variants">Variants</TabsTrigger>
            <TabsTrigger value="metrics">Metrics</TabsTrigger>
            <TabsTrigger value="insights">Insights</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              <PerformanceGauge
                value={testResults.overallConfidence}
                label="Confidence Level"
                color={getConfidenceColor(testResults.overallConfidence)}
              />
              <MetricCard
                title="Total Views"
                value={testResults.totalViews.toLocaleString()}
                icon={<Eye className="w-4 h-4" />}
                trend={testResults.viewsTrend}
              />
              <MetricCard
                title="Best CTR"
                value={formatPercentage(testResults.bestCTR)}
                icon={<Target className="w-4 h-4" />}
                trend={testResults.ctrTrend}
              />
              <MetricCard
                title="Improvement"
                value={`+${testResults.maxImprovement}%`}
                icon={<TrendingUp className="w-4 h-4" />}
                badge={{
                  text: 'vs Control',
                  variant: 'default'
                }}
              />
            </div>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Test Summary</CardTitle>
                <CardDescription>
                  Key findings from your A/B test
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {testResults.keyInsights.map((insight, index) => (
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

          <TabsContent value="variants" className="space-y-4">
            <div className="flex items-center gap-4 mb-4">
              <Select value={selectedMetric} onValueChange={(value: any) => setSelectedMetric(value)}>
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ctr">Click-through Rate</SelectItem>
                  <SelectItem value="watchTime">Watch Time</SelectItem>
                  <SelectItem value="engagement">Engagement</SelectItem>
                  <SelectItem value="conversions">Conversions</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid gap-4">
              {testResults.variants.map((variant) => (
                <Card key={variant.id} className={variant.isWinner ? 'border-green-500 bg-green-50' : ''}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-base flex items-center gap-2">
                          {variant.name}
                          {variant.isControl && (
                            <Badge variant="outline">Control</Badge>
                          )}
                          {variant.isWinner && (
                            <Badge className="bg-green-100 text-green-800 border-green-300">
                              <Trophy className="w-3 h-3 mr-1" />
                              Winner
                            </Badge>
                          )}
                        </CardTitle>
                        <CardDescription>
                          {variant.participants.toLocaleString()} participants
                        </CardDescription>
                      </div>
                      <OptimizationBadge
                        score={variant.performanceScore}
                        variant="score"
                        size="sm"
                      />
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="p-3 bg-secondary/50 rounded text-sm">
                        {variant.content}
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="text-center">
                          <div className="text-lg font-semibold">
                            {formatPercentage(variant.metrics.ctr)}
                          </div>
                          <div className="text-xs text-muted-foreground">CTR</div>
                        </div>
                        <div className="text-center">
                          <div className="text-lg font-semibold">
                            {formatDuration(variant.metrics.avgWatchTime)}
                          </div>
                          <div className="text-xs text-muted-foreground">Watch Time</div>
                        </div>
                        <div className="text-center">
                          <div className="text-lg font-semibold">
                            {formatPercentage(variant.metrics.engagementRate)}
                          </div>
                          <div className="text-xs text-muted-foreground">Engagement</div>
                        </div>
                        <div className="text-center">
                          <div className="text-lg font-semibold">
                            {variant.metrics.conversions}
                          </div>
                          <div className="text-xs text-muted-foreground">Conversions</div>
                        </div>
                      </div>

                      {variant.improvementVsControl !== 0 && (
                        <div className="flex items-center gap-2 text-sm">
                          {variant.improvementVsControl > 0 ? (
                            <TrendingUp className="w-4 h-4 text-green-500" />
                          ) : (
                            <TrendingDown className="w-4 h-4 text-red-500" />
                          )}
                          <span className={variant.improvementVsControl > 0 ? 'text-green-600' : 'text-red-600'}>
                            {variant.improvementVsControl > 0 ? '+' : ''}{variant.improvementVsControl}% vs Control
                          </span>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="metrics" className="space-y-4">
            <div className="grid md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Performance Trends</CardTitle>
                  <CardDescription>How metrics changed over time</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {testResults.metricsTrend.map((trend, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded">
                        <div>
                          <div className="font-medium">{trend.date}</div>
                          <div className="text-sm text-muted-foreground">
                            CTR: {formatPercentage(trend.ctr)}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="flex items-center gap-1">
                            {trend.change > 0 ? (
                              <TrendingUp className="w-4 h-4 text-green-500" />
                            ) : (
                              <TrendingDown className="w-4 h-4 text-red-500" />
                            )}
                            <span className={trend.change > 0 ? 'text-green-600' : 'text-red-600'}>
                              {trend.change > 0 ? '+' : ''}{trend.change}%
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Statistical Significance</CardTitle>
                  <CardDescription>Confidence levels for each metric</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {Object.entries(testResults.significanceTests).map(([metric, data]) => (
                      <div key={metric}>
                        <div className="flex justify-between mb-2">
                          <span className="capitalize">{metric}</span>
                          <span className="font-medium">{data.confidence}%</span>
                        </div>
                        <Progress value={data.confidence} className="h-2" />
                        <p className="text-xs text-muted-foreground mt-1">
                          {data.significant ? 'Statistically significant' : 'Not significant'}
                        </p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="insights" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Key Learnings</CardTitle>
                <CardDescription>
                  Actionable insights from your test results
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {testResults.actionableInsights.map((insight, index) => (
                    <div key={index} className="flex items-start gap-3 p-4 border rounded-lg">
                      <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                        <Lightbulb className="w-4 h-4 text-primary" />
                      </div>
                      <div className="flex-1">
                        <h4 className="font-medium mb-1">{insight.title}</h4>
                        <p className="text-sm text-muted-foreground mb-2">{insight.description}</p>
                        <Badge variant="outline" className="text-xs">
                          {insight.category}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Recommendations</CardTitle>
                <CardDescription>
                  Next steps to improve performance
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {testResults.recommendations.map((rec, index) => (
                    <div key={index} className="flex items-start gap-3 p-3 bg-secondary/30 rounded-lg">
                      <div className="w-6 h-6 bg-primary/10 rounded-full flex items-center justify-center text-sm font-medium text-primary mt-0.5">
                        {index + 1}
                      </div>
                      <p className="text-sm flex-1">{rec}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}

      {/* Empty State */}
      {!activeTests?.length && !testResults && (
        <Card>
          <CardContent className="text-center py-12">
            <FlaskConical className="w-12 h-12 mx-auto text-muted-foreground/50 mb-4" />
            <h3 className="font-medium mb-2">No active tests</h3>
            <p className="text-sm text-muted-foreground">
              Create your first A/B test to start optimizing your content performance
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}