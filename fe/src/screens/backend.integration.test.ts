import { afterAll, describe, expect, it } from 'vitest';
import { File as NodeFile } from 'node:buffer';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { createApiClient } from '../api/client';

// Node 18's global scope lacks File; use the one from node:buffer for uploads.
const FileCtor = (globalThis as { File?: typeof File }).File ??
  (NodeFile as unknown as typeof File);

const here = dirname(fileURLToPath(import.meta.url));
const docxBytes = readFileSync(join(here, '../test/assets/sample.docx'));

/**
 * Live integration test — runs against a REAL backend.
 * Excluded from the default unit run; execute with:
 *   VITE_API_TARGET=http://localhost:5000 npm run test:integration
 *
 * Set API_BASE to point at the backend (defaults to http://localhost:5000).
 */
const API_BASE = process.env.API_BASE ?? 'http://localhost:5000';
const client = createApiClient({ baseUrl: API_BASE });

describe('live backend integration', () => {
  const created: string[] = [];

  afterAll(() => {
    if (created.length) {
      // Registry is in-memory/ephemeral; nothing to clean up server-side.
    }
  });

  it('reports a healthy API', async () => {
    const health = await client.health();
    expect(health.status).toBe('healthy');
    expect(health.api_version).toBeTruthy();
  });

  it('advertises supported document formats', async () => {
    const res = await client.supportedFormats();
    expect(Array.isArray(res.supported_formats)).toBe(true);
    expect(res.supported_formats.length).toBeGreaterThan(0);
  });

  it('uploads a text document and returns a document id', async () => {
    const file = new FileCtor(
      ['Hello Divergentia. This is an integration test document.'],
      'integration-sample.txt',
      { type: 'text/plain' },
    );
    const res = await client.uploadDocument(file);
    created.push(res.document_id);
    expect(res.document_id).toMatch(
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i,
    );
    expect(res.file_extension).toBe('txt');
  });

  it('runs a full processing chain on a DOCX (upload → format → spacing → preview → download)', async () => {
    const docx = new FileCtor([docxBytes], 'integration-sample.docx', {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    });
    const uploaded = await client.uploadDocument(docx);
    created.push(uploaded.document_id);
    const id = uploaded.document_id;
    expect(uploaded.file_extension).toBe('docx');

    const formatted = await client.applyFormatting(id, {
      titles: true,
      section_titles: true,
      theme: { positive: '#3f7d8a', negative: '#9a3b3b', scheme: 'even' },
    });
    expect(formatted.success).toBe(true);
    expect(formatted.download_url).toContain(id);

    const spaced = await client.applySpacing(id, { paragraphs: true });
    expect(spaced.success).toBe(true);

    const preview = await client.preview(id);
    expect(preview.word_count).toBeGreaterThan(0);

    // The download endpoint should return a file (chained, latest version).
    const res = await fetch(client.downloadUrl(id));
    expect(res.status).toBe(200);
    const bytes = await res.arrayBuffer();
    expect(bytes.byteLength).toBeGreaterThan(0);
  });
});
