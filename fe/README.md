# Divergentia — Front-End

A calm, gamified ("Sims-like"), neurodivergent-friendly UI for the Divergentia
document API. Built for performance and accessibility.

## Stack
- **React 18 + Vite + TypeScript**
- Plain CSS design system (theming via `<html data-*>` attributes)
- **Vitest + Testing Library + jest-axe** (unit, integration & a11y tests)

## Implemented (Phase 1)
- **Step 1 — Welcome room** (`src/screens/WelcomeScreen.tsx`): pick an assistant
  companion and set accessibility preferences (reading font, colour theme,
  text size, reduce-motion, classic mode). Persisted to `localStorage`.
- **Step 2 — Upload** (`src/screens/UploadScreen.tsx`): drag-and-drop / choose a
  document, client-side format validation against the backend, explicit
  idle → working → done status via an ARIA live region, and an "assistant
  awake/asleep" indicator driven by `/api/health`.

## Implemented (Phase 2)
- **Step 3 — Workshop hub** (`src/screens/WorkshopHub.tsx`): the document sits on
  the desk; tool **stations** open in an accessible modal **Drawer**
  (`src/components/Drawer.tsx`). Stations are grouped into *Make it readable*
  and *Understand it*, with AI stations disabled (assistant "napping") when
  Ollama is down.
- **Tool stations** (`src/screens/workshop/StationForms.tsx`) covering every
  processing endpoint: colour/style (`/format`), spacing (`/spacing`), frames
  (`/framing`), highlighting (`/highlighting`), section keywords (`/keywords`),
  summary (`/summarize`) and rephrase (`/paraphrase`). Each records an entry in
  the **applied-steps timeline** and supports *start fresh from original*
  (`from_original`).
- **Live preview** (`src/screens/workshop/PreviewPanel.tsx`) via `/preview`,
  refreshed after every operation, plus a **Download** link (`/download`).
- **Typed API client** (`src/api/client.ts`) now wraps every backend endpoint.

## Accessibility
WCAG 2.2 AA intent: full keyboard operation, visible focus, real-DOM controls
(no canvas-only interactions), honours `prefers-reduced-motion` /
`prefers-contrast`, dyslexia-friendly font option, and a Classic (plain) mode.

## Getting started
```bash
npm install
npm run dev        # http://localhost:4200 (proxies /api -> http://localhost:5000)
```
Point the proxy elsewhere with `VITE_API_TARGET`, e.g.
`VITE_API_TARGET=http://localhost:8000 npm run dev`.

## Testing
```bash
npm test                     # unit + component + a11y (mocked backend)
npm run test:integration     # live tests against a running backend
# API_BASE overrides the target (default http://localhost:5000)
API_BASE=http://localhost:5000 npm run test:integration
```

## Build
```bash
npm run build    # type-checks then bundles to dist/
```
