export type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost'

export const buttonVariantClasses: Record<ButtonVariant, string> = {
  primary:
    'bg-[var(--color-primary)] text-[var(--color-primary-fg)] hover:bg-[var(--color-primary-hover)] border border-transparent',
  secondary:
    'bg-transparent text-[var(--color-fg)] border border-[var(--color-border)] hover:bg-[var(--color-surface)]',
  danger: 'bg-[var(--color-danger)] text-white hover:opacity-90 border border-transparent',
  ghost: 'bg-transparent text-[var(--color-fg)] border border-transparent hover:bg-[var(--color-surface)]',
}
