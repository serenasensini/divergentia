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
        setMessage(err instanceof ApiError ? err.message : t('errors.generic'));
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
