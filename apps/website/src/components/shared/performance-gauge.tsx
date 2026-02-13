'use client'

import { cn } from '@echo/ui/cn'

interface PerformanceGaugeProps {
  value: number // 0-100
  label: string
  size?: 'sm' | 'md' | 'lg'
  showValue?: boolean
  color?: 'default' | 'success' | 'warning' | 'danger'
  className?: string
}

export function PerformanceGauge({
  value,
  label,
  size = 'md',
  showValue = true,
  color = 'default',
  className
}: PerformanceGaugeProps) {
  const normalizedValue = Math.max(0, Math.min(100, value))
  const strokeDasharray = 2 * Math.PI * 45 // radius = 45
  const strokeDashoffset = strokeDasharray - (strokeDasharray * normalizedValue) / 100

  const sizeClasses = {
    sm: 'w-16 h-16',
    md: 'w-24 h-24', 
    lg: 'w-32 h-32'
  }

  const textSizes = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base'
  }

  const getColor = () => {
    if (color !== 'default') {
      return {
        success: 'stroke-green-500',
        warning: 'stroke-yellow-500',
        danger: 'stroke-red-500'
      }[color]
    }

    // Auto color based on value
    if (normalizedValue >= 80) return 'stroke-green-500'
    if (normalizedValue >= 60) return 'stroke-blue-500'
    if (normalizedValue >= 40) return 'stroke-yellow-500'
    return 'stroke-red-500'
  }

  return (
    <div className={cn('flex flex-col items-center gap-2', className)}>
      <div className={cn('relative', sizeClasses[size])}>
        <svg
          className="transform -rotate-90 w-full h-full"
          viewBox="0 0 100 100"
        >
          {/* Background circle */}
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            className="text-muted-foreground/20"
          />
          {/* Progress circle */}
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            className={cn('transition-all duration-500 ease-out', getColor())}
          />
        </svg>
        {showValue && (
          <div className="absolute inset-0 flex items-center justify-center">
            <span className={cn('font-semibold', textSizes[size])}>
              {Math.round(normalizedValue)}%
            </span>
          </div>
        )}
      </div>
      <span className={cn('text-center font-medium', textSizes[size])}>
        {label}
      </span>
    </div>
  )
}