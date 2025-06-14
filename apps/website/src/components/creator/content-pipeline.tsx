// @ts-nocheck
'use client'

import { Badge } from '@echo/ui/badge'
import { Button } from '@echo/ui/button'
import { Card } from '@echo/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@echo/ui/tabs'
import { Textarea } from '@echo/ui/textarea'
import { useToast } from '@echo/ui/use-toast'
import { trpc } from '@/lib/trpc'
import {
  Check,
  Copy,
  Download,
  FileText,
  Image,
  Loader2,
  RefreshCw,
  Sparkles,
  Upload,
  Video,
} from 'lucide-react'
import { useState } from 'react'

interface ContentPipelineProps {
  ideaId: string
}

export function ContentPipeline({ ideaId }: ContentPipelineProps) {
  const [selectedTitle, setSelectedTitle] = useState<number>(0)
  const [editedContent, setEditedContent] = useState<Record<string, string>>({})
  const { toast } = useToast()

  const { data: idea } = trpc.ideas.get.useQuery({ id: ideaId })
  const { data: content, refetch: refetchContent } = trpc.content.get.useQuery(
    { ideaId },
    { enabled: !!ideaId }
  )

  const generateContent = trpc.content.generate.useMutation({
    onSuccess: () => {
      refetchContent()
      toast({
        title: 'Content generated!',
        description: 'Your content has been generated successfully.',
      })
    },
    onError: (error: unknown) => {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Unknown error',
        variant: 'destructive',
      })
    },
  })

  const updateContent = trpc.content.update.useMutation({
    onSuccess: () => {
      toast({
        title: 'Content updated',
        description: 'Your changes have been saved.',
      })
    },
  })

  const copyToClipboard = (text: string, type: string) => {
    navigator.clipboard.writeText(text)
    toast({
      title: 'Copied!',
      description: `${type} copied to clipboard`,
    })
  }

  const handleGenerateContent = () => {
    generateContent.mutate({ ideaId })
  }

  const handleSaveEdit = (field: string) => {
    if (editedContent[field] && content) {
      updateContent.mutate({
        id: content.id,
        [field]: editedContent[field],
      })
    }
  }

  if (!idea) return null

  return (
    <div className="space-y-6">
      {/* Idea Overview */}
      <Card className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-lg font-semibold mb-2">Idea Overview</h3>
            <p className="text-muted-foreground">{idea.content}</p>
            <div className="flex items-center gap-2 mt-3">
              <Badge variant="secondary">{idea.type}</Badge>
              <Badge>{idea.status}</Badge>
            </div>
          </div>
          {!content && (
            <Button onClick={handleGenerateContent} disabled={generateContent.isPending}>
              {generateContent.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4 mr-2" />
                  Generate Content
                </>
              )}
            </Button>
          )}
        </div>
      </Card>

      {content && (
        <Tabs defaultValue="titles" className="space-y-4">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="titles">Titles</TabsTrigger>
            <TabsTrigger value="script">Script</TabsTrigger>
            <TabsTrigger value="description">Description</TabsTrigger>
            <TabsTrigger value="thumbnail">Thumbnail</TabsTrigger>
          </TabsList>

          {/* Titles Tab */}
          <TabsContent value="titles">
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Generated Titles</h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => generateContent.mutate({ ideaId, regenerate: 'titles' })}
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Regenerate
                </Button>
              </div>
              <div className="space-y-3">
                {content.titles?.map((title: string, index: number) => (
                  <div
                    key={index}
                    className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                      selectedTitle === index
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:bg-accent'
                    }`}
                    onClick={() => setSelectedTitle(index)}
                  >
                    <div className="flex items-start justify-between">
                      <p className="flex-1">{title}</p>
                      <div className="flex gap-2 ml-4">
                        {selectedTitle === index && <Check className="h-4 w-4 text-primary" />}
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={(e: React.MouseEvent) => {
                            e.stopPropagation()
                            copyToClipboard(title, 'Title')
                          }}
                        >
                          <Copy className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </TabsContent>

          {/* Script Tab */}
          <TabsContent value="script">
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Video Script</h3>
                <div className="flex gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => copyToClipboard(content.script || '', 'Script')}
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    Copy
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => generateContent.mutate({ ideaId, regenerate: 'script' })}
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Regenerate
                  </Button>
                </div>
              </div>
              <Textarea
                value={editedContent.script || content.script || ''}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                  setEditedContent({ ...editedContent, script: e.target.value })
                }
                className="min-h-[400px] font-mono text-sm"
                placeholder="Your video script will appear here..."
              />
              {editedContent.script && editedContent.script !== content.script && (
                <Button onClick={() => handleSaveEdit('script')} className="mt-4" size="sm">
                  Save Changes
                </Button>
              )}
            </Card>
          </TabsContent>

          {/* Description Tab */}
          <TabsContent value="description">
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Video Description</h3>
                <div className="flex gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => copyToClipboard(content.description || '', 'Description')}
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    Copy
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => generateContent.mutate({ ideaId, regenerate: 'description' })}
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Regenerate
                  </Button>
                </div>
              </div>
              <Textarea
                value={editedContent.description || content.description || ''}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                  setEditedContent({ ...editedContent, description: e.target.value })
                }
                className="min-h-[300px]"
                placeholder="Your video description will appear here..."
              />
              {editedContent.description && editedContent.description !== content.description && (
                <Button onClick={() => handleSaveEdit('description')} className="mt-4" size="sm">
                  Save Changes
                </Button>
              )}
              {content.tags && content.tags.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-medium mb-2">Tags</h4>
                  <div className="flex flex-wrap gap-2">
                    {content.tags.map((tag: string, index: number) => (
                      <Badge key={index} variant="secondary">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </Card>
          </TabsContent>

          {/* Thumbnail Tab */}
          <TabsContent value="thumbnail">
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Thumbnail Ideas</h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => generateContent.mutate({ ideaId, regenerate: 'thumbnail' })}
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Regenerate
                </Button>
              </div>
              <div className="grid grid-cols-2 gap-4">
                {content.thumbnailUrls?.map((url: string, index: number) => (
                  <div
                    key={index}
                    className="relative aspect-video rounded-lg overflow-hidden bg-muted"
                  >
                    <img
                      src={url}
                      alt={`Thumbnail ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute bottom-2 right-2 flex gap-2">
                      <Button
                        size="icon"
                        variant="secondary"
                        className="h-8 w-8"
                        onClick={() => {
                          // TODO: Implement download
                          toast({
                            title: 'Coming soon',
                            description: 'Download functionality will be available soon',
                          })
                        }}
                      >
                        <Download className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
              {content.thumbnailPrompts && (
                <div className="mt-4">
                  <h4 className="text-sm font-medium mb-2">Thumbnail Prompts</h4>
                  <div className="space-y-2">
                    {content.thumbnailPrompts.map((prompt: string, index: number) => (
                      <p key={index} className="text-sm text-muted-foreground">
                        {index + 1}. {prompt}
                      </p>
                    ))}
                  </div>
                </div>
              )}
            </Card>
          </TabsContent>
        </Tabs>
      )}

      {/* Action Bar */}
      {content && (
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Badge variant="outline" className="text-sm">
                Selected: {content.titles?.[selectedTitle]}
              </Badge>
            </div>
            <Button>
              <Upload className="h-4 w-4 mr-2" />
              Upload to YouTube
            </Button>
          </div>
        </Card>
      )}
    </div>
  )
}
