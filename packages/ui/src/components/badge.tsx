import { type VariantProps, cva } from 'class-variance-authority'
import type * as React from 'react'
import { cn } from '../utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-lg px-2.5 py-0.5 text-xs font-medium transition-all duration-200',
  {
    variants: {
      variant: {
        default: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        secondary: 'bg-muted text-muted-foreground hover:bg-muted/80',
        outline: 'border border-border text-foreground hover:bg-secondary/50',
        ghost: 'text-muted-foreground hover:bg-secondary hover:text-foreground',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />
}

export { Badge, badgeVariants }
