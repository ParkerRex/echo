// @ts-nocheck
'use client'

import { Badge } from '@echo/ui/badge'
import { Card } from '@echo/ui/card'
import { ScrollArea } from '@echo/ui/scroll-area'
import { trpc } from '@/lib/trpc'
import { cn } from '@/lib/utils'
import { formatDistanceToNow } from 'date-fns'
import { Clock, FileText, Link, Mic } from 'lucide-react'

interface IdeaListProps {
  selectedId: string | null
  onSelect: (id: string) => void
}

export function IdeaList({ selectedId, onSelect }: IdeaListProps) {
  const { data: ideas, isLoading } = trpc.ideas.list.useQuery({
    limit: 20,
  })

  const getIcon = (type: string) => {
    switch (type) {
      case 'transcript':
        return <FileText className="h-4 w-4" />
      case 'url':
        return <Link className="h-4 w-4" />
      case 'voice':
        return <Mic className="h-4 w-4" />
      default:
        return <FileText className="h-4 w-4" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready':
        return 'bg-green-500'
      case 'scripting':
      case 'outlining':
        return 'bg-yellow-500'
      case 'published':
        return 'bg-blue-500'
      case 'archived':
        return 'bg-gray-500'
      default:
        return 'bg-gray-400'
    }
  }

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-muted animate-pulse rounded" />
          ))}
        </div>
      </Card>
    )
  }

  return (
    <Card className="p-4">
      <h3 className="font-semibold mb-3">Recent Ideas</h3>
      <ScrollArea className="h-[400px]">
        <div className="space-y-2">
          {ideas?.map((idea: any) => (
            <button
              key={idea.id}
              onClick={() => onSelect(idea.id)}
              className={cn(
                'w-full text-left p-3 rounded-lg transition-colors',
                'hover:bg-accent',
                selectedId === idea.id && 'bg-accent'
              )}
            >
              <div className="flex items-start gap-3">
                <div className="mt-1 text-muted-foreground">{getIcon(idea.type)}</div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium line-clamp-2">{idea.content}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <div className={`w-2 h-2 rounded-full ${getStatusColor(idea.status)}`} />
                    <span className="text-xs text-muted-foreground">{idea.status}</span>
                    <span className="text-xs text-muted-foreground">•</span>
                    <span className="text-xs text-muted-foreground flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {formatDistanceToNow(new Date(idea.createdAt), { addSuffix: true })}
                    </span>
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>
      </ScrollArea>
    </Card>
  )
}
