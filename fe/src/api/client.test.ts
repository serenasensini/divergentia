import { describe, expect, it } from 'vitest';
import { createApiClient, ApiError } from './client';
import { mockEndpoint } from '../test/fetchMock';
import { uploadFixture } from '../test/fixtures';

const client = createApiClient();

describe('api client', () => {
  it('fetches health', async () => {
    const health = await client.health();
    expect(health.status).toBe('healthy');
    expect(health.ollama_status.available).toBe(true);
  });

  it('fetches supported formats', async () => {
    const res = await client.supportedFormats();
    expect(res.supported_formats).toContain('txt');
  });

  it('uploads a document as multipart form data', async () => {
    const file = new File(['hello world'], 'notes.txt', { type: 'text/plain' });
    const res = await client.uploadDocument(file);
    expect(res.document_id).toBe(uploadFixture.document_id);
    expect(res.original_filename).toBe('notes.txt');
  });

  it('raises ApiError with the server message on failure', async () => {
    mockEndpoint(
      'POST',
      '/api/documents/upload',
      () =>
        new Response(JSON.stringify({ message: 'File too large' }), {
          status: 400,
          headers: { 'Content-Type': 'application/json' },
        }),
    );
    const file = new File(['x'], 'big.txt', { type: 'text/plain' });
    await expect(client.uploadDocument(file)).rejects.toMatchObject({
      name: 'ApiError',
      status: 400,
      message: 'File too large',
    });
    await expect(client.uploadDocument(file)).rejects.toBeInstanceOf(ApiError);
  });
});
