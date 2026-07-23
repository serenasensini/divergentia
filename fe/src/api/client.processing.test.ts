import { describe, expect, it, vi } from 'vitest';
import { createApiClient } from './client';

/**
 * Verifies each document-processing method targets the right endpoint,
 * method and JSON envelope (the backend expects a wrapper key per operation).
 */
function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

/** A vi.fn typed to match fetch so mock.calls has proper argument types. */
function fetchReturning(body: unknown, status = 200) {
  return vi.fn(
    (_input: RequestInfo | URL, _init?: RequestInit): Promise<Response> =>
      Promise.resolve(jsonResponse(body, status)),
  );
}

const ID = 'abc';
const ok = { success: true, document_id: ID, download_url: 'x', format: 'docx' };

describe('api client — processing endpoints', () => {
  it('formatting wraps body under "formatting" via PUT', async () => {
    const fetchImpl = fetchReturning(ok);
    const client = createApiClient({ baseUrl: 'http://x', fetchImpl });
    await client.applyFormatting(ID, { titles: true });

    const [url, init] = fetchImpl.mock.calls[0];
    expect(url).toBe('http://x/api/documents/abc/format');
    expect(init?.method).toBe('PUT');
    expect(JSON.parse(init?.body as string)).toEqual({
      formatting: { titles: true },
    });
  });

  it('framing wraps body under "framing"', async () => {
    const fetchImpl = fetchReturning(ok);
    const client = createApiClient({ baseUrl: 'http://x', fetchImpl });
    await client.applyFraming(ID, { paragraphs: true });
    const body = JSON.parse(fetchImpl.mock.calls[0][1]?.body as string);
    expect(body).toEqual({ framing: { paragraphs: true } });
  });

  it('spacing, keywords and highlighting use their wrapper keys', async () => {
    const fetchImpl = fetchReturning(ok);
    const client = createApiClient({ baseUrl: 'http://x', fetchImpl });
    await client.applySpacing(ID, { paragraphs: true });
    await client.applyKeywords(ID, { max_keywords: 3 });
    await client.applyHighlighting(ID, { enabled: true, nouns: true });
    const keys = fetchImpl.mock.calls.map(
      (c) => Object.keys(JSON.parse(c[1]?.body as string))[0],
    );
    expect(keys).toEqual(['spacing', 'keywords', 'highlighting']);
  });

  it('summarize/paraphrase document post the raw body', async () => {
    const fetchImpl = fetchReturning({
      document_id: ID,
      summary: 's',
      style: 'simple',
    });
    const client = createApiClient({ baseUrl: 'http://x', fetchImpl });
    await client.summarizeDocument(ID, 'brief');
    await client.paraphraseDocument(ID, 'simple');
    expect(fetchImpl.mock.calls[0][0]).toBe(
      'http://x/api/documents/abc/summarize',
    );
    expect(JSON.parse(fetchImpl.mock.calls[0][1]?.body as string)).toEqual({
      summary_type: 'brief',
      add_to_document: false,
    });
    expect(JSON.parse(fetchImpl.mock.calls[1][1]?.body as string)).toEqual({
      style: 'simple',
      apply_to_document: false,
    });
  });

  it('builds a download URL', () => {
    const client = createApiClient({ baseUrl: 'http://x' });
    expect(client.downloadUrl(ID)).toBe('http://x/api/documents/abc/download');
  });

  it('preview and extract-text hit the right routes', async () => {
    const fetchImpl = fetchReturning({
      document_id: ID,
      text_preview: 'hi',
      character_count: 2,
      word_count: 1,
    });
    const client = createApiClient({ baseUrl: 'http://x', fetchImpl });
    await client.preview(ID);
    await client.extractText(ID);
    expect(fetchImpl.mock.calls[0][0]).toBe(
      'http://x/api/documents/abc/preview',
    );
    expect(fetchImpl.mock.calls[1][0]).toBe(
      'http://x/api/documents/abc/extract-text',
    );
    expect(fetchImpl.mock.calls[1][1]?.method).toBe('POST');
  });
});
