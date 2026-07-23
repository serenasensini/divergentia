# Divergentia — Project Notes & Roadmap

Working notes for planned activities. Each entry has a status and a step-by-step
procedure so the work can be picked up later.

---

## 1. General repository README

**Status:** Done.

A complete root [`README.md`](./README.md) already exists and covers:
overview, **authors (Serena Sensini & Martina Ricci)**, **license (CC BY-NC 4.0)**,
architecture, prerequisites, manual local setup (BE + FE), Docker/Podman setup,
testing and project layout.

The [`LICENSE`](./LICENSE) file has now been added at the repo root with the
full **CC BY-NC 4.0** legal text and an attribution header for *Serena Sensini
and Martina Ricci*. All paths referenced by the README (`./LICENSE`,
`be/.env.example`, `be/README.md`) resolve correctly.

### Remaining (optional, not automatable from here)

1. Optionally add badges (license, Python/Node versions) at the top of the README.
2. Verify the "Run locally" steps end-to-end on a clean clone (venv, spaCy model
   download, `npm install`, Docker compose up) — needs a real clean checkout/
   machine, not done as part of this pass.

---

## 2. BE — framing across a page break (edge case)

**Status:** Done — implemented and covered by unit tests.

**Problem (solved):** Framing wraps a section/paragraph/sentence in a 1x1 table
with all four borders. When a framed block spans a page break, Word used to
split the table row and render the box awkwardly.

**Implemented behaviour** in `be/app/services/formatting_service.py`:
- `_set_table_borders_edges(table, width, color, style, edges)` draws only the
  requested outer borders (others emitted as `w:val="nil"`); `_set_table_borders`
  is now a thin wrapper calling it with all four edges.
- `_has_page_break_before`, `_run_has_page_break`, `_split_runs_at_page_break`
  and `_segment_block_by_page_breaks` detect explicit `w:br type="page"` runs,
  `pageBreakBefore` paragraphs and `w:lastRenderedPageBreak` hints, splitting a
  block into page-delimited segments.
- `_encapsulate_paragraphs_in_table` emits one table per segment via
  `_segment_edges(index, total)`: first segment -> top/left/right, middle ->
  left/right, last -> bottom/left/right, single segment -> all four (unchanged
  behaviour). `_add_page_break_paragraph_after` forces the continuation table
  to start at the top of the next page.
- Unit tests in `be/tests/unit/test_framing.py` (`TestFramingAcrossPageBreak`)
  cover: a section split via `page_break_before`, a paragraph split via an
  explicit page break, and the single-page case keeping the full box. All 8
  tests in that file pass.

### Remaining (optional follow-up)

- `_encapsulate_sentences_in_tables` still uses the old full-box
  `_set_table_borders` (a single sentence rarely spans a page, so this was left
  as-is); apply the same segment-splitting treatment there if that edge case
  becomes relevant.
- The optional high-fidelity LibreOffice-headless pagination pass (for blocks
  with no explicit break) was not implemented — gate it behind a config flag if
  needed later.

---

## 3. FE — "The Sims"-inspired game UI

**Status:** Done (prototyped behind an opt-in preference, `gameTheme`), not
the default experience.

Goal: give the interface a playful, game-like feel inspired by *The Sims* — the
iconic green **plumbob** diamond, strong saturated colours and glossy elements —
**without** breaking the low-stimulation, neurodivergent-friendly design goals.

### What's implemented

- **`gameTheme` preference** (`fe/src/state/preferences.tsx`), default `false`,
  reflected on `<html data-game-theme>`; toggled from the Welcome screen
  (`fe/src/screens/WelcomeScreen.tsx`) next to the existing classic-mode switch.
- **`<Plumbob />` component** (`fe/src/components/Plumbob.tsx`): a reusable
  rotated-square diamond with `completed` / `current` / `upcoming` states,
  decorative by default (`aria-hidden`) or exposed as `role="img"` with a label.
  Also supports a one-off `celebrate` bounce/spin (see micro-interactions below).
- **`<DiamondStepTracker />` component**
  (`fe/src/components/DiamondStepTracker.tsx`): a row of plumbobs, one per
  workshop station, wired into `WorkshopHub` (`fe/src/screens/WorkshopHub.tsx`)
  next to the existing `.timeline` list when `gameTheme` is on. A station is
  marked completed the first time its drawer reports `onApplied`.
- **Saturated accent palette** as CSS custom properties, scoped under
  `html[data-game-theme='true']` in `fe/src/styles/global.css`
  (`--plumbob-green/teal/coral/yellow/glow`) — large surfaces (`--bg`,
  `--surface`) are untouched, only the plumbob accents use them.
