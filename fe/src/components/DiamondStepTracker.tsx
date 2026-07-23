import { Plumbob, type PlumbobState } from './Plumbob';

export interface DiamondStep {
  id: string;
  /** Short label shown under the diamond. */
  label: string;
}

export interface DiamondStepTrackerProps {
  /** Ordered list of steps in the workflow (e.g. the workshop stations). */
  steps: DiamondStep[];
  /** Ids (or labels) of steps already applied/completed. */
  completedIds: ReadonlySet<string>;
  /** Accessible heading id, if this tracker is described elsewhere. */
  'aria-label'?: string;
  /** Id of the step that just completed — plays a one-off bounce/spin. */
  celebratingId?: string | null;
  /** Called once the celebration animation for `celebratingId` finishes. */
  onCelebrateEnd?: () => void;
}

/**
 * Row of diamond ("plumbob") markers — one per operation. Completed steps
 * are filled, the first not-yet-completed step glows as "current", and the
 * rest stay muted outlines. A cosmetic alternative to the plain `.timeline`
 * list, gated behind the `gameTheme` preference.
 *
 * Motion (the "current" glow/pulse and the one-off "celebrate" bounce on a
 * freshly completed step) is CSS-driven and is automatically turned off by
 * the app-wide reduced-motion rules, so no extra guard is needed here.
 */
export function DiamondStepTracker({
  steps,
  completedIds,
  'aria-label': ariaLabel = 'Progress',
  celebratingId = null,
  onCelebrateEnd,
}: DiamondStepTrackerProps) {
  let currentAssigned = false;

  return (
    <ol className="diamond-tracker" aria-label={ariaLabel}>
      {steps.map((step) => {
        const isCompleted = completedIds.has(step.id);
        let state: PlumbobState = 'upcoming';
        if (isCompleted) {
          state = 'completed';
        } else if (!currentAssigned) {
          state = 'current';
          currentAssigned = true;
        }

        const status =
          state === 'completed'
            ? `${step.label}: completed`
            : state === 'current'
              ? `${step.label}: current step`
              : `${step.label}: not started yet`;

        return (
          <li key={step.id} className="diamond-tracker__item">
            <Plumbob
              state={state}
              size={22}
              label={status}
              celebrate={celebratingId === step.id}
              onCelebrateEnd={onCelebrateEnd}
            />
            <span className="diamond-tracker__label" aria-hidden="true">
              {step.label}
            </span>
          </li>
        );
      })}
    </ol>
  );
}

