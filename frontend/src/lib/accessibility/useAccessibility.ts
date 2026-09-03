import { useContext } from 'react'
import { AccessibilityContext } from './AccessibilityContext'

export function useAccessibility() {
  const ctx = useContext(AccessibilityContext)
  if (!ctx) throw new Error('useAccessibility precisa estar dentro de <AccessibilityProvider>.')
  return ctx
}
