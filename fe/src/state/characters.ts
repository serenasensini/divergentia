/**
 * Assistant characters the user can pick in the Welcome room.
 * Purely cosmetic + a warm, predictable companion metaphor.
 */
export interface AssistantCharacter {
  id: string;
  name: string;
  emoji: string;
  blurb: string;
}

export const CHARACTERS: AssistantCharacter[] = [
  {
    id: 'lumi',
    name: 'Lumi',
    emoji: '🦉',
    blurb: 'A calm owl who reads slowly and never rushes you.',
  },
  {
    id: 'pip',
    name: 'Pip',
    emoji: '🦊',
    blurb: 'A tidy fox who loves sorting and structuring documents.',
  },
  {
    id: 'nova',
    name: 'Nova',
    emoji: '🐢',
    blurb: 'A steady turtle who keeps everything one clear step at a time.',
  },
  {
    id: 'ember',
    name: 'Ember',
    emoji: '🐉',
    blurb: 'A gentle dragon who highlights and colours with care.',
  },
];

export const DEFAULT_CHARACTER_ID = CHARACTERS[0].id;
