import { CHARACTERS } from '../state/characters';

interface AssistantAvatarProps {
  characterId: string;
  /** asleep dims the avatar to signal the AI (Ollama) is unavailable. */
  asleep?: boolean;
  size?: number;
}

/**
 * Renders the chosen companion. Decorative: the emoji is aria-hidden and the
 * character name is exposed as text where needed by callers.
 */
export function AssistantAvatar({
  characterId,
  asleep = false,
  size = 64,
}: AssistantAvatarProps) {
  const character =
    CHARACTERS.find((c) => c.id === characterId) ?? CHARACTERS[0];

  return (
    <span
      className="assistant-avatar"
      data-asleep={String(asleep)}
      style={{ fontSize: `${size}px`, lineHeight: 1 }}
      role="img"
      aria-label={
        asleep ? `${character.name} is resting` : `${character.name}, your assistant`
      }
    >
      {character.emoji}
      {asleep && (
        <span className="assistant-avatar__zzz" aria-hidden="true">
          z
        </span>
      )}
    </span>
  );
}
