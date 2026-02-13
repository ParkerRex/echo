'use client'

import { Badge } from '@echo/ui/badge'
import { CheckCircle, AlertCircle, XCircle, Clock, Zap } from 'lucide-react'
import { cn } from '@echo/ui/cn'

interface OptimizationBadgeProps {
  score: number // 0-100
  label?: string
  size?: 'sm' | 'md' | 'lg'
  showIcon?: boolean
  variant?: 'score' | 'status'
  className?: string
}

export function OptimizationBadge({
  score,
  label,
  size = 'md',
  showIcon = true,
  variant = 'score',
  className
}: OptimizationBadgeProps) {
  const normalizedScore = Math.max(0, Math.min(100, score))

  const getScoreConfig = () => {
    if (normalizedScore >= 90) {
      return {
        color: 'bg-green-100 text-green-700 border-green-200',
        icon: <CheckCircle className="w-4 h-4" />,
        text: 'Excellent'
      }
    }
    if (normalizedScore >= 70) {
      return {
        color: 'bg-blue-100 text-blue-700 border-blue-200',
        icon: <Zap className="w-4 h-4" />,
        text: 'Good'
      }
    }
    if (normalizedScore >= 50) {
      return {
        color: 'bg-yellow-100 text-yellow-700 border-yellow-200',
        icon: <Clock className="w-4 h-4" />,
        text: 'Fair'
      }
    }
    if (normalizedScore >= 30) {
      return {
        color: 'bg-orange-100 text-orange-700 border-orange-200',
        icon: <AlertCircle className="w-4 h-4" />,
        text: 'Poor'
    }
    }
    return {
      color: 'bg-red-100 text-red-700 border-red-200',
      icon: <XCircle className="w-4 h-4" />,
      text: 'Critical'
    }
  }

  const config = getScoreConfig()
  
  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-2'
  }

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4', 
    lg: 'w-5 h-5'
  }

  if (variant === 'status') {
    return (
      <Badge
        className={cn(
          'inline-flex items-center gap-1.5 border font-medium',
          config.color,
          sizeClasses[size],
          className
        )}
      >
        {showIcon && (
          <span className={iconSizes[size]}>
            {config.icon}
          </span>
        )}
        <span>{label || config.text}</span>
      </Badge>
    )
  }

  return (
    <Badge
      className={cn(
        'inline-flex items-center gap-1.5 border font-medium tabular-nums',
        config.color,
        sizeClasses[size],
        className
      )}
    >
      {showIcon && (
        <span className={iconSizes[size]}>
          {config.icon}
        </span>
      )}
      <span>{normalizedScore}%</span>
      {label && <span className="hidden sm:inline">• {label}</span>}
    </Badge>
  )
}