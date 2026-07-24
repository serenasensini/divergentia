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

---

5. FE — WorkshopHub: applied steps list (accessibility & UX)

**Status:** To be done.

Check the applied steps list in the WorkshopHub for accessibility and UX improvements. Ensure that the list is easily navigable, readable, and provides clear feedback to users about their progress. Consider implementing ARIA roles and properties to enhance screen reader support, and review the visual design for clarity and contrast.

---

6. FE — WorkshopHub: station card interactions (accessibility & UX)

**Status:** To be done.

Check the station card interactions in the WorkshopHub for accessibility and UX improvements. Ensure that the cards are easily navigable, readable, and provide clear feedback to users about their actions. Consider implementing ARIA roles and properties to enhance screen reader support, and review the visual design for clarity and contrast.

--- 

7. FE - Complete translation coverage (i18n)

**Status:** Done (GitHub issue #3).

Character descriptions (Lumi, Pip, Nova, Ember) are no longer hardcoded: the
`blurb` was removed from `fe/src/state/characters.ts` and moved to i18n under
`characters.<id>.blurb` (EN + IT), resolved at render time in
`WelcomeScreen.tsx`. Other hardcoded strings found in an audit were also moved
to i18n: the Toast region/dismiss `aria-label`s (`notifications.*` in
`Toast.tsx`) and the keyword-model placeholder (`keywords.modelPlaceholder` in
`StationForms.tsx`). A missing EN `welcome.soundEffects` key was added so the
EN locale no longer falls back to the raw key path. `tsc --noEmit` clean and the
FE suite (41 tests) is green.

---

8. FE - Explain first-time options with tooltips or a guided tour

**Status:** Done (GitHub issue #4).

Each first-time preference in `WelcomeScreen.tsx` now has an accessible help
tooltip via the existing `<Tooltip>` component (focus/hover reachable,
`aria-describedby`, Esc-dismissible). The reading-font tooltip lists every font
option with a short description (`welcome.help.font` + `welcome.fontDesc.*`);
theme, text size, reduce-motion, classic mode, game theme and sound effects each
get a `welcome.help.*` explanation (EN + IT). No tour animation was added, so
`prefers-reduced-motion` is unaffected. Covered by a new tooltip test.

**Follow-up fix:** the reading-font preference was correctly wired
(`<html data-font>` → `--font-active` → `body`) but the Atkinson Hyperlegible
and OpenDyslexic families were never loaded, so selecting them silently fell
back to the system font. Both are now self-hosted under `fe/public/fonts/`
(`.woff2`, OFL) with `@font-face` rules (Regular/Bold/Italic/BoldItalic,
`font-display: swap`) in `global.css`, so the choice now visibly changes the
rendering — offline, no third-party requests. See `fe/public/fonts/NOTICE.md`.

---

9. FE - Add a "Reset to defaults" button for preferences

**Status:** Done (GitHub issue #5).

A clearly-labelled "Reset to defaults" button in the Welcome/preferences setup
section (`WelcomeScreen.tsx`) opens an accessible confirmation dialog
(`role="alertdialog"`, `aria-modal`, labelled/described, focus moved to the
confirm button, Esc/overlay-click to cancel) before calling the existing
`reset()` from `preferences.tsx`. A polite `role="status"` live region announces
completion. New i18n keys `welcome.reset*` (EN + IT). Covered by new tests for
the confirm and cancel flows.

---

10. BE - Check for PDF upload support

**Status:** Done (GitHub issue #6).

PDF uploads are accepted and converted to DOCX on upload via **PyMuPDF**
(`be/app/utils/document_converter.py`): the text is extracted and rebuilt into
real, editable paragraphs so all `python-docx`-based formatting features work.
Image-only/scanned PDFs (no extractable text) are rejected with a clear message
(no OCR). Covered by `be/tests/unit/test_document_converter.py`.

> Implementation note: converting PDFs via LibreOffice produced a DOCX full of
> Draw-style text boxes from which `python-docx` reads 0 paragraphs, so PyMuPDF
> is used for PDF instead of LibreOffice.

---

11. BE - Check for DOC upload support

**Status:** Done (GitHub issue #7).

DOC uploads are accepted and converted to DOCX on upload via **LibreOffice
headless** (`soffice --headless --convert-to docx`) for high structural
fidelity on legacy binary `.doc` files (`be/app/utils/document_converter.py`).
The Dockerfile installs `libreoffice-writer` + `fonts-liberation`; the
conversion binary/timeout are configurable via `LIBREOFFICE_BIN` /
`DOC_CONVERSION_TIMEOUT`. Covered by `be/tests/unit/test_document_converter.py`.

---

12. BE - Remove any RTF upload support

**Status:** Done (GitHub issue #8).

RTF support has been removed end-to-end: dropped from `ALLOWED_EXTENSIONS`
(`be/app/config.py`, `.env.example`), from the mime map
(`be/app/utils/file_handler.py`) and from text extraction
(`be/app/utils/text_extractor.py`). Bruno docs and the FE fixture
(`fe/src/test/fixtures.ts`) were updated so the supported formats are now
`['pdf', 'docx', 'doc', 'txt']`. RTF uploads are no longer accepted.

---

13. BE - Check for security vulnerabilities in file upload handling

**Status:** To be done.

Check the backend for any security vulnerabilities related to file upload handling. Ensure that proper validation, sanitization, and access controls are in place to prevent malicious files from being uploaded. Test the file upload functionality for common security issues such as file type validation, file size limits, and protection against directory traversal attacks.

---

14. BE - Implement file type validation for uploads

**Status:** To be done.

Implement file type validation for uploads in the backend. Ensure that only supported file types (e.g., DOCX, PDF) are accepted and that any unsupported file types are rejected with an appropriate error message. Test the file upload functionality to confirm that the validation works as expected and that users receive clear feedback when attempting to upload unsupported file types.

---

15. BE - Implement file size limits for uploads

**Status:** To be done.

Implement file size limits for uploads in the backend. Ensure that users are informed of the maximum allowed file size and that any files exceeding this limit are rejected with an appropriate error message. Test the file upload functionality to confirm that the size limit is enforced correctly and that users receive clear feedback when attempting to upload files that are too large.

---

16. BE - Check for logging levels and sensitive information exposure

**Status:** To be done.

Check the backend logging levels and ensure that sensitive information is not exposed in logs. Review the logging configuration to ensure that only necessary information is logged and that sensitive data (e.g., user credentials, personal information) is not included in log entries. Test the application to confirm that logs are appropriately configured and that sensitive information is protected. Allow changing the level of logging (e.g., debug, info, warning, error) via configuration or environment variables, and ensure that sensitive information is never logged at any level.


17. BE - Framing options should be translated

**Status:** To be done.

Ensure that the framing options in the backend are translated and available in all supported languages. Review the codebase for any hardcoded strings related to framing options and replace them with appropriate i18n keys. Verify that translations are available for all supported languages and that the application correctly displays the translated text based on user preferences or browser settings. 

As an example, now we've got "single", "double", "dashed" and so on for the border style, but they are not translated.

18. BE - Lists should be framed in a single box as a single unit, not as single rows

**Status:** To be done.

Ensure that lists in the backend are framed as a single box, rather than framing each list item individually. Review the codebase for any logic related to framing lists and update it to treat the entire list as a single unit. Test the application to confirm that lists are correctly framed as a single box and that the visual representation is consistent with the intended design.


---

19. BE - Check for performance issues with large documents

**Status:** To be done.

Check the backend for any performance issues when processing large documents. Test the application with various document sizes and formats to identify any bottlenecks or slowdowns in processing. Optimize the backend logic as needed to improve performance and ensure that large documents are handled efficiently without causing timeouts or excessive resource usage.

---

20. BE - Allow exporting the processed document in multiple formats (e.g., DOCX, PDF)

**Status:** To be done.

Allow users to export the processed document in multiple formats, such as DOCX and PDF. Implement the necessary backend logic to convert the processed document into the desired format and provide a download link for users. Test the export functionality to confirm that documents are correctly generated in the selected format and that users can successfully download them.

--- 

21. FE - Convert the "Mostra solo testo" feature in a reading mode, with a toggle button to switch between reading and editing mode

**Status:** To be done.

Emulating what Firefox does natively as browser on pages, this feature will allow users to switch between a reading mode, where only the text is displayed, and an editing mode, where the full document can be edited. Implement a toggle button to switch between these modes and ensure that the application correctly updates the display based on the selected mode. Test the feature to confirm that it works as expected and provides a seamless reading and editing experience.