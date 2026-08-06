import type { ReactElement, ReactNode } from 'react'
import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/lib/auth/AuthContext'
import { ToastProvider } from '@/components/ui/Toast'

export function renderWithProviders(
  ui: ReactElement,
  { route = '/', wrapper: ExtraWrapper }: { route?: string; wrapper?: ({ children }: { children: ReactNode }) => ReactElement } = {},
) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })

  function Wrapper({ children }: { children: ReactNode }) {
    const content = (
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={[route]}>
          <AuthProvider>
            <ToastProvider>{children}</ToastProvider>
          </AuthProvider>
        </MemoryRouter>
      </QueryClientProvider>
    )
    return ExtraWrapper ? <ExtraWrapper>{content}</ExtraWrapper> : content
  }

  return render(ui, { wrapper: Wrapper })
}
