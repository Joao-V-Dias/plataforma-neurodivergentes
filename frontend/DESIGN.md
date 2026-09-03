---
name: Plataforma Adaptativa
description: Estação de Leitura — a monitoring-instrument console for a neurodivergent-first programming-education platform.
colors:
  signal-cyan: "#17708f"
  signal-cyan-fg: "#f2f7f8"
  critical-red: "#a8362a"
  reading-green: "#1c744a"
  attention-amber: "#96590a"
  decorative-pink: "#8a4a7e"
  decorative-cyan: "#2d5f8c"
  decorative-orange: "#b0530f"
  decorative-yellow: "#8a7a12"
  bg: "#eef1f3"
  surface: "#e2e7ea"
  elevated: "#d3dade"
  border: "#7c93a0"
  border-muted: "#b7c3c9"
  ink: "#131f26"
  ink-secondary: "#435661"
  ink-muted: "#56636b"
typography:
  display:
    fontFamily: "IBM Plex Sans, Atkinson Hyperlegible, system-ui, sans-serif"
    fontSize: "2.875rem"
    fontWeight: 700
    lineHeight: 1.2
  headline:
    fontFamily: "IBM Plex Sans, Atkinson Hyperlegible, system-ui, sans-serif"
    fontSize: "1.75rem"
    fontWeight: 700
  body:
    fontFamily: "Atkinson Hyperlegible, system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "JetBrains Mono, JetBrains Mono Local, Fira Code, ui-monospace, monospace"
    fontSize: "0.75rem"
    fontWeight: 600
    letterSpacing: "0.04em"
  readout:
    fontFamily: "JetBrains Mono, JetBrains Mono Local, Fira Code, ui-monospace, monospace"
    fontSize: "0.9375rem"
    fontWeight: 500
rounded:
  sm: "4px"
  md: "6px"
  lg: "8px"
  full: "999px"
spacing:
  1: "0.25rem"
  2: "0.5rem"
  3: "0.75rem"
  4: "1rem"
  5: "1.5rem"
  6: "2rem"
  7: "2.5rem"
  8: "3rem"
components:
  badge-sucesso:
    backgroundColor: "color-mix(in srgb, {colors.reading-green} 14%, {colors.surface})"
    textColor: "{colors.reading-green}"
    rounded: "{rounded.sm}"
    padding: "0.2rem 0.55rem 0.2rem 0.45rem"
  badge-erro:
    backgroundColor: "color-mix(in srgb, {colors.critical-red} 14%, {colors.surface})"
    textColor: "{colors.critical-red}"
    rounded: "{rounded.sm}"
    padding: "0.2rem 0.55rem 0.2rem 0.45rem"
  badge-aviso:
    backgroundColor: "color-mix(in srgb, {colors.attention-amber} 14%, {colors.surface})"
    textColor: "{colors.attention-amber}"
    rounded: "{rounded.sm}"
    padding: "0.2rem 0.55rem 0.2rem 0.45rem"
  badge-info:
    backgroundColor: "color-mix(in srgb, {colors.signal-cyan} 14%, {colors.surface})"
    textColor: "{colors.signal-cyan}"
    rounded: "{rounded.sm}"
    padding: "0.2rem 0.55rem 0.2rem 0.45rem"
  station-row:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    padding: "0.75rem 1.5rem"
  avatar-dial:
    backgroundColor: "{colors.elevated}"
    textColor: "{colors.ink-secondary}"
    rounded: "{rounded.full}"
---

# Design System: Plataforma Adaptativa

## Overview

**Creative North Star: "Estação de Leitura" (Reading Station)**

This is a monitoring-instrument console — the visual grammar of an INMET-style weather/telemetry station adapted to a programming-education product for neurodivergent students. Progress is rendered as a personal reading a student checks on their own instrument panel, never a rank against classmates: LEDs, gauge-chips, tabular readouts, and banded intensity meters stand in for cards and rank badges. The world is dark-first in spirit (the console reads best under panel light) but ships as two fully complete, independently normative themes — light is the actual runtime default — plus an independent pure-black/white high-contrast layer switched by a stored accessibility preference, not a design toggle.

