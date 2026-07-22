import { vi } from 'vitest';
import {
  formatsFixture,
  healthFixture,
  previewFixture,
  processResultFixture,
  uploadFixture,
} from './fixtures';

/**
 * Deterministic global.fetch mock reproducing the backend contract.
 * Chosen over a network interceptor because it works reliably across the
 * jsdom/undici combination without depending on fetch-patching internals.
 */
type FetchHandler = (
  url: string,
  init?: RequestInit,
) => Response | Promise<Response>;

const overrides: { method: string; match: string; handler: FetchHandler }[] = [];

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

/** Override the response for a single endpoint for the current test. */
export function mockEndpoint(
  method: string,
  match: string,
  handler: FetchHandler,
): void {
  overrides.push({ method: method.toUpperCase(), match, handler });
}

async function router(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  const url =
    typeof input === 'string'
      ? input
      : input instanceof URL
        ? input.toString()
        : input.url;
  const method = (init?.method ?? 'GET').toUpperCase();

  const override = overrides.find(
    (o) => o.method === method && url.includes(o.match),
  );
  if (override) return override.handler(url, init);

  if (url.includes('/api/health')) return json(healthFixture);
  if (url.includes('/api/formats/supported')) return json(formatsFixture);
  if (url.includes('/api/documents/upload')) {
    const body = init?.body;
    let filename = uploadFixture.original_filename;
    if (body instanceof FormData) {
      const file = body.get('file');
      if (file && typeof file !== 'string') filename = file.name;
    }
    return json({ ...uploadFixture, original_filename: filename }, 201);
  }
  if (url.includes('/preview')) return json(previewFixture);
  if (url.includes('/extract-text')) {
    return json({
      document_id: previewFixture.document_id,
      text_content: previewFixture.text_preview,
      character_count: previewFixture.character_count,
      word_count: previewFixture.word_count,
    });
  }
  if (url.includes('/summarize')) {
    return json({
      document_id: previewFixture.document_id,
      summary: 'A short summary.',
      key_points: ['Point one', 'Point two'],
      summary_type: 'brief',
    });
  }
  if (url.includes('/paraphrase')) {
    return json({
      document_id: previewFixture.document_id,
      style: 'simple',
      paraphrased_sections: { '0': 'Rephrased text.' },
    });
  }
  if (
    method === 'PUT' &&
    (url.includes('/format') ||
      url.includes('/framing') ||
      url.includes('/spacing') ||
      url.includes('/keywords') ||
      url.includes('/highlighting'))
  ) {
    return json(processResultFixture);
  }
  return json({ message: 'Not found' }, 404);
}

export function installFetchMock(): void {
  overrides.length = 0;
  global.fetch = vi.fn(router) as unknown as typeof fetch;
}

export function resetFetchMock(): void {
  overrides.length = 0;
}
