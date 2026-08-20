/**
 * AI model tiers for Ollama-backed features (keywords, summary, rephrase).
 *
 * Users pick a friendly tier label; they never see or type a raw model name.
 * Each tier maps to a concrete reference Ollama model tag. Keeping the map in
 * one place makes it easy to change the underlying models later without
 * touching every station that uses them (see issue #22).
 */
export type AiModelTier = 'fast' | 'balanced' | 'advanced';

export const DEFAULT_AI_MODEL_TIER: AiModelTier = 'balanced';

/** Ordered so UIs can render tiers from lightest to heaviest. */
export const AI_MODEL_TIERS: AiModelTier[] = ['fast', 'balanced', 'advanced'];

/** Tier -> concrete Ollama model tag sent to the backend. */
export const AI_MODEL_TIER_TO_MODEL: Record<AiModelTier, string> = {
  fast: 'llama3.2:1b',
  balanced: 'llama3.2:3b',
  advanced: 'llama3.1:8b',
};

/** Resolve a tier to its concrete Ollama model id. */
export function resolveAiModel(tier: AiModelTier): string {
  return AI_MODEL_TIER_TO_MODEL[tier];
}

