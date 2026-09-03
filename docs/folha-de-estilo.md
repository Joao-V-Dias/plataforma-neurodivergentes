# Folha de Estilo — Plataforma Educacional

Sistema de design · Tipografia & Cores · Base **GitHub + Dracula**

---

## Tipografia

- **Interface e texto:** Inter — `Inter, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`
- **Código:** JetBrains Mono — `"JetBrains Mono", "Fira Code", ui-monospace, monospace`

| Estilo          | Fonte          | Peso | Tamanho | Uso                                    |
| --------------- | -------------- | ---- | ------- | -------------------------------------- |
| Display / Hero  | Inter          | 800  | 46px    | Destaque principal da home             |
| Título H1       | Inter          | 700  | 36px    | Título de página                       |
| Título H2       | Inter          | 700  | 28px    | Título de seção                        |
| Título H3       | Inter          | 600  | 22px    | Título de aula                         |
| Subtítulo H4    | Inter          | 600  | 18px    | Subtítulo de bloco                     |
| Corpo grande    | Inter          | 400  | 18px    | Introduções e textos de destaque       |
| Corpo           | Inter          | 400  | 16px    | Texto de leitura (line-height 1.6)     |
| Corpo pequeno   | Inter          | 400  | 14px    | Notas e descrições secundárias         |
| Legenda / Label | Inter          | 500  | 12px    | Rótulos, categorias, tags (uppercase)  |
| Código          | JetBrains Mono | 400  | 15px    | Trechos de código e valores técnicos   |

---

## Tema Escuro (GitHub Dark + acentos Dracula)

### Superfícies e bordas

| Nome       | Hex       | Amostra |
| ---------- | --------- | ------- |
| Fundo      | `#0D1117` | ⬛ |
| Superfície | `#161B22` | ⬛ |
| Elevado    | `#21262D` | ⬛ |
| Borda      | `#30363D` | ⬛ |

### Texto

| Nome       | Hex       | Amostra |
| ---------- | --------- | ------- |
| Texto      | `#F8F8F2` | ⬜ |
| Secundário | `#8B949E` | ◻️ |
| Comentário | `#6272A4` | 🟦 |

### Acentos (Dracula)

| Nome     | Hex       | Amostra |
| -------- | --------- | ------- |
| Roxo     | `#BD93F9` | 🟪 |
| Rosa     | `#FF79C6` | 🌸 |
| Ciano    | `#8BE9FD` | 🩵 |
| Verde    | `#50FA7B` | 🟩 |
| Laranja  | `#FFB86C` | 🟧 |
| Amarelo  | `#F1FA8C` | 🟨 |
| Vermelho | `#FF5555` | 🟥 |

---

## Tema Claro (GitHub Light)

### Superfícies e bordas

| Nome       | Hex       | Amostra |
| ---------- | --------- | ------- |
| Fundo      | `#FFFFFF` | ⬜ |
| Superfície | `#F6F8FA` | ◻️ |
| Elevado    | `#EAEEF2` | ◻️ |
| Borda      | `#D0D7DE` | ◻️ |

### Texto

| Nome       | Hex       | Amostra |
| ---------- | --------- | ------- |
| Texto      | `#1F2328` | ⬛ |
| Secundário | `#656D76` | ◼️ |
| Suave      | `#8C959F` | ◻️ |

### Acentos (GitHub Light)

| Nome     | Hex       | Amostra |
| -------- | --------- | ------- |
| Azul     | `#0969DA` | 🟦 |
| Roxo     | `#8250DF` | 🟪 |
| Verde    | `#1A7F37` | 🟩 |
| Rosa     | `#BF3989` | 🌸 |
| Amarelo  | `#9A6700` | 🟫 |
| Vermelho | `#CF222E` | 🟥 |

---

## Variáveis CSS

```css
:root {
  /* Tipografia */
  --font-sans: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --font-mono: "JetBrains Mono", "Fira Code", ui-monospace, monospace;

  --text-display: 46px;  --weight-display: 800;
  --text-h1: 36px;       --weight-h1: 700;
  --text-h2: 28px;       --weight-h2: 700;
  --text-h3: 22px;       --weight-h3: 600;
  --text-h4: 18px;       --weight-h4: 600;
  --text-body-lg: 18px;
  --text-body: 16px;
  --text-body-sm: 14px;
  --text-caption: 12px;  --weight-caption: 500;
  --text-code: 15px;
  --leading-body: 1.6;
}

/* Tema Escuro (GitHub Dark + Dracula) — padrão */
:root {
  --bg: #0D1117;
  --surface: #161B22;
  --elevated: #21262D;
  --border: #30363D;

  --text: #F8F8F2;
  --text-secondary: #8B949E;
  --text-muted: #6272A4;

  --accent: #BD93F9;   /* roxo */
  --pink: #FF79C6;
  --cyan: #8BE9FD;
  --green: #50FA7B;
  --orange: #FFB86C;
  --yellow: #F1FA8C;
  --red: #FF5555;
}

/* Tema Claro (GitHub Light) */
[data-theme="light"] {
  --bg: #FFFFFF;
  --surface: #F6F8FA;
  --elevated: #EAEEF2;
  --border: #D0D7DE;

  --text: #1F2328;
  --text-secondary: #656D76;
  --text-muted: #8C959F;

  --accent: #0969DA;   /* azul */
  --purple: #8250DF;
  --green: #1A7F37;
  --pink: #BF3989;
  --yellow: #9A6700;
  --red: #CF222E;
}
```

---

**Fontes:** Inter (rsms.me/inter) · JetBrains Mono
**Cores:** Dracula Theme + GitHub Primer
