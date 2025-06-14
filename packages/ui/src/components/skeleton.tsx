import type * as React from 'react'
import { cn } from '../utils'

function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'relative overflow-hidden',
        'bg-gradient-to-r from-transparent via-secondary to-transparent',
        'bg-[length:200%_100%]',
        'animate-shimmer rounded-lg',
        className
      )}
      {...props}
    />
  )
}

export { Skeleton }