The console vocabulary is deliberately restrained: hairline 1px bezels carry all hierarchy, there is no shadow anywhere, radii stay small and consistent, and color is functional rather than decorative — reserved almost entirely for status (an active reading, a critical error, a streak) rather than for branding or mood. This restraint is a direct answer to the product's own audience: ADHD/autism/dyslexia/dyscalculia students need a low-stimulation, literal, predictable surface, and PRODUCT.md's principle that game framing must never read as childish or turn into scoreboard pressure. The build explicitly rejects the prior "Working Notebook" world (read as childish) and generic pastel ed-tech.

**Key Characteristics:**
- Instrument-panel realism: LEDs, gauge-chip readouts, banded meters, tabular mono figures — never illustrative or playful iconography
- Two complete parallel themes (light default, dark) plus an independent high-contrast layer, never a lightened/darkened derivative of the other
- Color is scarce and operational: one signal cyan, one amber, one red, one green — each with exactly one reserved job
- Flat by construction: no shadow exists anywhere in the built surfaces; hairline borders do all the work
- Body copy is always achromatic; color appears only on the specific element carrying the live status

## Colors

The palette is a restrained operational instrument palette: a near-black/near-white achromatic scale for structure and text, four reserved status hues used nowhere else, and a separate decorative set confined to identity/cosmetic roles.

### Primary
- **Signal Cyan** (`#17708f` light / `#3fb0d4` dark): the single operational accent — active reading value, primary links, focus ring, primary action, hover-state emphasis on interactive rows. This is the only color legitimately usable for "primary."

### Neutral
- **Panel Background** (`--bg`, `#eef1f3` light / `#0c1922` dark): page background.
- **Surface** (`--surface`, `#e2e7ea` light / `#12222d` dark): station rows, panel backgrounds, header chips.
- **Elevated** (`--elevated`, `#d3dade` light / `#1a2f3c` dark): hover state, active nav tab background, avatar dial fill.
- **Border** (`--border`, `#7c93a0` light / `#3a5563` dark): structural hairlines — panel edges, header rules, LED-strip frames.
- **Border Muted** (`--border-muted`, `#b7c3c9` light / `#223541` dark): secondary dividers between rows.
- **Ink** (`--text`, `#131f26` light / `#e8eef1` dark): primary text.
- **Ink Secondary** (`--text-secondary`, `#435661` light / `#9fb2bc` dark): station metadata (period, identity labels).
- **Ink Muted** (`--text-muted`, `#56636b` light / `#7995a1` dark): captions, inactive status labels, timestamps.

### Named Rules
**The Signal Reserve Rule.** Exactly four operational hues exist, each with exactly one job, everywhere in the product: signal cyan (`--accent`) for active reading/link/focus/primary action; reading green (`--green`, `#1c744a` light / `#52d190` dark) for success/approved/active-station state; attention amber (`--amber`, `#96590a` light / `#f0ab4a` dark) for streak/attention only, never error; critical red (`--red`, `#a8362a` light / `#ef6355` dark) for error/critical/destructive only. A parallel decorative-identity set — pink (`#8a4a7e`/`#c98fc0`), cyan (`#2d5f8c`/`#6fa8d1`), orange (`#b0530f`/`#e2894a`), yellow (`#8a7a12`/`#d6c25a`) — exists purely for cosmetic variety (avatar hues, nav-tab identity ink) and must never carry status meaning. This distinction was a finish-review correction this round (tab identity and streak/points icons initially misused reserved status hues) and is the load-bearing rule of the palette.

**The Plain-Name Rule.** Color never speaks alone. Every LED, badge, and status band ships with a literal text label (`em curso`/`encerrada`, badge text) alongside the color, satisfying WCAG 1.4.1 and the product's colorblind-safe requirement.

**The Achromatic Body Rule.** Body text and structural chrome (borders, backgrounds, secondary/muted text) stay strictly achromatic. Color is confined to the specific element carrying the active status — an LED, a badge, a reading value, a station name on hover — never applied as an ambient tint across a row or panel.

## Typography

**Display/Headline Font:** IBM Plex Sans (with Atkinson Hyperlegible, system-ui fallback)
**Body Font:** Atkinson Hyperlegible (with system-ui, -apple-system, Segoe UI, Roboto fallback)
**Label/Mono Font:** JetBrains Mono (with JetBrains Mono Local, Fira Code, ui-monospace fallback)

