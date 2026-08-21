/**
 * Thin, typed client for the Divergentia backend.
 *
 * In the browser we rely on Vite's dev proxy (/api -> Flask), so the default
 * baseUrl is empty (same-origin). Tests and other environments can override it.
 */
import type {
  ExtractTextResponse,
  FormattingOptions,
  FramingOptions,
  HealthResponse,
  HighlightingOptions,
  KeywordOptions,
  ParaphraseResponse,
  ParaphraseStyle,
  PreviewResponse,
  ProcessResult,
  SpacingOptions,
  SummarizeResponse,
  SummaryType,
  SupportedFormatsResponse,
  TextParaphraseResponse,
  TextSummarizeResponse,
  UploadResponse,
} from './types';

export class ApiError extends Error {
  status: number;
  body: unknown;

  constructor(message: string, status: number, body: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.body = body;
  }
}

export interface ApiClientOptions {
  baseUrl?: string;
  fetchImpl?: typeof fetch;
  /** Abort an upload that makes no progress (see UPLOAD_TIMEOUT_MS). */
  uploadTimeoutMs?: number;
}

/**
 * Upload ceiling, aligned with the 120s read timeout used by gunicorn and the
 * Nginx front-end. Without it a browser that silently fails to produce the
 * request body (e.g. it cannot read the chosen file) leaves the UI stuck on
 * "Uploading…" forever, with no error and no way out.
 */
export const UPLOAD_TIMEOUT_MS = 120_000;

/**
 * Default base URL. Empty in the browser (same-origin via Vite proxy).
 * Tests set VITE_API_BASE_URL so Node's fetch receives an absolute URL.
 */
function defaultBaseUrl(): string {
  const fromImportMeta =
    typeof import.meta !== 'undefined'
      ? (import.meta as { env?: Record<string, string | undefined> }).env
          ?.VITE_API_BASE_URL
      : undefined;
  const fromProcess =
    typeof process !== 'undefined' ? process.env?.VITE_API_BASE_URL : undefined;
  return fromImportMeta ?? fromProcess ?? '';
}

async function parseError(response: Response): Promise<never> {
  let body: unknown = null;
  try {
    body = await response.json();
  } catch {
    body = await response.text().catch(() => null);
  }
  const message =
    (body && typeof body === 'object' && 'message' in body
      ? String((body as Record<string, unknown>).message)
      : undefined) ?? `Request failed with status ${response.status}`;
  throw new ApiError(message, response.status, body);
}