- **Glossy, chunky controls.** Under `data-game-theme`, `.button` gets rounded
  corners, a soft drop shadow and a hover/active lift; `.button--primary` gets
  a green→teal gradient with a small diamond accent glyph before the label.
  A new `.button--diamond` utility class provides a compact diamond-shaped
  icon-button variant for future primary actions.
- **Playful copy.** When `gameTheme` is on, the "Applied so far" section swaps
  to gamified strings ("Unlocked so far" / "No stages unlocked yet. Pick a
  station to begin your quest…", EN + IT) via new `hub.appliedSoFarGame` /
  `hub.nothingAppliedGame` i18n keys, kept calm rather than arcade-like.
- **Playful, optional micro-interactions.**
  - The plumbob for a station plays a brief one-off spin/bounce
    (`.plumbob--celebrate`, `@keyframes plumbob-celebrate`) the moment that
    station is completed, self-clearing via `onAnimationEnd`.
  - A soft two-note "chime" (`fe/src/utils/sound.ts`, synthesised with the Web
    Audio API — no binary asset) plays on the same event.
  - **Gating:** the chime is a new, separate `soundEffects` preference
    (default `false`, opt-in, only shown/settable once `gameTheme` is on) — it
    never plays unless both `gameTheme` and `soundEffects` are on. The bounce
    animation is CSS-only and is automatically skipped by the existing
    `html[data-reduce-motion='true']` / `prefers-reduced-motion` rules, exactly
    like the "current" pulse — no extra JS guard needed.
- **Plumbob motif wired more broadly**: an SVG favicon
  (`fe/public/favicon.svg`, linked from `fe/index.html`) and an inline plumbob
  next to both the Welcome screen title and the Workshop hub title when
  `gameTheme` is on.
- **Tests**: `Plumbob.test.tsx`, `DiamondStepTracker.test.tsx` (jest-axe a11y +
  state/celebrate assertions), `WelcomeScreen.test.tsx` (`gameTheme` toggle) and
  `WorkshopHub.test.tsx` (diamond tracker rendering, chime played only when
  `gameTheme` **and** `soundEffects` are both on). Full FE suite (38 tests) and
  `tsc --noEmit` both pass.

### Remaining (future iterations, optional)

- Apply `.button--diamond` to an actual primary action once a suitable compact
  icon-only control is identified (e.g. a quick-access toolbar).
- Broader gamified copy pass ("unlock the next stage" style language) beyond
  the applied-steps section, if desired.
- Consider surfacing `soundEffects` as a global mute rather than tied only to
  the game theme, if sound effects expand beyond the success chime.

---

## 4. FE — WorkshopHub responsiveness (stations grid vs. preview panel)

**Status:** Done.

**Problem:** In the side-by-side layout (viewport ≥ 900px), the tool-station
cards grid (`.station-grid`, `repeat(auto-fit, minmax(200px, 1fr))`) could pack
in 3 columns. Because CSS Grid tracks default to an "auto" (content-based)
minimum size, that 3-column content forced `.hub__stations` wider than its
`1.6fr` share, shrinking the `1fr` preview column below a usable width (a
classic grid-blowout). On top of that, `DocxPreview` rendered the document at
its fixed physical page width (`ignoreWidth: false`, ~800px for A4/Letter),
so any preview column narrower than that always needed horizontal scrolling
— defeating the "visible at the document's minimum width without scrolling"
goal regardless of column width.

**Fix**, in `fe/src/styles/global.css` and `fe/src/components/DocxPreview.tsx`:
- `.hub__layout` (≥900px) now uses
  `grid-template-columns: minmax(0, 1fr) minmax(320px, 420px);` instead of a
  plain `1.6fr 1fr` split — the preview column always gets a guaranteed
  320–420px band, whatever the stations column ends up needing.
- `.hub__stations { min-width: 0; }` at that breakpoint prevents the grid
  blowout described above.
- `.station-grid` is capped to `repeat(2, 1fr)` once the preview sits
  alongside it (≥900px), so the cards can never expand to 3 columns and eat
  into the preview's space. Below 900px (stacked single-column layout) it
  keeps the flexible `auto-fit` behaviour, since there's no competing preview
  column there.
- `DocxPreview` now calls `renderAsync(..., { ignoreWidth: true, ... })`, so
  the rendered page reflows to the available preview width instead of
  enforcing the document's physical page size — the preview is always fully
  visible with no horizontal scrollbar, at any column width. Added defensive
  `max-width: 100%` CSS for the wrapper/section/images/tables inside the
  preview iframe as a safety net for any fixed-width content.

Verified: `tsc --noEmit` clean, full FE test suite green (38 tests), and the
frontend image rebuilt + redeployed via `podman compose build web` /
`podman compose up -d --force-recreate web`.