**Character:** A technical, humanist pairing. Atkinson Hyperlegible is an accessibility-mandated body face (British Dyslexia Association-aligned, non-negotiable per PRODUCT.md) that keeps prose legible under dyslexia/low-vision conditions; IBM Plex Sans gives headings a technical, instrument-panel authority without going cold; JetBrains Mono renders every tabular or state-bearing value (dates, readouts, station numbers, status labels, code) with fixed-width precision.

### Hierarchy
- **Display** (700, 2.875rem / `--text-display`): reserved for the largest page-level moments; not heavily used on the anchor surface itself.
- **Headline** (700, 1.75rem / `--text-h2`, IBM Plex Sans): page titles (e.g. "Minhas turmas").
- **Title** (600, 1.125–1.125rem / `--text-h4`, IBM Plex Sans): station/card names, section titles.
- **Body** (400, 1rem / `--text-body`, Atkinson Hyperlegible, line-height 1.6): all prose and descriptive copy.
- **Label** (600, 0.75rem / `--text-caption`, JetBrains Mono, uppercase, 0.04–0.05em tracking): column headers, status labels, badges.
- **Readout** (500–700, 0.875–0.9375rem / `--text-body-sm`–`--text-code`, JetBrains Mono, tabular-nums): dates, station numbers, streak/points counters, periods — any value read like an instrument.

### Named Rules
**The Tabular Readout Rule.** Any value that represents a live count, date, period, or sequential number renders in JetBrains Mono with `font-variant-numeric: tabular-nums`, never in the body sans. This is what makes the console read as an instrument rather than a document.

## Layout

The anchor surface (`MinhasTurmasPage`) fills its content width edge-to-edge with no floating narrow column — a dense instrument panel, not a card grid. Spacing follows an 8-step rem scale (`--space-1` 0.25rem through `--space-8` 3rem). The aluno shell is a fixed 6rem instrument rail on the left (icon + label per tab, sticky, full viewport height) plus a flexible body with a sticky 3.5rem header. The gestão (staff) shell instead uses a 15.5rem sidebar in a two-column CSS grid. Both shells collapse to a horizontal, scrollable top bar under 720px (aluno) / 900px (gestão). The station list itself is a CSS grid (`5rem minmax(0,1fr) 9rem 8.5rem 4.5rem` desktop) that collapses to a 3-column/2-row grid-template-areas layout on mobile, dropping the column header row entirely rather than truncating it.

## Elevation & Depth

Flat by construction — there is no `box-shadow` anywhere in the rebuilt surfaces (index.css, AlunoShell, GestaoShell, MinhasTurmasPage, Badge, Avatar, FotoOuAvatar, ResultadoCasoCard all confirmed shadow-free). Depth and hierarchy are conveyed entirely through hairline 1px borders (`--border` / `--border-muted`) and background-tone steps across three layers: `--bg` (page) → `--surface` (panels, rows, chips) → `--elevated` (hover state, active tab, avatar fill). There is no ambient glow or lifted-card metaphor anywhere in this world.

### Named Rules
**The Flat Instrument Rule.** Surfaces never lift or cast shadow, at rest or on hover. State changes communicate through background-tone stepping (`surface` → `elevated`) and border/color shifts only.

## Shapes

Radius is small and deliberately consistent: `--radius-sm` (4px) for compact chips/tabs/badges, `--radius` (6px) for standard containers and buttons, `--radius-lg` (8px) for the outer station panel. Nothing in the system is sharp/0px, and nothing is pill-shaped except genuinely circular instrument parts — avatar/photo dials, status LEDs, gauge markers, active-tab dots — which use 999px. Borders are 1–1.5px hairlines throughout; there is no double-border or inset-ring treatment.

### Named Rules
**The Round-Only-If-Real Rule.** Full-pill radius (999px) is reserved for parts that are genuinely circular instrument components (LED, avatar dial, gauge dot). Rectangular containers — panels, badges, buttons, inputs — stay within the 4–8px radius steps and never approach pill shape.

## Components

### Buttons
Buttons are not present in the rebuilt anchor surfaces sampled this pass (no button variant was restructured); inherited chrome (border, radius, focus ring) follows the shared token system per the global rules above.

