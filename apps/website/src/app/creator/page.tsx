'use client'

import { trpc } from '@/lib/trpc'
import { Button } from '@echo/ui/button'
import { Card } from '@echo/ui/card'
import {
  AlertCircle,
  Calendar,
  CheckCircle,
  Clock,
  Eye,
  MoreHorizontal,
  Play,
  Sparkles,
  TrendingUp,
  Upload,
  Video,
} from 'lucide-react'
import Image from 'next/image'
import Link from 'next/link'
import { useState } from 'react'

export default function CreatorPage() {
  const [view, setView] = useState<'grid' | 'list'>('grid')

  // Protected route - user must be authenticated to access
  const { data: videos, isLoading } = trpc.video.list.useQuery({
    limit: 20,
    offset: 0,
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'processing':
        return <Clock className="w-4 h-4 text-orange-500" />
      case 'published':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-500" />
      default:
        return <Video className="w-4 h-4 text-muted-foreground" />
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'processing':
        return 'Processing'
      case 'published':
        return 'Ready'
      case 'failed':
        return 'Failed'
      default:
        return 'Draft'
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b border-border/50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Link href="/" className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                  <Video className="w-4 h-4 text-primary-foreground" />
                </div>
                <span className="text-xl font-semibold">Echo</span>
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="outline" size="sm">
                <TrendingUp className="w-4 h-4 mr-2" />
                Analytics
              </Button>
              <Link href="/">
                <Button size="sm">
                  <Upload className="w-4 h-4 mr-2" />
                  Upload Video
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-6 py-8 max-w-7xl">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-semibold mb-2">My Videos</h1>
            <p className="text-muted-foreground">
              Manage your uploaded videos and their optimization results
            </p>
          </div>

          <div className="flex items-center gap-4 mt-4 sm:mt-0">
            <div className="flex bg-secondary rounded-lg p-1">
              <button
                onClick={() => setView('grid')}
                className={`px-3 py-2 text-sm rounded-md transition-colors ${
                  view === 'grid'
                    ? 'bg-background text-foreground shadow-sm'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                Grid
              </button>
              <button
                onClick={() => setView('list')}
                className={`px-3 py-2 text-sm rounded-md transition-colors ${
                  view === 'list'
                    ? 'bg-background text-foreground shadow-sm'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                List
              </button>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Videos</p>
                <p className="text-2xl font-semibold">{videos?.totalCount || 0}</p>
              </div>
              <Video className="w-8 h-8 text-muted-foreground" />
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Processing</p>
                <p className="text-2xl font-semibold">
                  {videos?.items?.filter((v: any) => v.status === 'processing').length || 0}
                </p>
              </div>
              <Clock className="w-8 h-8 text-orange-500" />
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Ready</p>
                <p className="text-2xl font-semibold">
                  {videos?.items?.filter((v: any) => v.status === 'published').length || 0}
                </p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">This Month</p>
                <p className="text-2xl font-semibold">
                  {videos?.items?.filter((v: any) => {
                    const videoDate = new Date(v.createdAt)
                    const now = new Date()
                    return (
                      videoDate.getMonth() === now.getMonth() &&
                      videoDate.getFullYear() === now.getFullYear()
                    )
                  }).length || 0}
                </p>
              </div>
              <Calendar className="w-8 h-8 text-muted-foreground" />
            </div>
          </Card>
        </div>

        {/* Videos Grid/List */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <Card key={i} className="p-6">
                <div className="animate-pulse">
                  <div className="aspect-video bg-secondary rounded-lg mb-4" />
                  <div className="h-4 bg-secondary rounded w-3/4 mb-2" />
                  <div className="h-3 bg-secondary rounded w-1/2" />
                </div>
              </Card>
            ))}
          </div>
        ) : videos?.items?.length === 0 ? (
          <Card className="p-12 text-center">
            <Video className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No videos yet</h3>
            <p className="text-muted-foreground mb-6">
              Upload your first video to get started with AI-powered optimization
            </p>
            <Link href="/">
              <Button>
                <Upload className="w-4 h-4 mr-2" />
                Upload Your First Video
              </Button>
            </Link>
          </Card>
        ) : (
          <div
            className={
              view === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-4'
            }
          >
            {videos?.items?.map((video: any) => (
              <Card
                key={video.id}
                className={`overflow-hidden hover:shadow-lg transition-all cursor-pointer ${
                  view === 'list' ? 'p-6' : ''
                }`}
              >
                {view === 'grid' ? (
                  <>
                    <div className="aspect-video bg-secondary relative">
                      {video.metadata?.[0]?.thumbnail ? (
                        <Image
                          src={video.metadata[0].thumbnail}
                          alt={video.fileName}
                          fill
                          className="object-cover"
                        />
                      ) : (
                        <div className="flex items-center justify-center h-full">
                          <Video className="w-12 h-12 text-muted-foreground" />
                        </div>
                      )}
                      <div className="absolute top-3 right-3 flex items-center gap-2">
                        {getStatusIcon(video.status)}
                      </div>
                      {video.status === 'published' && (
                        <div className="absolute bottom-3 left-3">
                          <Button
                            size="sm"
                            variant="secondary"
                            className="bg-black/50 hover:bg-black/70 text-white border-0"
                          >
                            <Play className="w-3 h-3 mr-1" />
                            View Results
                          </Button>
                        </div>
                      )}
                    </div>

                    <div className="p-6">
                      <div className="flex items-start justify-between mb-3">
                        <h3 className="font-medium text-sm leading-tight line-clamp-2">
                          {video.metadata?.[0]?.title || video.fileName}
                        </h3>
                        <button className="p-1 hover:bg-secondary rounded">
                          <MoreHorizontal className="w-4 h-4 text-muted-foreground" />
                        </button>
                      </div>

                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          {getStatusIcon(video.status)}
                          {getStatusLabel(video.status)}
                        </span>
                        <span>{new Date(video.createdAt).toLocaleDateString()}</span>
                      </div>

                      <div className="mt-3 flex items-center gap-4 text-xs text-muted-foreground">
                        <span>{(video.fileSize / (1024 * 1024)).toFixed(1)} MB</span>
                        {video.duration && (
                          <span>
                            {Math.floor(video.duration / 60)}:
                            {(video.duration % 60).toString().padStart(2, '0')}
                          </span>
                        )}
                      </div>

                      {video.metadata?.[0]?.generatedTitles && (
                        <div className="mt-4 flex items-center gap-1 text-xs">
                          <Sparkles className="w-3 h-3 text-primary" />
                          <span className="text-muted-foreground">
                            {video.metadata[0].generatedTitles.length} titles generated
                          </span>
                        </div>
                      )}
                    </div>
                  </>
                ) : (
                  <div className="flex items-center gap-6">
                    <div className="w-32 h-20 bg-secondary rounded-lg relative flex-shrink-0">
                      {video.metadata?.[0]?.thumbnail ? (
                        <Image
                          src={video.metadata[0].thumbnail}
                          alt={video.fileName}
                          fill
                          className="object-cover rounded-lg"
                        />
                      ) : (
                        <div className="flex items-center justify-center h-full">
                          <Video className="w-8 h-8 text-muted-foreground" />
                        </div>
                      )}
                    </div>

                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-sm mb-1 truncate">
                        {video.metadata?.[0]?.title || video.fileName}
                      </h3>
                      <div className="flex items-center gap-4 text-xs text-muted-foreground mb-2">
                        <span className="flex items-center gap-1">
                          {getStatusIcon(video.status)}
                          {getStatusLabel(video.status)}
                        </span>
                        <span>{new Date(video.createdAt).toLocaleDateString()}</span>
                        <span>{(video.fileSize / (1024 * 1024)).toFixed(1)} MB</span>
                      </div>
                      {video.metadata?.[0]?.generatedTitles && (
                        <div className="flex items-center gap-1 text-xs">
                          <Sparkles className="w-3 h-3 text-primary" />
                          <span className="text-muted-foreground">
                            {video.metadata[0].generatedTitles.length} titles •
                            {video.metadata[0].thumbnailUrls?.length || 0} thumbnails
                          </span>
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      {video.status === 'published' && (
                        <Button size="sm" variant="outline">
                          <Eye className="w-4 h-4 mr-1" />
                          View
                        </Button>
                      )}
                      <button className="p-2 hover:bg-secondary rounded">
                        <MoreHorizontal className="w-4 h-4 text-muted-foreground" />
                      </button>
                    </div>
                  </div>
                )}
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
