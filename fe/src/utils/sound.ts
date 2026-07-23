/**
 * Tiny success "chime" for the optional Sims-inspired game theme.
 *
 * Synthesised on the fly with the Web Audio API (no binary asset to ship or
 * maintain). Callers are expected to already have checked the `gameTheme`
 * and `soundEffects` preferences — this module only guards against the
 * runtime environment (no `AudioContext`, jsdom in tests, browser autoplay
 * restrictions, etc.) so it can never throw or crash the app.
 */
let sharedContext: AudioContext | null = null;

function getAudioContext(): AudioContext | null {
  if (typeof window === 'undefined') return null;
  const Ctor =
    window.AudioContext ||
    (window as unknown as { webkitAudioContext?: typeof AudioContext })
      .webkitAudioContext;
  if (!Ctor) return null;
  try {
    if (!sharedContext) {
      sharedContext = new Ctor();
    }
    return sharedContext;
  } catch {
    return null;
  }
}

/**
 * Play a short, calm two-note "ding" (no harsh transients) to celebrate a
 * completed step. Silently does nothing if the Web Audio API is unavailable
 * or the context cannot resume (e.g. no prior user gesture).
 */
export function playSuccessChime(): void {
  const ctx = getAudioContext();
  if (!ctx) return;

  try {
    if (ctx.state === 'suspended') {
      void ctx.resume();
    }

    const now = ctx.currentTime;
    const notes: Array<[frequency: number, start: number]> = [
      [660, 0],
      [880, 0.09],
    ];

    notes.forEach(([frequency, start]) => {
      const oscillator = ctx.createOscillator();
      const gain = ctx.createGain();
      oscillator.type = 'sine';
      oscillator.frequency.setValueAtTime(frequency, now + start);

      gain.gain.setValueAtTime(0.0001, now + start);
      gain.gain.exponentialRampToValueAtTime(0.15, now + start + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + start + 0.25);

      oscillator.connect(gain);
      gain.connect(ctx.destination);
      oscillator.start(now + start);
      oscillator.stop(now + start + 0.3);
    });
  } catch {
    // Best-effort only; never let a sound glitch break the workshop flow.
  }
}

