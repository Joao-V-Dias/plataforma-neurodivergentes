---
version: 1
slug: "src-pages-aluno-minhasturmaspage-tsx"
primary_target: "src/pages/aluno/MinhasTurmasPage.tsx"
related_targets: []
---

# Aluno Home (Minhas Turmas) — Redesign

Scope: full system visual redesign, replacing the previous "Working Notebook" world end to end (all functionality preserved). Mode: Operate. Anchor surface: `/` (Aluno) → `MinhasTurmasPage`, then the same world applied across shells, auth, onboarding, aluno, gestao and problem-solving screens in one pass.

Audience/job/action/proof/constraints: neurodivergent students (mixed age, ADHD/autism/dyslexia/dyscalculia) and their teachers/coordinators; must stay predictable, literal, low-stimulation-capable, colorblind-safe, WCAG AA, and never pressure the student with performance data. CodeMirror's own syntax theme is out of scope — untouched. Explicitly rejects both the prior notebook world (read as childish) and generic pastel ed-tech.

## Direction contract

THESIS: Progress is a personal reading, not a rank — the app is an instrument panel a student checks on their own system, never a scoreboard against classmates.

OWN-WORLD: A monitoring-instrument console (INMET-style weather/telemetry station). Dark-first ground `#0d1a24`, ink `#e7eef2`, one signal cyan `#3aa6c9` for readings/links/focus, amber `#e8a33d` reserved for streak/attention, one red `#c94f3a` for critical/error only — body text stays achromatic elsewhere. Light theme is a full parallel swap, not a lightened dark. Hairline 1px bezels, no shadow, small consistent radius (never sharp/square, never pill), tabular figures, banded intensity meters replace card lists. Atkinson Hyperlegible stays for body (accessibility, non-negotiable); IBM Plex Sans for headings (technical, humanist); JetBrains Mono for tabular/code readouts. Named rules: The Live-Reading Raise (a changed row updates in place, never remove-and-reinsert), The Single-Band Raise (color only on the active status band), The Commit-Preview Raise (a preview beat before any irreversible submit), plus the carried No-Color-Alone and Plain-Name raises.

STORY: The student opens their panel, sees turmas as monitored stations down a left rail, this term's path as a live reading trail across the header, opens a problem, watches hint intensity climb one band at a time, and a stamped reading — never a rank — marks it resolved.

FIRST VIEWPORT: Left instrument rail (one station/turma per row, live status LED); full-width header readout (date, streak and points as small gauges); the main panel is a dense station list filling the width, no wasted side padding, each row a bordered instrument strip with a progress band and inline "abrir" action on hover/focus.

FORM: Estacao de Leitura — candidate 6 of 7 on my own ranked list, assigned by the roll; seed key 40a4e4cd; build-phase kind `assigned`.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.

## Unresolved decisions

- Exact per-turma station color/LED assignment (reuse existing per-turma color if any, or assign deterministically by turma id).
- Whether Mapa do Jogo becomes a literal "front system moving across a map" or a simpler station list like Minhas Turmas — resolve when that surface is built.