export function createApiClient(options: ApiClientOptions = {}) {
  const baseUrl = (options.baseUrl ?? defaultBaseUrl()).replace(/\/$/, '');
  // Resolve fetch at call time so test doubles that replace globalThis.fetch
  // after the client is constructed are still honoured.
  const doFetch: typeof fetch = options.fetchImpl
    ? options.fetchImpl
    : (...args: Parameters<typeof fetch>) => globalThis.fetch(...args);
  const uploadTimeoutMs = options.uploadTimeoutMs ?? UPLOAD_TIMEOUT_MS;
  const url = (path: string) => `${baseUrl}${path}`;

  return {
    baseUrl,

    async health(): Promise<HealthResponse> {
      const res = await doFetch(url('/api/health'), {
        headers: { Accept: 'application/json' },
      });
      if (!res.ok) return parseError(res);
      return (await res.json()) as HealthResponse;
    },

    async supportedFormats(): Promise<SupportedFormatsResponse> {
      const res = await doFetch(url('/api/formats/supported'), {
        headers: { Accept: 'application/json' },
      });
      if (!res.ok) return parseError(res);
      return (await res.json()) as SupportedFormatsResponse;
    },

    async uploadDocument(file: File): Promise<UploadResponse> {
      const form = new FormData();
      form.append('file', file);
      // Manual AbortController (rather than AbortSignal.timeout) to stay
      // compatible with the jsdom test environment.
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), uploadTimeoutMs);
      let res: Response;
      try {
        res = await doFetch(url('/api/documents/upload'), {
          method: 'POST',
          body: form,
          signal: controller.signal,
        });
      } finally {
        clearTimeout(timer);
      }
      if (!res.ok) return parseError(res);
      return (await res.json()) as UploadResponse;
    },

    async extractText(documentId: string): Promise<ExtractTextResponse> {
      const res = await doFetch(
        url(`/api/documents/${documentId}/extract-text`),
        { method: 'POST', headers: { Accept: 'application/json' } },
      );
      if (!res.ok) return parseError(res);
      return (await res.json()) as ExtractTextResponse;
    },

    async preview(documentId: string): Promise<PreviewResponse> {
      const res = await doFetch(url(`/api/documents/${documentId}/preview`), {
        headers: { Accept: 'application/json' },
      });
      if (!res.ok) return parseError(res);
      return (await res.json()) as PreviewResponse;
    },

    async styles(documentId: string): Promise<Record<string, unknown>> {
      const res = await doFetch(url(`/api/documents/${documentId}/styles`), {
        headers: { Accept: 'application/json' },
      });
      if (!res.ok) return parseError(res);
      return (await res.json()) as Record<string, unknown>;
    },

    async applyFormatting(
      documentId: string,
      formatting: FormattingOptions,
    ): Promise<ProcessResult> {
      return putJson(
        url(`/api/documents/${documentId}/format`),
        { formatting },
        doFetch,
      );
    },

    async applyFraming(
      documentId: string,
      framing: FramingOptions,
    ): Promise<ProcessResult> {
      return putJson(
        url(`/api/documents/${documentId}/framing`),
        { framing },
        doFetch,
      );
    },

    async applySpacing(
      documentId: string,
      spacing: SpacingOptions,
    ): Promise<ProcessResult> {
      return putJson(
        url(`/api/documents/${documentId}/spacing`),
        { spacing },
        doFetch,
      );
    },

    async applyKeywords(
      documentId: string,
      keywords: KeywordOptions,
    ): Promise<ProcessResult> {
      return putJson(
        url(`/api/documents/${documentId}/keywords`),
        { keywords },
        doFetch,
      );
    },

    async applyHighlighting(
      documentId: string,
      highlighting: HighlightingOptions,
    ): Promise<ProcessResult> {
      return putJson(
        url(`/api/documents/${documentId}/highlighting`),
        { highlighting },
        doFetch,
      );
    },

    async summarizeDocument(
      documentId: string,
      summaryType: SummaryType,
      addToDocument = false,
      model?: string,
    ): Promise<SummarizeResponse> {
      return postJson(
        url(`/api/documents/${documentId}/summarize`),
        { summary_type: summaryType, add_to_document: addToDocument, model },
        doFetch,
      );
    },

    async paraphraseDocument(
      documentId: string,
      style: ParaphraseStyle,
      applyToDocument = false,
      model?: string,
    ): Promise<ParaphraseResponse> {
      return postJson(
        url(`/api/documents/${documentId}/paraphrase`),
        { style, apply_to_document: applyToDocument, model },
        doFetch,
      );
    },

    async summarizeText(
      text: string,
      maxLength = 500,
      model?: string,
    ): Promise<TextSummarizeResponse> {
      return postJson(
        url('/api/text/summarize'),
        { text, max_length: maxLength, model },
        doFetch,
      );
    },

    async paraphraseText(
      text: string,
      style: ParaphraseStyle,
      model?: string,
    ): Promise<TextParaphraseResponse> {
      return postJson(url('/api/text/paraphrase'), { text, style, model }, doFetch);
    },

    /** Absolute-or-relative URL to download the latest processed document. */
    downloadUrl(documentId: string): string {
      return url(`/api/documents/${documentId}/download`);
    },
  };
}

async function sendJson<T>(
  method: 'POST' | 'PUT',
  target: string,
  body: unknown,
  doFetch: typeof fetch,
): Promise<T> {
  const res = await doFetch(target, {
    method,
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) return parseError(res);
  return (await res.json()) as T;
}

function putJson<T>(target: string, body: unknown, doFetch: typeof fetch) {
  return sendJson<T>('PUT', target, body, doFetch);
}

function postJson<T>(target: string, body: unknown, doFetch: typeof fetch) {
  return sendJson<T>('POST', target, body, doFetch);
}

export type ApiClient = ReturnType<typeof createApiClient>;

/** Default client used by the app (same-origin via dev proxy). */
export const apiClient = createApiClient();
