export type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost'

export const buttonVariantClasses: Record<ButtonVariant, string> = {
  primary: 'bg-[var(--color-primary)] text-[var(--color-primary-fg)] hover:bg-[var(--color-primary-hover)]',
  // Preenchido com --color-surface em vez de contornado: um botão com
  // borda visível ao lado de um primary sólido lê como "dois estilos
  // competindo"; um fundo suave sem borda é mais leve e ainda se
  // diferencia claramente do cartão branco por baixo.
  secondary: 'bg-[var(--color-surface)] text-[var(--color-fg)] hover:bg-[var(--color-border)]',
  danger: 'bg-[var(--color-danger)] text-white hover:opacity-90',
  ghost: 'bg-transparent text-[var(--color-fg)] hover:bg-[var(--color-surface)]',
}
