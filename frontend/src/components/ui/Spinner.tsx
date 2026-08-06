import { cn } from '@/lib/cn'

const sizeClasses = {
  sm: 'h-4 w-4 border-2',
  md: 'h-6 w-6 border-2',
  lg: 'h-10 w-10 border-[3px]',
}

export function Spinner({ size = 'md', className }: { size?: keyof typeof sizeClasses; className?: string }) {
  return (
    <span
      role="status"
      aria-label="Carregando"
      className={cn(
        'inline-block animate-spin rounded-full border-current border-t-transparent',
        sizeClasses[size],
        className,
      )}
    />
  )
}

export function PageSpinner({ label = 'Carregando...' }: { label?: string }) {
  return (
    <div className="flex min-h-[40vh] flex-col items-center justify-center gap-3 text-[var(--color-muted)]">
      <Spinner size="lg" />
      <p>{label}</p>
    </div>
  )
}
