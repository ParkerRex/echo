// @ts-nocheck
'use client'

import { useState } from 'react'
import { trpc } from '@/lib/trpc'
import { Button } from '@echo/ui/button'
import { Input } from '@echo/ui/input'
import { Label } from '@echo/ui/label'
import { Textarea } from '@echo/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@echo/ui/select'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@echo/ui/card'
import { Alert, AlertDescription } from '@echo/ui/alert'
import { Badge } from '@echo/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@echo/ui/tabs'
import { Youtube, Upload, CheckCircle, AlertCircle, ExternalLink, Loader2 } from 'lucide-react'

interface YouTubePublisherProps {
  videoId: string
  metadata: any
}

export function YouTubePublisher({ videoId, metadata }: YouTubePublisherProps) {
  const [selectedTitle, setSelectedTitle] = useState(0)
  const [customTitle, setCustomTitle] = useState('')
  const [description, setDescription] = useState(metadata?.description || '')
  const [tags, setTags] = useState<string[]>(metadata?.tags || [])
  const [privacyStatus, setPrivacyStatus] = useState<'private' | 'unlisted' | 'public'>('private')
  const [categoryId, setCategoryId] = useState('22') // People & Blogs default
  const [selectedThumbnail, setSelectedThumbnail] = useState(0)
  const [publishAt, setPublishAt] = useState('')

  // Check if YouTube is connected
  const { data: connectionStatus } = trpc.youtube.isConnected.useQuery()
  const { data: channelInfo } = trpc.youtube.getChannelInfo.useQuery()
  const { data: categories } = trpc.youtube.getCategories.useQuery()

  // Mutations
  const connectYouTube = trpc.youtube.getAuthUrl.useMutation()
  const publishVideo = trpc.youtube.publishVideo.useMutation()
  const disconnectYouTube = trpc.youtube.disconnect.useMutation()

  const handleConnect = async () => {
    try {
      const { authUrl } = await connectYouTube.mutateAsync({ videoId })
      window.location.href = authUrl
    } catch (error) {
      console.error('Failed to get auth URL:', error)
    }
  }

  const handlePublish = async () => {
    try {
      const finalTitle = customTitle || metadata?.generatedTitles?.[selectedTitle] || 'Untitled Video'
      
      const result = await publishVideo.mutateAsync({
        videoId,
        title: finalTitle,
        description,
        tags,
        categoryId,
        privacyStatus,
        thumbnailIndex: selectedThumbnail,
        publishAt: publishAt || undefined,
      })

      if (result.youtubeUrl) {
        window.open(result.youtubeUrl, '_blank')
      }
    } catch (error) {
      console.error('Failed to publish video:', error)
    }
  }

  const handleDisconnect = async () => {
    if (confirm('Are you sure you want to disconnect your YouTube account?')) {
      await disconnectYouTube.mutateAsync()
    }
  }

  if (!connectionStatus?.isConnected) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Youtube className="w-5 h-5 text-red-600" />
              <CardTitle>Connect YouTube Account</CardTitle>
            </div>
          </div>
          <CardDescription>
            Connect your YouTube account to publish videos directly from Echo
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="bg-secondary/50 rounded-lg p-4 space-y-2">
              <p className="text-sm font-medium">What you'll be able to do:</p>
              <ul className="text-sm text-muted-foreground space-y-1 ml-4">
                <li>• Upload videos directly to YouTube</li>
                <li>• Set custom titles, descriptions, and tags</li>
                <li>• Choose privacy settings and schedule uploads</li>
                <li>• Track video performance and analytics</li>
              </ul>
            </div>
            <Button onClick={handleConnect} className="w-full" size="lg">
              <Youtube className="w-4 h-4 mr-2" />
              Connect YouTube Account
            </Button>
            <p className="text-xs text-center text-muted-foreground">
              You'll be redirected to YouTube to authorize Echo
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Youtube className="w-5 h-5 text-red-600" />
              <CardTitle>Publish to YouTube</CardTitle>
            </div>
            {channelInfo && (
              <p className="text-sm text-muted-foreground">
                Publishing to: {channelInfo.channelName}
              </p>
            )}
          </div>
          <Button variant="ghost" size="sm" onClick={handleDisconnect}>
            Disconnect
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="details" className="space-y-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="details">Details</TabsTrigger>
            <TabsTrigger value="thumbnail">Thumbnail</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          <TabsContent value="details" className="space-y-4">
            {/* Title Selection */}
            <div className="space-y-2">
              <Label>Video Title</Label>
              <div className="space-y-2">
                {metadata?.generatedTitles?.map((title: string, index: number) => (
                  <div
                    key={index}
                    className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                      selectedTitle === index && !customTitle
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:border-border/80'
                    }`}
                    onClick={() => {
                      setSelectedTitle(index)
                      setCustomTitle('')
                    }}
                  >
                    <div className="w-6 h-6 rounded-full border-2 flex items-center justify-center">
                      {selectedTitle === index && !customTitle && (
                        <div className="w-3 h-3 rounded-full bg-primary" />
                      )}
                    </div>
                    <span className="text-sm flex-1">{title}</span>
                    <Badge variant="secondary" className="text-xs">
                      {title.length} chars
                    </Badge>
                  </div>
                ))}
                <div className="pt-2">
                  <Input
                    placeholder="Or write a custom title..."
                    value={customTitle}
                    onChange={(e) => setCustomTitle(e.target.value)}
                    maxLength={100}
                  />
                  {customTitle && (
                    <p className="text-xs text-muted-foreground mt-1">
                      {customTitle.length}/100 characters
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label>Description</Label>
              <Textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={8}
                maxLength={5000}
                placeholder="Enter video description..."
              />
              <p className="text-xs text-muted-foreground">
                {description.length}/5000 characters
              </p>
            </div>

            {/* Tags */}
            <div className="space-y-2">
              <Label>Tags</Label>
              <div className="flex flex-wrap gap-2 mb-2">
                {tags.map((tag, index) => (
                  <Badge
                    key={index}
                    variant="secondary"
                    className="cursor-pointer"
                    onClick={() => setTags(tags.filter((_, i) => i !== index))}
                  >
                    {tag} ×
                  </Badge>
                ))}
              </div>
              <Input
                placeholder="Add a tag and press Enter..."
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && e.currentTarget.value) {
                    e.preventDefault()
                    setTags([...tags, e.currentTarget.value])
                    e.currentTarget.value = ''
                  }
                }}
              />
            </div>
          </TabsContent>

          <TabsContent value="thumbnail" className="space-y-4">
            <div className="space-y-2">
              <Label>Select Thumbnail</Label>
              <div className="grid grid-cols-2 gap-4">
                {metadata?.thumbnailUrls?.map((url: string, index: number) => (
                  <div
                    key={index}
                    className={`relative aspect-video rounded-lg overflow-hidden border-2 cursor-pointer transition-all ${
                      selectedThumbnail === index
                        ? 'border-primary shadow-lg'
                        : 'border-border hover:border-border/80'
                    }`}
                    onClick={() => setSelectedThumbnail(index)}
                  >
                    <img
                      src={url}
                      alt={`Thumbnail ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                    {selectedThumbnail === index && (
                      <div className="absolute top-2 right-2 w-6 h-6 bg-primary rounded-full flex items-center justify-center">
                        <CheckCircle className="w-4 h-4 text-primary-foreground" />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="settings" className="space-y-4">
            {/* Category */}
            <div className="space-y-2">
              <Label>Category</Label>
              <Select value={categoryId} onValueChange={setCategoryId}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {categories?.map((category) => (
                    <SelectItem key={category.id} value={category.id}>
                      {category.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Privacy Status */}
            <div className="space-y-2">
              <Label>Privacy Status</Label>
              <Select value={privacyStatus} onValueChange={setPrivacyStatus}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="private">Private</SelectItem>
                  <SelectItem value="unlisted">Unlisted</SelectItem>
                  <SelectItem value="public">Public</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Schedule */}
            <div className="space-y-2">
              <Label>Schedule (Optional)</Label>
              <Input
                type="datetime-local"
                value={publishAt}
                onChange={(e) => setPublishAt(e.target.value)}
              />
              <p className="text-xs text-muted-foreground">
                Leave empty to publish immediately
              </p>
            </div>
          </TabsContent>
        </Tabs>

        <div className="mt-6 space-y-4">
          <Button
            onClick={handlePublish}
            disabled={publishVideo.isPending}
            className="w-full"
            size="lg"
          >
            {publishVideo.isPending ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Publishing to YouTube...
              </>
            ) : (
              <>
                <Upload className="w-4 h-4 mr-2" />
                Publish to YouTube
              </>
            )}
          </Button>

          {publishVideo.isSuccess && (
            <Alert>
              <CheckCircle className="w-4 h-4" />
              <AlertDescription>
                Video published successfully!{' '}
                <a
                  href={publishVideo.data?.youtubeUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-medium underline"
                >
                  View on YouTube
                  <ExternalLink className="w-3 h-3 inline ml-1" />
                </a>
              </AlertDescription>
            </Alert>
          )}

          {publishVideo.isError && (
            <Alert variant="destructive">
              <AlertCircle className="w-4 h-4" />
              <AlertDescription>
                Failed to publish video. Please try again.
              </AlertDescription>
            </Alert>
          )}
        </div>
      </CardContent>
    </Card>
  )
}