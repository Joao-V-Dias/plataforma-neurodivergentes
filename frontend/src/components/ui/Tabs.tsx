import * as TabsPrimitive from '@radix-ui/react-tabs'
import { cn } from '@/lib/cn'

// eslint-disable-next-line react-refresh/only-export-components -- re-export de componente estável do Radix, não afeta fast refresh na prática
export const Tabs = TabsPrimitive.Root

export function TabsList(props: TabsPrimitive.TabsListProps) {
  return (
    <TabsPrimitive.List
      {...props}
      className={cn(
        'inline-flex gap-1 rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] p-1',
        props.className,
      )}
    />
  )
}

export function TabsTrigger(props: TabsPrimitive.TabsTriggerProps) {
  return (
    <TabsPrimitive.Trigger
      {...props}
      className={cn(
        'rounded px-3 py-1.5 text-sm font-medium text-[var(--color-muted)] transition-colors',
        'data-[state=active]:bg-[var(--color-bg)] data-[state=active]:text-[var(--color-fg)] data-[state=active]:shadow-sm',
        props.className,
      )}
    />
  )
}

export function TabsContent(props: TabsPrimitive.TabsContentProps) {
  return <TabsPrimitive.Content {...props} className={cn('mt-4', props.className)} />
}
