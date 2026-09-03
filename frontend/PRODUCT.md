# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Three groups sharing one platform, scoped to a single school (`Instituicao`) at a time:

- **Aluno (student):** the primary user. A neurodivergent student (ADHD, ASD/autism, dyslexia, dyscalculia, and other conditions from an extensible vocabulary) learning programming (Python). Age/grade level is mixed and not fixed to one school stage — design should stay age-neutral rather than skewing toward small children or toward teens specifically. Solves programming problems in a code editor, receives AI-generated progressive hints tuned to their profile, tracks personal progress, picks an avatar, and sees their classes ("turmas") through a gamified frame (`Mapa do Jogo`, `Batalha`).
- **Professor (teacher):** creates and manages turmas (classes), authors problems (with public + hidden test cases), approves student self-registrations, views student progress and hint history/effectiveness for their classes.
- **Coordenador / Diretor (coordinator / director):** same capabilities as Professor plus institution-wide visibility (all turmas, all users) and the ability to create accounts for any role below them. Diretor is the top of the RBAC hierarchy (`Diretor > Coordenador > Professor > Aluno`) and is the only role that can exist before any other account does (bootstrapped via a setup script, not a public endpoint).

## Product Purpose

An adaptive programming-education platform built specifically for neurodivergent students. It exists to make learning to code accessible to students whose needs (attention, sensory load, literacy, working memory) are usually an afterthought in generic coding-education tools, by adapting both the *content* of AI-generated hints and the *interface itself* (contrast, font, motion, read-aloud) to each student's declared profile — while keeping teachers and school staff in control of curriculum, class rosters, and oversight of what the AI says to each student.

Success means a neurodivergent student can work through programming problems with hint support that matches how they process information, without a teacher having to manually tailor material per student, and without the AI ever overstepping into clinical territory.

## Positioning

The differentiator is that adaptation is structural, not cosmetic: hint content itself changes per student (tone, structure, pacing) based on a declared neurodivergence profile and Big Five/TIPI personality traits, enforced server-side via prompt engineering and hint-level guardrails a competitor could not simply copy by adding a dark-mode toggle. Progressive hints are staged (Socratic question -> conceptual hint -> pseudocode -> full solution) and the level is server-calculated, never client-chosen, so a student can't skip straight to the answer. This is paired with UI-level accessibility (high contrast, readable font, reduced motion, read-aloud) applied globally from the same stored preferences used to inform the AI — the accessibility layer and the adaptive-teaching layer read from the same source of truth about the student.

## Operating Context

- Runs inside a school's own workflow: a Diretor bootstraps the institution, creates Coordenador/Professor accounts, teachers create turmas and enroll students, students self-register (pending approval) or are created directly by staff.
- Every account and every piece of data is scoped to one `Instituicao` (multi-tenant) — no cross-school visibility.
- Code submissions run in an isolated, network-disabled, resource-limited Docker sandbox; only Python is currently supported.
- AI hints are provided by Groq (`llama-3.3-70b-versatile`); if no API key is configured, hints fail closed with a controlled 503 rather than breaking the rest of the app.
- Neurodivergence profile and Big Five data are treated as sensitive health-adjacent data under LGPD (Brazil's data-protection law) — see `docs/lgpd.md` in the repo root. Consent is captured separately from general signup consent, and profile history is append-only (never overwritten).
- Interface language is Portuguese (pt-BR); this is a Brazilian project.

## Capabilities and Constraints

- RBAC hierarchy `Diretor > Coordenador > Professor > Aluno`; a role can create any role strictly below it, never its own or above.
- Student self-registration requires an institution code and starts inactive until a Professor+ approves it.
- Hint levels (1-4) are strictly sequential and server-enforced; the client never selects or displays a level chooser beyond "request next hint."
- Hidden test cases and their inputs/outputs/errors are never exposed to students, even on failure; only pass/fail per case.
- Hint effectiveness metrics (time-to-resolve after a hint) are visible only to Professor+, deliberately never shown to the student, to avoid performance-pressure during learning.
- Accessibility preferences (font, contrast, extra time, read-aloud, reduced-stimulus) are not clinical data, are user-editable at any time by anyone, and apply optimistically (before server confirmation) across the whole app via `data-*` attributes on `<html>`.
- Default theme is dark (`escuro`); a light theme (`claro`) exists and is user-toggleable, persisted in `localStorage`.
- Only Python is supported for code execution today (scope decision, not a technical ceiling).
- Frontend is a from-scratch rebuild (this `frontend/` directory) of an earlier implementation now kept at `../frontend-legacy/` for reference; treat `frontend-legacy` as prior art/evidence, not as current product truth.

## Brand Commitments

Working name: **Plataforma Adaptativa**. No committed logo, mascot, or visual identity yet — current favicon/icon assets are placeholders, not a brand commitment. No other naming, tagline, or voice commitments exist yet.

## Evidence on Hand

None. This is an academic prototype built for an Iniciação Científica (undergraduate research) project — there is no live partner school, no real student/teacher accounts, no testimonials, case studies, or usage metrics to reference. Future design and copy work must not fabricate school names, student counts, quotes, or outcomes; use placeholder/sample data clearly framed as such where a screen needs example content.

## Product Principles

1. **Adaptation is structural, not decorative.** Both AI hint content and UI presentation must trace back to the student's actual stored profile/preferences — never a generic "accessibility mode" applied uniformly.
2. **Staff stays in control, AI stays in its lane.** Teachers/coordinators/directors always have final visibility and control; the AI never diagnoses, evaluates, or replaces professional judgment about a student's condition.
3. **Never pressure the student with their own performance data.** Metrics like hint effectiveness and time-to-resolve exist for staff calibration only, not for student-facing gamified pressure.
4. **Sensitive data stays sensitive.** Neurodivergence and personality data are health-adjacent under LGPD — minimize exposure, never resurface the raw condition where only the adaptation code/log is needed.
5. **Game framing serves engagement, not childishness.** Mapa do Jogo/Batalha/avatars should read as motivating across a mixed age range, not as a young-kids skin bolted onto a serious tool.

## Accessibility & Inclusion

Core product requirement, not an add-on: high contrast mode, adjustable/readable font (including a dyslexia-friendlier option), reduced-motion/reduced-stimulus mode (disables all animation/transition), read-aloud (Web Speech API) on problem statements and hints, and extra-time accommodation — all driven by per-user `PreferenciasAcessibilidade` and applied globally, not per-page. Target audience explicitly includes ADHD, autism (TEA), dyslexia, and dyscalculia; original scope cited a Lighthouse Accessibility Score target above 90 (unconfirmed as a currently binding number, but directionally correct — treat WCAG AA as the working bar unless the user sets a stricter one).
