'use client'

import { Badge } from '@echo/ui/badge'
import { Button } from '@echo/ui/button'
import { Copy, TrendingUp, TrendingDown, Minus, X } from 'lucide-react'
import { cn } from '@echo/ui/cn'
import { useState } from 'react'

interface KeywordPillProps {
  keyword: string
  searchVolume?: number
  competition?: 'low' | 'medium' | 'high'
  trend?: 'rising' | 'stable' | 'declining'
  difficulty?: number
  onRemove?: () => void
  onClick?: () => void
  copyable?: boolean
  removable?: boolean
  className?: string
}

export function KeywordPill({
  keyword,
  searchVolume,
  competition,
  trend,
  difficulty,
  onRemove,
  onClick,
  copyable = false,
  removable = false,
  className
}: KeywordPillProps) {
  const [copied, setCopied] = useState(false)

  const getCompetitionColor = () => {
    switch (competition) {
      case 'low': return 'bg-green-100 text-green-700 border-green-200'
      case 'medium': return 'bg-yellow-100 text-yellow-700 border-yellow-200'
      case 'high': return 'bg-red-100 text-red-700 border-red-200'
      default: return 'bg-secondary text-secondary-foreground'
    }
  }

  const getTrendIcon = () => {
    switch (trend) {
      case 'rising': return <TrendingUp className="w-3 h-3 text-green-500" />
      case 'declining': return <TrendingDown className="w-3 h-3 text-red-500" />
      default: return <Minus className="w-3 h-3 text-muted-foreground" />
    }
  }

  const handleCopy = async (e: React.MouseEvent) => {
    e.stopPropagation()
    await navigator.clipboard.writeText(keyword)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleRemove = (e: React.MouseEvent) => {
    e.stopPropagation()
    onRemove?.()
  }

  return (
    <div
      className={cn(
        'inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-sm font-medium transition-colors',
        onClick ? 'cursor-pointer hover:bg-secondary/80' : '',
        getCompetitionColor(),
        className
      )}
      onClick={onClick}
    >
      <div className="flex items-center gap-1.5">
        <span>{keyword}</span>
        {trend && getTrendIcon()}
      </div>

      {/* Metadata */}
      <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
        {searchVolume !== undefined && (
          <span title="Search Volume">
            {searchVolume > 1000 ? `${Math.round(searchVolume / 1000)}k` : searchVolume}
          </span>
        )}
        
        {difficulty !== undefined && (
          <Badge variant="outline" className="text-xs px-1 py-0">
            {difficulty}%
          </Badge>
        )}
      </div>

      {/* Actions */}
      <div className="flex items-center gap-1">
        {copyable && (
          <Button
            size="sm"
            variant="ghost"
            className="h-auto w-auto p-1 hover:bg-background/50"
            onClick={handleCopy}
            title="Copy keyword"
          >
            {copied ? (
              <span className="text-green-500 text-xs">✓</span>
            ) : (
              <Copy className="w-3 h-3" />
            )}
          </Button>
        )}
        
        {removable && (
          <Button
            size="sm"
            variant="ghost"
            className="h-auto w-auto p-1 hover:bg-red-100 hover:text-red-600"
            onClick={handleRemove}
            title="Remove keyword"
          >
            <X className="w-3 h-3" />
          </Button>
        )}
      </div>
    </div>
  )
}