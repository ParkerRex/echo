// @ts-nocheck
'use client'

import { trpc } from '@/lib/trpc'
import { Card, CardContent } from '@echo/ui/card'
import { Button } from '@echo/ui/button'
import { Video, Clock, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

interface VideoHistoryProps {
  onSelectVideo: (videoId: string) => void
}

export function VideoHistory({ onSelectVideo }: VideoHistoryProps) {
  const { data, isLoading } = trpc.video.list.useQuery({
    limit: 10,
    offset: 0,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (!data?.items.length) {
    return (
      <div className="text-center py-12">
        <Video className="w-12 h-12 mx-auto text-muted-foreground/50 mb-4" />
        <p className="text-muted-foreground">No videos uploaded yet</p>
        <p className="text-sm text-muted-foreground mt-2">
          Upload your first video to get started
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {data.items.map((video) => {
        const job = video.jobs?.[0]
        const isProcessing = video.status === 'processing'
        const hasFailed = video.status === 'failed' || job?.status === 'failed'
        const isComplete = video.status === 'published' || job?.status === 'completed'

        return (
          <Card
            key={video.id}
            className="cursor-pointer hover:border-border/80 transition-colors"
            onClick={() => onSelectVideo(video.id)}
          >
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="font-medium text-foreground mb-1">
                    {video.fileName}
                  </h3>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <span>{(video.fileSize! / (1024 * 1024)).toFixed(1)} MB</span>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {formatDistanceToNow(new Date(video.createdAt), { addSuffix: true })}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {isProcessing && (
                    <div className="flex items-center gap-2 px-3 py-1 bg-orange-50 dark:bg-orange-950/20 text-orange-600 dark:text-orange-400 rounded-full text-sm">
                      <Loader2 className="w-3 h-3 animate-spin" />
                      Processing
                    </div>
                  )}
                  {isComplete && (
                    <div className="flex items-center gap-2 px-3 py-1 bg-green-50 dark:bg-green-950/20 text-green-600 dark:text-green-400 rounded-full text-sm">
                      <CheckCircle className="w-3 h-3" />
                      Complete
                    </div>
                  )}
                  {hasFailed && (
                    <div className="flex items-center gap-2 px-3 py-1 bg-red-50 dark:bg-red-950/20 text-red-600 dark:text-red-400 rounded-full text-sm">
                      <AlertCircle className="w-3 h-3" />
                      Failed
                    </div>
                  )}
                </div>
              </div>
              {video.metadata?.[0]?.generatedTitles?.[0] && (
                <p className="mt-3 text-sm text-muted-foreground line-clamp-1">
                  "{video.metadata[0].generatedTitles[0]}"
                </p>
              )}
            </CardContent>
          </Card>
        )
      })}
      
      {data.hasMore && (
        <div className="text-center pt-4">
          <Button variant="outline" size="sm">
            Load more
          </Button>
        </div>
      )}
    </div>
  )
}