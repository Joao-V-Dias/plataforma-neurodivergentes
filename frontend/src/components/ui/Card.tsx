import type { HTMLAttributes } from 'react'
import { cn } from '@/lib/cn'
import './Card.css'

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div data-card className={cn('card', className)} {...props} />
}
