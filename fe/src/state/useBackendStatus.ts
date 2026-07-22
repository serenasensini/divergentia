import { useCallback, useEffect, useState } from 'react';
import { apiClient } from '../api/client';
import type { HealthResponse } from '../api/types';

export type BackendPhase = 'checking' | 'online' | 'offline';

export interface BackendStatus {
  phase: BackendPhase;
  /** Whether the AI assistant (Ollama) is awake. */
  aiAwake: boolean;
  model?: string;
  refresh: () => void;
}

/**
 * Polls /api/health so the UI can show the workshop (and the AI companion)
 * as "awake" or "asleep" instead of surfacing raw errors.
 */
export function useBackendStatus(pollMs = 20000): BackendStatus {
  const [phase, setPhase] = useState<BackendPhase>('checking');
  const [health, setHealth] = useState<HealthResponse | null>(null);

  const check = useCallback(async () => {
    try {
      const result = await apiClient.health();
      setHealth(result);
      setPhase('online');
    } catch {
      setHealth(null);
      setPhase('offline');
    }
  }, []);

  useEffect(() => {
    let active = true;
    const run = () => {
      if (active) void check();
    };
    run();
    const id = window.setInterval(run, pollMs);
    return () => {
      active = false;
      window.clearInterval(id);
    };
  }, [check, pollMs]);

  return {
    phase,
    aiAwake: Boolean(health?.ollama_status?.available),
    model: health?.ollama_status?.model,
    refresh: () => void check(),
  };
}
