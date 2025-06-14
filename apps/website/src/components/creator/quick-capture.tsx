// @ts-nocheck
'use client'

import { Button } from '@echo/ui/button'
import { Card } from '@echo/ui/card'
import { Textarea } from '@echo/ui/textarea'
import { useToast } from '@/hooks/use-toast'
import { trpc } from '@/lib/trpc'
import { Clipboard, Loader2, Mic, Sparkles } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'

interface QuickCaptureProps {
  onIdeaCaptured: (ideaId: string) => void
}

export function QuickCapture({ onIdeaCaptured }: QuickCaptureProps) {
  const [input, setInput] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [detectedType, setDetectedType] = useState<'idea' | 'transcript' | 'url'>('idea')
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const { toast } = useToast()

  const createIdea = trpc.ideas.create.useMutation({
    onSuccess: (data: any) => {
      setInput('')
      onIdeaCaptured(data.id)
      toast({
        title: 'Idea captured!',
        description: 'Your idea has been saved and is ready for processing.',
      })
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive',
      })
    },
  })

  // Detect content type
  useEffect(() => {
    const content = input.trim()
    if (content.startsWith('http://') || content.startsWith('https://')) {
      setDetectedType('url')
    } else if (content.length > 500 && content.includes(' ')) {
      setDetectedType('transcript')
    } else {
      setDetectedType('idea')
    }
  }, [input])

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Enter' && e.metaKey && textareaRef.current === document.activeElement) {
        e.preventDefault()
        handleSubmit()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [input])

  const handleSubmit = () => {
    if (!input.trim()) return

    createIdea.mutate({
      content: input.trim(),
      type: detectedType,
      source: 'manual',
    })
  }

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText()
      setInput(text)
      textareaRef.current?.focus()
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to read from clipboard',
        variant: 'destructive',
      })
    }
  }

  const handleVoiceRecord = () => {
    // TODO: Implement voice recording
    toast({
      title: 'Coming soon',
      description: 'Voice recording will be available in the next update',
    })
  }

  const getPlaceholder = () => {
    switch (detectedType) {
      case 'url':
        return "Detected: URL - We'll analyze this video for insights"
      case 'transcript':
        return "Detected: Transcript - We'll generate content from this"
      default:
        return 'Type your video idea, paste a transcript, or drop a YouTube URL...'
    }
  }

  return (
    <Card className="p-6">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Quick Capture</h2>
          <div className="flex gap-2">
            <Button variant="ghost" size="icon" onClick={handlePaste} title="Paste from clipboard">
              <Clipboard className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" onClick={handleVoiceRecord} title="Voice record">
              <Mic className={`h-4 w-4 ${isRecording ? 'text-red-500' : ''}`} />
            </Button>
          </div>
        </div>

        <Textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={getPlaceholder()}
          className="min-h-[120px] resize-none"
          autoFocus
        />

        <div className="flex items-center justify-between">
          <p className="text-xs text-muted-foreground">Press ⌘+Enter to capture</p>
          <Button onClick={handleSubmit} disabled={!input.trim() || createIdea.isPending} size="sm">
            {createIdea.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <>
                <Sparkles className="h-4 w-4 mr-2" />
                Capture
              </>
            )}
          </Button>
        </div>
      </div>
    </Card>
  )
}
