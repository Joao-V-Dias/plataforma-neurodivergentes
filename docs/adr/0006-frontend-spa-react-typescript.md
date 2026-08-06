# 0006 — Frontend SPA em React + TypeScript

**Status:** Aceito (Parte 7)

## Contexto

A Parte 7 original definia um frontend acessível, com meta de Lighthouse
Accessibility Score > 90 — o restante do texto do escopo não estava mais
disponível no momento da implementação (só esse fragmento sobre
acessibilidade). A decisão de arquitetura seguiu o padrão do resto do
projeto (backend das Partes 1–6) como fonte de verdade para as telas.

## Decisão

SPA client-side puro (`frontend/`): React 19 + TypeScript + Vite,
TanStack Query para estado de servidor, React Router, React Hook Form +
Zod, Radix UI (primitivas acessíveis por padrão: foco gerenciado, ARIA
correto) + Tailwind CSS v4, CodeMirror 6 para o editor de código.

Sem SSR/framework full-stack (Next.js etc.) — a API já existe e é
completa, o frontend só precisa consumi-la. Autenticação via
access+refresh token em `localStorage`, com rotação automática de
refresh no cliente (trade-off documentado em
`frontend/src/lib/api/tokenStorage.ts`: XSS pode roubar o token, mas não
há backend-for-frontend para usar cookie httpOnly, e a rotação com
detecção de reuso do lado do servidor mitiga o dano de um token roubado).

## Consequências

- **Positivo:** cliente de API totalmente tipado (`frontend/src/lib/api/types.ts`)
  espelhando os schemas Pydantic do backend — qualquer mudança de
  contrato quebra a build do frontend em vez de falhar silenciosamente
  em runtime.
- **Positivo:** acessibilidade tratada como estado de aplicação, não só
  CSS — `AccessibilityProvider` lê as preferências do usuário
  (`PreferenciasAcessibilidade`, Parte 3) e aplica globalmente (alto
  contraste, tamanho de fonte, redução de estímulos, leitura em voz
  alta), com padrões de contraste testados manualmente em ambos os
  temas.
- **Negativo:** sem o texto completo original da Parte 7, é possível que
  algum requisito específico do escopo não tenha sido coberto — vale
  revisar contra o documento original se ele for recuperado.
- **Negativo:** `localStorage` para tokens é um trade-off de segurança
  conhecido (ver acima) — endereçável no futuro com um backend-for-
  frontend que sete cookies httpOnly, se o risco de XSS justificar o
  investimento.
