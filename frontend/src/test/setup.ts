import '@testing-library/jest-dom/vitest'

// jsdom não implementa matchMedia nem ResizeObserver, usados por
// primitivas do Radix UI (Select/Dialog) para posicionamento - sem esses
// stubs, qualquer teste que monte esses componentes lança em runtime.
if (!window.matchMedia) {
  window.matchMedia = (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  })
}

class StubResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}
// eslint-disable-next-line @typescript-eslint/no-explicit-any
;(globalThis as any).ResizeObserver ??= StubResizeObserver
