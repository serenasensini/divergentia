/**
 * Plumbob — the reusable diamond motif for the optional Sims-inspired game
 * theme. A single rotated-square shape with a soft gradient and glow, used
 * as the app's signature accent: header logo, step markers, current-step
 * indicator, etc.
 *
 * Purely decorative by default (aria-hidden). Pass `label` to make it a
 * meaningful status icon for assistive tech (e.g. "Step complete").
 *
 * Sizing, colour and animation all come from CSS custom properties so the
 * shape can be dropped anywhere and themed consistently. Any glow/pulse
 * animation is automatically disabled by the global reduced-motion rules
 * (`html[data-reduce-motion='true']` and the OS `prefers-reduced-motion`
 * media query) — no extra logic is needed here.
 */
import type { CSSProperties } from 'react';

export type PlumbobState = 'completed' | 'current' | 'upcoming';

export interface PlumbobProps {
  /** Visual/semantic state; defaults to 'upcoming'. */
  state?: PlumbobState;
  /** Diameter in pixels (the diamond is inscribed in a square of this size). */
  size?: number;
  /** Accessible label. When provided, the shape is exposed to assistive tech. */
  label?: string;
  className?: string;
  /**
   * Play a brief one-off spin/bounce (e.g. right when a step is completed).
   * Purely a CSS `@keyframes` animation, so it is automatically skipped by
   * the app-wide reduced-motion rules — no extra guard is needed here.
   */
  celebrate?: boolean;
  /** Called once the celebrate animation finishes, to let the parent reset it. */
  onCelebrateEnd?: () => void;
}

export function Plumbob({
  state = 'upcoming',
  size = 28,
  label,
  className = '',
  celebrate = false,
  onCelebrateEnd,
}: PlumbobProps) {
  return (
    <span
      className={`plumbob plumbob--${state} ${celebrate ? 'plumbob--celebrate' : ''} ${className}`.trim()}
      style={{ '--plumbob-size': `${size}px` } as CSSProperties}
      role={label ? 'img' : undefined}
      aria-label={label}
      aria-hidden={label ? undefined : true}
      onAnimationEnd={celebrate ? onCelebrateEnd : undefined}
    >
      <span className="plumbob__facet" />
    </span>
  );
}


