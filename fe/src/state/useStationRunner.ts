import { useCallback, useState } from 'react';
import { ApiError } from '../api/client';
import { useToast } from '../components/Toast';
import { useI18n } from '../state/i18n';

export type RunPhase = 'idle' | 'working' | 'done' | 'error';

interface StationRunner {
  phase: RunPhase;
  message: string;
  /** Execute an API call, managing status text and error handling. */
  run: (
    task: () => Promise<void>,
    workingMessage: string,
    doneMessage: string,
  ) => Promise<void>;
  reset: () => void;
}

/**
 * Shared state machine for a tool station: idle → working → done | error.
 * The working state shows inline status; success is announced via a top-right
 * toast (auto-dismissing after 5s) rather than an inline box; errors stay
 * inline so they remain visible until the next action.
 */
export function useStationRunner(): StationRunner {
  const [phase, setPhase] = useState<RunPhase>('idle');
  const [message, setMessage] = useState('');
  const { showToast } = useToast();
  const { t } = useI18n();

  const run = useCallback(
    async (
      task: () => Promise<void>,
      workingMessage: string,
      doneMessage: string,
    ) => {
      setPhase('working');
      setMessage(workingMessage);
      try {
        await task();
        setPhase('done');
        setMessage('');
        showToast(doneMessage, 'success');
      } catch (err) {
        setPhase('error');
        // The backend error message is always in English and can be highly
        // technical (e.g. "Failed to apply text formatting: ..."), regardless
        // of the user's chosen UI language. Rather than leaking that raw,
        // untranslated text, always show a generic, localised error message.
        // The original error is still logged for debugging.
        if (err instanceof ApiError) {
          // eslint-disable-next-line no-console
          console.error('Station action failed:', err.status, err.message);
        } else {
          // eslint-disable-next-line no-console
          console.error('Station action failed:', err);
        }
        setMessage(t('errors.generic'));
      }
    },
    [showToast, t],
  );

  const reset = useCallback(() => {
    setPhase('idle');
    setMessage('');
  }, []);

  return { phase, message, run, reset };
}
