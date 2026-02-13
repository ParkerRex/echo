// @ts-nocheck
'use client'

import { trpc } from '@/lib/trpc'
import { ArrowLeft, CheckCircle, Copy, Download, RefreshCw, TrendingUp, Search, Target, Lightbulb, FlaskConical, BarChart3 } from 'lucide-react'
import Image from 'next/image'
import { useEffect, useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@echo/ui/tabs'
import { Badge } from '@echo/ui/badge'
import { ContentStrategy } from '@/components/content-strategy'
import { ABTesting } from '@/components/ab-testing'
import { PerformancePrediction } from '@/components/performance-prediction'

interface VideoResultsProps {
  videoId: string
  onReset: () => void
}

export function VideoResults({ videoId, onReset }: VideoResultsProps) {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null)
  const [selectedThumbnail, setSelectedThumbnail] = useState(0)

  // Poll for job status
  const { data: video, isLoading } = trpc.video.getById.useQuery(
    { videoId: videoId },
    {
      refetchInterval: (data: any) => {
        // Poll every 2 seconds if processing
        if (data?.status === 'processing') return 2000
        return false
      },
    }
  )

  const { data: jobStatus } = trpc.video.getJobStatus.useQuery(
    { jobId: video?.jobs?.[0]?.id || '' },
    {
      enabled: !!video?.jobs?.[0]?.id && video?.status === 'processing',
      refetchInterval: 2000,
    }
  )

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text)
    setCopiedIndex(index)
    setTimeout(() => setCopiedIndex(null), 2000)
  }

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto text-center py-12">
        <div className="animate-pulse">
          <div className="h-8 bg-secondary rounded-lg w-64 mx-auto mb-4"></div>
          <div className="h-4 bg-secondary rounded-lg w-48 mx-auto"></div>
        </div>
      </div>
    )
  }

  if (!video) {
    return (
      <div className="max-w-6xl mx-auto text-center py-12">
        <p className="text-destructive mb-4">Video not found</p>
        <button
          type="button"
          onClick={onReset}
          className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Upload another video
        </button>
      </div>
    )
  }

  const isProcessing = video.status === 'processing'
  const metadata = video.metadata?.[0] // Get the latest metadata

  // Extract content data for components
  const firstTitle = metadata?.generatedTitles?.[0] || ''
  const description = metadata?.description || ''
  const thumbnailUrl = metadata?.thumbnailUrls?.[0] || ''

  return (
    <div className="max-w-7xl mx-auto">
      <button
        type="button"
        onClick={onReset}
        className="mb-6 inline-flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Upload another video
      </button>

      <div className="bg-card rounded-2xl border border-border/50 overflow-hidden">
        {/* Video Header */}
        <div className="p-8 border-b border-border/50">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-2xl font-semibold mb-2">{video.fileName}</h2>
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <span>{(video.fileSize / (1024 * 1024)).toFixed(1)} MB</span>
                <span>•</span>
                <span>{video.mimeType}</span>
                {video.duration && (
                  <>
                    <span>•</span>
                    <span>
                      {Math.floor(video.duration / 60)}:
                      {(video.duration % 60).toString().padStart(2, '0')}
                    </span>
                  </>
                )}
              </div>
            </div>
            <div className="flex items-center gap-3">
              {isProcessing ? (
                <div className="flex items-center gap-2 px-3 py-2 bg-orange-50 dark:bg-orange-950/20 text-orange-600 dark:text-orange-400 rounded-full text-sm font-medium">
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Processing
                </div>
              ) : (
                <div className="flex items-center gap-2 px-3 py-2 bg-green-50 dark:bg-green-950/20 text-green-600 dark:text-green-400 rounded-full text-sm font-medium">
                  <CheckCircle className="w-4 h-4" />
                  Complete
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Processing Status */}
        {isProcessing && jobStatus && (
          <div className="p-6 bg-secondary/30">
            <div className="flex items-center justify-between mb-4">
              <p className="font-medium">Processing your video...</p>
              <span className="text-sm text-muted-foreground">{jobStatus.progress || 0}%</span>
            </div>
            {jobStatus.progress !== undefined && (
              <div className="w-full bg-border rounded-full h-2 overflow-hidden">
                <div
                  className="bg-primary h-full transition-all duration-500 ease-out rounded-full"
                  style={{ width: `${jobStatus.progress}%` }}
                />
              </div>
            )}
            <p className="text-sm text-muted-foreground mt-3">
              {jobStatus.error || 'Analyzing video content and generating optimizations...'}
            </p>
          </div>
        )}

        {/* Main Content Hub */}
        {metadata && !isProcessing && (
          <div className="p-8">
            <Tabs defaultValue="results" className="w-full">
              <TabsList className="grid w-full grid-cols-5 mb-8">
                <TabsTrigger value="results" className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" />
                  <span className="hidden sm:inline">Results</span>
                </TabsTrigger>
                <TabsTrigger value="strategy" className="flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" />
                  <span className="hidden sm:inline">Strategy</span>
                </TabsTrigger>
                <TabsTrigger value="testing" className="flex items-center gap-2">
                  <FlaskConical className="w-4 h-4" />
                  <span className="hidden sm:inline">A/B Testing</span>
                </TabsTrigger>
                <TabsTrigger value="prediction" className="flex items-center gap-2">
                  <BarChart3 className="w-4 h-4" />
                  <span className="hidden sm:inline">Prediction</span>
                </TabsTrigger>
                <TabsTrigger value="analytics" className="flex items-center gap-2">
                  <Target className="w-4 h-4" />
                  <span className="hidden sm:inline">Analytics</span>
                </TabsTrigger>
              </TabsList>

              {/* Original Results Tab */}
              <TabsContent value="results" className="space-y-8">
                {/* Generated Titles */}
                <section>
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-xl font-semibold">10 Optimized Titles</h3>
                    <span className="text-sm text-muted-foreground bg-secondary px-3 py-1 rounded-full">
                      Click to copy
                    </span>
                  </div>
                  <div className="grid gap-3">
                    {metadata.generatedTitles?.map((title: string, index: number) => (
                      <div
                        key={index}
                        className="group flex items-start gap-4 p-4 bg-secondary/50 rounded-xl hover:bg-secondary transition-colors cursor-pointer"
                        onClick={() => copyToClipboard(title, index)}
                      >
                        <div className="flex-shrink-0 w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center text-sm font-medium text-primary">
                          {index + 1}
                        </div>
                        <p className="flex-1 text-sm leading-relaxed">{title}</p>
                        <button
                          type="button"
                          className="opacity-0 group-hover:opacity-100 p-2 text-muted-foreground hover:text-foreground transition-all"
                          title="Copy to clipboard"
                        >
                          {copiedIndex === index ? (
                            <CheckCircle className="w-5 h-5 text-green-500" />
                          ) : (
                            <Copy className="w-5 h-5" />
                          )}
                        </button>
                      </div>
                    ))}
                  </div>
                </section>

                {/* Thumbnails */}
                {metadata.thumbnailUrls && metadata.thumbnailUrls.length > 0 && (
                  <section>
                    <div className="flex items-center justify-between mb-6">
                      <h3 className="text-xl font-semibold">AI Thumbnail Backgrounds</h3>
                      <span className="text-sm text-muted-foreground bg-secondary px-3 py-1 rounded-full">
                        {metadata.thumbnailUrls.length} generated
                      </span>
                    </div>

                    <div className="grid lg:grid-cols-2 gap-8">
                      <div>
                        <p className="text-sm text-muted-foreground mb-4">
                          Select a thumbnail background to preview and download
                        </p>
                        <div className="grid grid-cols-2 gap-3">
                          {metadata.thumbnailUrls.map((url: string, index: number) => (
                            <button
                              type="button"
                              key={index}
                              onClick={() => setSelectedThumbnail(index)}
                              className={`relative aspect-video rounded-xl overflow-hidden border-2 transition-all hover:scale-105 ${
                                selectedThumbnail === index
                                  ? 'border-primary shadow-lg'
                                  : 'border-border hover:border-border/80'
                              }`}
                            >
                              <Image
                                src={url}
                                alt={`Thumbnail ${index + 1}`}
                                fill
                                className="object-cover"
                              />
                              <div className="absolute inset-0 bg-black/20 opacity-0 hover:opacity-100 transition-opacity flex items-center justify-center">
                                <span className="text-white text-sm font-medium">Preview</span>
                              </div>
                              {selectedThumbnail === index && (
                                <div className="absolute top-2 right-2 w-6 h-6 bg-primary rounded-full flex items-center justify-center">
                                  <CheckCircle className="w-4 h-4 text-primary-foreground" />
                                </div>
                              )}
                            </button>
                          ))}
                        </div>
                      </div>

                      {/* Selected Thumbnail Preview */}
                      <div className="bg-secondary/50 rounded-2xl p-6">
                        <h4 className="font-medium mb-4">Preview & Download</h4>
                        <div className="relative aspect-video rounded-xl overflow-hidden mb-6 bg-border">
                          <Image
                            src={metadata.thumbnailUrls[selectedThumbnail]}
                            alt="Selected thumbnail"
                            fill
                            className="object-cover"
                          />
                        </div>
                        <div className="space-y-3">
                          <button
                            type="button"
                            className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-xl hover:bg-primary/90 transition-colors font-medium"
                          >
                            <Download className="w-5 h-5" />
                            Download HD (1920×1080)
                          </button>
                          <p className="text-xs text-muted-foreground text-center">
                            High-quality background ready for your thumbnail design
                          </p>
                        </div>
                      </div>
                    </div>
                  </section>
                )}

                {/* Video Description */}
                {metadata.description && (
                  <section>
                    <div className="flex items-center justify-between mb-6">
                      <h3 className="text-xl font-semibold">Optimized Description</h3>
                      <button
                        type="button"
                        onClick={() => copyToClipboard(metadata.description, -1)}
                        className="flex items-center gap-2 px-3 py-2 text-sm bg-secondary hover:bg-secondary/80 rounded-lg transition-colors"
                      >
                        {copiedIndex === -1 ? (
                          <CheckCircle className="w-4 h-4 text-green-500" />
                        ) : (
                          <Copy className="w-4 h-4" />
                        )}
                        Copy
                      </button>
                    </div>
                    <div className="p-6 bg-secondary/50 rounded-xl border border-border/50">
                      <p className="whitespace-pre-wrap leading-relaxed text-sm">
                        {metadata.description}
                      </p>
                    </div>
                  </section>
                )}

                {/* Tags */}
                {metadata.tags && metadata.tags.length > 0 && (
                  <section>
                    <div className="flex items-center justify-between mb-6">
                      <h3 className="text-xl font-semibold">SEO Tags</h3>
                      <span className="text-sm text-muted-foreground bg-secondary px-3 py-1 rounded-full">
                        {metadata.tags.length} tags
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {metadata.tags.map((tag: string, index: number) => (
                        <button
                          key={index}
                          onClick={() => copyToClipboard(tag, index + 1000)}
                          className="group px-4 py-2 bg-secondary/50 hover:bg-secondary text-sm rounded-lg border border-border/50 hover:border-border transition-all cursor-pointer"
                        >
                          <span className="font-mono text-muted-foreground group-hover:text-foreground">
                            #{tag}
                          </span>
                          {copiedIndex === index + 1000 && (
                            <CheckCircle className="w-3 h-3 text-green-500 inline ml-1" />
                          )}
                        </button>
                      ))}
                    </div>
                    <p className="text-xs text-muted-foreground mt-4">
                      Click any tag to copy it to your clipboard
                    </p>
                  </section>
                )}
              </TabsContent>

              {/* Content Strategy Tab */}
              <TabsContent value="strategy">
                <ContentStrategy
                  initialTitle={firstTitle}
                  initialDescription={description}
                />
              </TabsContent>

              {/* A/B Testing Tab */}
              <TabsContent value="testing">
                <ABTesting
                  videoId={videoId}
                  initialTitle={firstTitle}
                  initialDescription={description}
                  initialThumbnail={thumbnailUrl}
                />
              </TabsContent>

              {/* Performance Prediction Tab */}
              <TabsContent value="prediction">
                <PerformancePrediction
                  initialTitle={firstTitle}
                  initialDescription={description}
                  thumbnailUrl={thumbnailUrl}
                />
              </TabsContent>

              {/* Analytics Tab (Placeholder) */}
              <TabsContent value="analytics">
                <div className="text-center py-12">
                  <Target className="w-12 h-12 mx-auto text-muted-foreground/50 mb-4" />
                  <h3 className="font-medium mb-2">Analytics Dashboard</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Coming soon! Track your video performance and audience insights here.
                  </p>
                  <Badge variant="outline">Under Development</Badge>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        )}

        {/* No Results State */}
        {!isProcessing && !metadata && (
          <div className="text-center py-12">
            <p className="text-muted-foreground mb-4">
              No results generated yet. Please try uploading again.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
