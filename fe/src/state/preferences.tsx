import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { DEFAULT_CHARACTER_ID } from './characters';

/**
 * Accessibility + personalisation preferences.
 * These are the neurodivergent-first controls that drive the whole UI.
 */
export type FontChoice = 'system' | 'atkinson' | 'dyslexic';
export type ThemeChoice = 'calm' | 'dark' | 'high-contrast';
export type TextSize = 'small' | 'medium' | 'large' | 'x-large';
export type Language = 'en' | 'it';

export interface Preferences {
  characterId: string;
  font: FontChoice;
  theme: ThemeChoice;
  textSize: TextSize;
  reduceMotion: boolean;
  /** Classic mode swaps the isometric scene for a plain list UI. */
  classicMode: boolean;
  /** UI language for internationalisation. */
  language: Language;
  /** Whether the Welcome room has been completed at least once. */
  onboarded: boolean;
}

const STORAGE_KEY = 'divergentia.preferences.v1';

/** Best-effort default language from the browser, falling back to English. */
function detectLanguage(): Language {
  if (typeof navigator === 'undefined') return 'en';
  const langs = [navigator.language, ...(navigator.languages ?? [])];
  return langs.some((l) => l?.toLowerCase().startsWith('it')) ? 'it' : 'en';
}

export const DEFAULT_PREFERENCES: Preferences = {
  characterId: DEFAULT_CHARACTER_ID,
  font: 'system',
  theme: 'calm',
  textSize: 'medium',
  reduceMotion:
    typeof window !== 'undefined' &&
    typeof window.matchMedia === 'function' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches,
  classicMode: false,
  language: detectLanguage(),
  onboarded: false,
};

function loadPreferences(): Preferences {
  if (typeof window === 'undefined' || !window.localStorage) {
    return DEFAULT_PREFERENCES;
  }
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULT_PREFERENCES;
    const parsed = JSON.parse(raw) as Partial<Preferences>;
    return { ...DEFAULT_PREFERENCES, ...parsed };
  } catch {
    return DEFAULT_PREFERENCES;
  }
}

interface PreferencesContextValue {
  preferences: Preferences;
  setPreference: <K extends keyof Preferences>(
    key: K,
    value: Preferences[K],
  ) => void;
  reset: () => void;
}

const PreferencesContext = createContext<PreferencesContextValue | null>(null);

/**
 * Reflect preferences onto <html> as data-attributes so CSS can respond
 * without JavaScript re-renders. Also honours system contrast preference.
 */
function applyToDocument(prefs: Preferences) {
  if (typeof document === 'undefined') return;
  const root = document.documentElement;
  const systemHighContrast =
    typeof window !== 'undefined' &&
    typeof window.matchMedia === 'function' &&
    window.matchMedia('(prefers-contrast: more)').matches;
  const theme = systemHighContrast ? 'high-contrast' : prefs.theme;

  root.dataset.theme = theme;
  root.dataset.font = prefs.font;
  root.dataset.textSize = prefs.textSize;
  root.dataset.reduceMotion = String(prefs.reduceMotion);
  root.lang = prefs.language;
}

export function PreferencesProvider({ children }: { children: ReactNode }) {
  const [preferences, setPreferences] = useState<Preferences>(loadPreferences);

  useEffect(() => {
    applyToDocument(preferences);
    if (typeof window !== 'undefined' && window.localStorage) {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences));
    }
  }, [preferences]);

  const setPreference = useCallback(
    <K extends keyof Preferences>(key: K, value: Preferences[K]) => {
      setPreferences((prev) => ({ ...prev, [key]: value }));
    },
    [],
  );

  const reset = useCallback(() => setPreferences(DEFAULT_PREFERENCES), []);

  const value = useMemo(
    () => ({ preferences, setPreference, reset }),
    [preferences, setPreference, reset],
  );

  return (
    <PreferencesContext.Provider value={value}>
      {children}
    </PreferencesContext.Provider>
  );
}

export function usePreferences(): PreferencesContextValue {
  const ctx = useContext(PreferencesContext);
  if (!ctx) {
    throw new Error('usePreferences must be used within a PreferencesProvider');
  }
  return ctx;
}
