/**
 * Assistant characters the user can pick in the Welcome room.
 * Purely cosmetic + a warm, predictable companion metaphor.
 *
 * Only language-neutral data lives here (id, proper-noun name, emoji). The
 * descriptive `blurb` is resolved through i18n at render time via the
 * `characters.<id>.blurb` key, so it is translated like any other string.
 */
export interface AssistantCharacter {
  id: string;
  name: string;
  emoji: string;
}

export const CHARACTERS: AssistantCharacter[] = [
  { id: 'lumi', name: 'Lumi', emoji: '🦉' },
  { id: 'pip', name: 'Pip', emoji: '🦊' },
  { id: 'nova', name: 'Nova', emoji: '🐢' },
];

export const DEFAULT_CHARACTER_ID = CHARACTERS[0].id;
