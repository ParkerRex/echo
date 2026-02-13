'use client'

import { useState } from 'react'
import { trpc } from '@/lib/trpc'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@echo/ui/card'
import { Button } from '@echo/ui/button'
import { Input } from '@echo/ui/input'
import { Label } from '@echo/ui/label'
import { Textarea } from '@echo/ui/textarea'
import { Badge } from '@echo/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@echo/ui/tabs'
import { Search, Target, Wand2, Loader2, Copy, CheckCircle } from 'lucide-react'
import { OptimizationBadge } from '@/components/shared/optimization-badge'
import { PerformanceGauge } from '@/components/shared/performance-gauge'
import { KeywordPill } from '@/components/shared/keyword-pill'

interface SEOOptimizerProps {
  initialTitle?: string
  initialDescription?: string
  niche?: string
}

export function SEOOptimizer({ initialTitle = '', initialDescription = '', niche }: SEOOptimizerProps) {
  const [title, setTitle] = useState(initialTitle)
  const [description, setDescription] = useState(initialDescription)
  const [targetKeywords, setTargetKeywords] = useState<string[]>([])
  const [newKeyword, setNewKeyword] = useState('')
  const [copied, setCopied] = useState<string | null>(null)

  // Optimize title mutation
  const optimizeTitle = trpc.contentStrategy.optimizeTitle.useMutation()

  // Generate SEO content mutation
  const generateSEOContent = trpc.contentStrategy.generateSEOContent.useMutation()

  const handleOptimizeTitle = async () => {
    if (!title.trim()) return
    
    await optimizeTitle.mutateAsync({
      originalTitle: title,
      niche: niche || '',
      targetKeywords
    })
  }

  const handleGenerateSEOContent = async () => {
    if (!title.trim()) return

    await generateSEOContent.mutateAsync({
      title,
      niche: niche || '',
      targetKeywords,
      includeDescription: true,
      includeTags: true
    })
  }

  const handleAddKeyword = () => {
    if (newKeyword.trim() && !targetKeywords.includes(newKeyword.trim())) {
      setTargetKeywords([...targetKeywords, newKeyword.trim()])
      setNewKeyword('')
    }
  }

  const handleRemoveKeyword = (keyword: string) => {
    setTargetKeywords(targetKeywords.filter(k => k !== keyword))
  }

  const handleCopy = async (text: string, type: string) => {
    await navigator.clipboard.writeText(text)
    setCopied(type)
    setTimeout(() => setCopied(null), 2000)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Target className="w-5 h-5 text-primary" />
          SEO Optimizer
        </h3>
        <p className="text-sm text-muted-foreground">
          Optimize your content for better search visibility and performance
        </p>
      </div>

      {/* Input Form */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Content to Optimize</CardTitle>
          <CardDescription>
            Enter your content details to get AI-powered SEO recommendations
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
            <Label htmlFor="description">Description (Optional)</Label>
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
            <Label>Target Keywords</Label>
            <div className="flex gap-2 mb-2">
              <Input
                value={newKeyword}
                onChange={(e) => setNewKeyword(e.target.value)}
                placeholder="Add a target keyword..."
                onKeyPress={(e) => e.key === 'Enter' && handleAddKeyword()}
              />
              <Button onClick={handleAddKeyword} disabled={!newKeyword.trim()}>
                Add
              </Button>
            </div>
            {targetKeywords.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {targetKeywords.map((keyword) => (
                  <KeywordPill
                    key={keyword}
                    keyword={keyword}
                    removable
                    onRemove={() => handleRemoveKeyword(keyword)}
                  />
                ))}
              </div>
            )}
          </div>

          <div className="flex gap-2">
            <Button
              onClick={handleOptimizeTitle}
              disabled={!title.trim() || optimizeTitle.isPending}
            >
              {optimizeTitle.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Wand2 className="w-4 h-4" />
              )}
              Optimize Title
            </Button>
            <Button
              variant="outline"
              onClick={handleGenerateSEOContent}
              disabled={!title.trim() || generateSEOContent.isPending}
            >
              {generateSEOContent.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Search className="w-4 h-4" />
              )}
              Full SEO Analysis
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Optimization Results */}
      {(optimizeTitle.data || generateSEOContent.data) && (
        <Tabs defaultValue="title" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="title">Title Optimization</TabsTrigger>
            <TabsTrigger value="content">SEO Content</TabsTrigger>
            <TabsTrigger value="analysis">Analysis</TabsTrigger>
          </TabsList>

          <TabsContent value="title" className="space-y-4">
            {optimizeTitle.data && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base flex items-center justify-between">
                    Optimized Titles
                    <OptimizationBadge
                      score={optimizeTitle.data.overallScore}
                      variant="score"
                      size="sm"
                    />
                  </CardTitle>
                  <CardDescription>
                    AI-generated title variations optimized for SEO
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {optimizeTitle.data.suggestions.map((suggestion, index) => (
                    <div
                      key={index}
                      className="p-4 border rounded-lg hover:bg-secondary/50 transition-colors"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-medium flex-1 pr-4">{suggestion.title}</h4>
                        <div className="flex items-center gap-2">
                          <OptimizationBadge
                            score={suggestion.seoScore}
                            size="sm"
                            variant="score"
                          />
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleCopy(suggestion.title, `title-${index}`)}
                          >
                            {copied === `title-${index}` ? (
                              <CheckCircle className="w-4 h-4 text-green-500" />
                            ) : (
                              <Copy className="w-4 h-4" />
                            )}
                          </Button>
                        </div>
                      </div>
                      <p className="text-sm text-muted-foreground mb-3">
                        {suggestion.reasoning}
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {suggestion.targetKeywords.map((keyword, i) => (
                          <Badge key={i} variant="outline" className="text-xs">
                            {keyword}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="content" className="space-y-4">
            {generateSEOContent.data && (
              <>
                {/* Description Suggestions */}
                {generateSEOContent.data.descriptions && generateSEOContent.data.descriptions.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Optimized Descriptions</CardTitle>
                      <CardDescription>
                        SEO-friendly descriptions to improve discoverability
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {generateSEOContent.data.descriptions.map((desc, index) => (
                        <div
                          key={index}
                          className="p-3 border rounded-lg relative group"
                        >
                          <p className="text-sm mb-2 pr-8">{desc}</p>
                          <Button
                            size="sm"
                            variant="ghost"
                            className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
                            onClick={() => handleCopy(desc, `desc-${index}`)}
                          >
                            {copied === `desc-${index}` ? (
                              <CheckCircle className="w-4 h-4 text-green-500" />
                            ) : (
                              <Copy className="w-4 h-4" />
                            )}
                          </Button>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                )}

                {/* Tag Suggestions */}
                {generateSEOContent.data.tags && generateSEOContent.data.tags.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Recommended Tags</CardTitle>
                      <CardDescription>
                        Tags to help your content get discovered
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-wrap gap-2">
                        {generateSEOContent.data.tags.map((tag, index) => (
                          <KeywordPill
                            key={index}
                            keyword={tag}
                            copyable
                            className="text-sm"
                          />
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </>
            )}
          </TabsContent>

          <TabsContent value="analysis" className="space-y-4">
            {(optimizeTitle.data || generateSEOContent.data) && (
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                <PerformanceGauge
                  value={optimizeTitle.data?.overallScore || generateSEOContent.data?.seoScore || 0}
                  label="SEO Score"
                />
                <PerformanceGauge
                  value={optimizeTitle.data?.keywordRelevance || 75}
                  label="Keyword Relevance"
                />
                <PerformanceGauge
                  value={optimizeTitle.data?.readabilityScore || 80}
                  label="Readability"
                />
                <PerformanceGauge
                  value={optimizeTitle.data?.clickabilityScore || 70}
                  label="Clickability"
                />
              </div>
            )}

            {optimizeTitle.data?.improvements && optimizeTitle.data.improvements.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Improvement Suggestions</CardTitle>
                  <CardDescription>
                    Actionable recommendations to boost your SEO performance
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {optimizeTitle.data.improvements.map((improvement, index) => (
                      <div key={index} className="flex items-start gap-3 p-3 bg-secondary/30 rounded-lg">
                        <div className="w-6 h-6 bg-primary/10 rounded-full flex items-center justify-center text-sm font-medium text-primary mt-0.5">
                          {index + 1}
                        </div>
                        <p className="text-sm flex-1">{improvement}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      )}

      {/* Empty State */}
      {!optimizeTitle.data && !generateSEOContent.data && (
        <Card>
          <CardContent className="text-center py-12">
            <Target className="w-12 h-12 mx-auto text-muted-foreground/50 mb-4" />
            <h3 className="font-medium mb-2">Ready to optimize your content?</h3>
            <p className="text-sm text-muted-foreground">
              Enter your title and keywords above to get AI-powered SEO recommendations
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}