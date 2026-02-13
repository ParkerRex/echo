'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@echo/ui/card'
import { Badge } from '@echo/ui/badge'
import { TrendingUp, TrendingDown, Minus, Info } from 'lucide-react'
import { cn } from '@echo/ui/cn'

interface MetricCardProps {
  title: string
  value: string | number
  change?: number
  changeLabel?: string
  trend?: 'up' | 'down' | 'stable'
  badge?: {
    text: string
    variant?: 'default' | 'secondary' | 'destructive' | 'outline'
  }
  description?: string
  className?: string
  icon?: React.ReactNode
}

export function MetricCard({
  title,
  value,
  change,
  changeLabel,
  trend,
  badge,
  description,
  className,
  icon
}: MetricCardProps) {
  const getTrendIcon = () => {
    if (trend === 'up') return <TrendingUp className="w-4 h-4 text-green-500" />
    if (trend === 'down') return <TrendingDown className="w-4 h-4 text-red-500" />
    return <Minus className="w-4 h-4 text-muted-foreground" />
  }

  const getTrendColor = () => {
    if (trend === 'up') return 'text-green-600'
    if (trend === 'down') return 'text-red-600'
    return 'text-muted-foreground'
  }

  return (
    <Card className={cn('relative', className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          {icon}
          {title}
          {description && (
            <Info className="w-3 h-3 text-muted-foreground" title={description} />
          )}
        </CardTitle>
        {badge && (
          <Badge variant={badge.variant || 'default'}>
            {badge.text}
          </Badge>
        )}
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <div>
            <div className="text-2xl font-bold">{value}</div>
            {(change !== undefined || changeLabel) && (
              <div className={cn('flex items-center gap-1 text-xs', getTrendColor())}>
                {trend && getTrendIcon()}
                {change !== undefined && (
                  <span>
                    {change > 0 ? '+' : ''}{change}%
                  </span>
                )}
                {changeLabel && <span>{changeLabel}</span>}
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}