### Badges
- **Shape:** `--radius-sm` (4px), 1px border.
- **Style:** an LED-dot (a `::before` pseudo-element, `currentColor`, 0.4rem circle) plus an uppercase JetBrains Mono label — never color-only. Background is a 14% tint of the status color mixed into `--surface`; border is a 35% tint of the same color. Variants: `--sucesso` (green), `--erro` (red), `--aviso` (amber), `--info`/`--accent` (cyan), `--neutro` (achromatic).
- **State:** static; no hover/press state observed (informational, not interactive).

### Avatars
- **Shape:** genuinely circular (999px), 1.5px border, `--elevated` fill — a "dial" reading, matching `FotoOuAvatar`'s photo-crop variant exactly.
- **Color:** identity color drawn only from the decorative set (orange, accent, pink, cyan, yellow, or muted achromatic) — never a status hue.

### Cards / Containers
- **Corner Style:** `--radius` (6px) for small containers (`resultado-caso`, note banners), `--radius-lg` (8px) for the outer station panel.
- **Background:** `--surface`.
- **Shadow Strategy:** none (see Elevation & Depth).
- **Border:** 1px `--border`; status-carrying containers (e.g. `ResultadoCasoCard`) tint the border itself toward green/red via `color-mix` rather than adding a shadow, background wash, or side-stripe.
- **Internal Padding:** `--space-3` `--space-4` typical.

### Navigation
- **Aluno instrument rail:** fixed 6rem vertical rail, icon-over-label tabs, sticky full-height. The active tab lights an LED bar on the rail's left edge plus a small corner dot, using a per-tab decorative identity color (`--tab-ink`) — Turmas uses accent cyan, Agenda uses decorative pink, Batalha uses decorative cyan. Hover shifts background to `--elevated` and text to `--text`; never a color change on hover, only on active.
- **Gestão sidebar:** 15.5rem fixed sidebar, left-edge accent bar (accent cyan only, no per-item identity color) on the active link, `--elevated` background on hover/active.
- **Header gauge-chips:** streak and points render as small mono-readout chips (`--surface` background, `--border-muted` border) with an amber icon — the two sanctioned uses of reserved amber (attention/streak), never green or red.

### Station List (signature component)
The anchor surface's primary content: a full-width bordered instrument panel (`--radius-lg`, 1px `--border`) listing turmas as monitored stations. Each row is a CSS-grid instrument strip: a padded-number station ID with LED (mono, tabular, LED colored `--green` when `turma.ativo`, `--border-muted` when not), station name (IBM Plex Sans, truncated), period (mono, tabular), a 5-segment ascending-height intensity meter reflecting real `turma.ativo` state (never fabricated progress data — bars are on/off, not a fake percentage), a plain-language status word (`em curso` / `encerrada`), and a hover/focus-revealed "abrir" affordance with an arrow that translates on hover. Rows update their LED/band/status in place on refetch rather than unmounting and remounting.

## Do's and Don'ts

### Do:
- **Do** use JetBrains Mono with `tabular-nums` for every date, count, period, or sequential value.
- **Do** pair every color-bearing status indicator (LED, badge, band) with a plain-language text label.
- **Do** keep both light and dark themes as complete, independently defined token sets — never derive one from the other with a filter or opacity trick.
- **Do** update a changed list row's status in place (LED, band, label) on refetch rather than removing and reinserting the DOM node.
- **Do** confine the decorative hue set (pink, cyan, orange, yellow) to identity/cosmetic roles: avatar tint, per-tab nav identity ink.
- **Do** reserve amber strictly for streak/attention (never error) and red strictly for critical/error (never a generic warning).

### Don't:
- **Don't** use `box-shadow` anywhere; depth comes from border + background-tone stepping only.
- **Don't** use the reserved status hues (cyan/green/amber/red) for decorative or identity purposes — that confusion was an actual finish-review defect this round (tab identity and streak/points icons initially borrowed status hues) and must not recur.
- **Don't** apply full-pill (999px) radius to anything that isn't a genuinely circular instrument part; rectangular containers stay in the 4–8px range.
- **Don't** show fabricated or invented progress/intensity values — the 5-segment band reflects real `ativo` state, not a synthesized percentage; this rule is a direct extension of PRODUCT.md's ban on pressuring students with invented performance data.
- **Don't** let color speak alone on any status indicator; always pair with a text label.
