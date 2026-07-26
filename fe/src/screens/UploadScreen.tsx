import { useCallback, useEffect, useRef, useState } from 'react';
import { apiClient, ApiError } from '../api/client';
import type { UploadResponse } from '../api/types';
import { AssistantAvatar } from '../components/AssistantAvatar';
import { useDocument } from '../state/document';
import { usePreferences } from '../state/preferences';
import { useBackendStatus } from '../state/useBackendStatus';
import { useI18n } from '../state/i18n';

type UploadPhase = 'idle' | 'working' | 'done' | 'error';

function extensionOf(name: string): string {
  const dot = name.lastIndexOf('.');
  return dot === -1 ? '' : name.slice(dot + 1).toLowerCase();
}

function humanSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/**
 * Step 2 — Upload.
 * Drag a document onto the desk (or use the button). We validate the file
 * type against the backend's supported formats, then upload it. Every state
 * is announced explicitly so nothing feels like it "just happened".
 */
export function UploadScreen({ onUploaded }: { onUploaded?: () => void }) {
  const { preferences } = usePreferences();
  const { t } = useI18n();
  const backend = useBackendStatus();
  const { setDocument } = useDocument();

  const [formats, setFormats] = useState<string[] | null>(null);
  const [maxUploadSizeBytes, setMaxUploadSizeBytes] = useState<number | null>(null);
  const [phase, setPhase] = useState<UploadPhase>('idle');
  const [message, setMessage] = useState('');
  const [result, setResult] = useState<UploadResponse | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    let active = true;
    apiClient
      .supportedFormats()
      .then((res) => {
        if (!active) return;
        setFormats(res.supported_formats.map((f) => f.toLowerCase()));
        if (typeof res.max_upload_size_bytes === 'number') {
          setMaxUploadSizeBytes(res.max_upload_size_bytes);
        }
      })
      .catch(() => {
        // Non-fatal: we can still attempt an upload; the server re-validates.
        if (active) setFormats(null);
      });
    return () => {
      active = false;
    };
  }, []);

  const handleFile = useCallback(
    async (file: File) => {
      const ext = extensionOf(file.name);
      if (formats && ext && !formats.includes(ext)) {
        setPhase('error');
        setResult(null);
        setMessage(
          t('upload.unsupported', {
            ext,
            list: formats.map((f) => `.${f}`).join(', '),
          }),
        );
        return;
      }

      if (maxUploadSizeBytes && file.size > maxUploadSizeBytes) {
        setPhase('error');
        setResult(null);
        setMessage(
          t('upload.tooLarge', {
            name: file.name,
            size: humanSize(file.size),
            max: humanSize(maxUploadSizeBytes),
          }),
        );
        return;
      }

      setPhase('working');
      setResult(null);
      setMessage(t('upload.uploadingFile', { name: file.name }));

      try {
        const uploaded = await apiClient.uploadDocument(file);
        setResult(uploaded);
        setDocument(uploaded);
        setPhase('done');
        setMessage(
          t('upload.done', {
            name: uploaded.original_filename,
            size: humanSize(uploaded.file_size),
          }),
        );
      } catch (err) {
        setPhase('error');
        setResult(null);
        const detail =
          err instanceof ApiError ? err.message : t('upload.genericError');
        setMessage(detail);
      }
    },
    [formats, maxUploadSizeBytes, setDocument, t],
  );

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files?.[0];
      if (file) void handleFile(file);
    },
    [handleFile],
  );

  const acceptAttr = formats ? formats.map((f) => `.${f}`).join(',') : undefined;

  return (
    <main className="upload" aria-labelledby="upload-title">
      <header className="upload__header">
        <AssistantAvatar
          characterId={preferences.characterId}
          asleep={!backend.aiAwake}
        />
        <div>
          <h1 id="upload-title" className="upload__title">
            {t('upload.title')}
          </h1>
          <p className="upload__status-line">
            {backend.phase === 'checking' && t('upload.checking')}
            {backend.phase === 'offline' && t('upload.offline')}
            {backend.phase === 'online' &&
              (backend.aiAwake
                ? t('upload.onlineAwake')
                : t('upload.onlineAsleep'))}
          </p>
        </div>
      </header>

      <div
        className={`desk${dragOver ? ' desk--over' : ''}`}
        data-phase={phase}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
      >
        <p className="desk__hint" id="desk-hint">
          {t('upload.deskHint')}
        </p>
        <button
          type="button"
          className="button button--primary"
          onClick={() => inputRef.current?.click()}
          disabled={phase === 'working'}
          aria-describedby="desk-hint"
        >
          {phase === 'working' ? t('upload.uploading') : t('upload.choose')}
        </button>
        <input
          ref={inputRef}
          className="visually-hidden"
          type="file"
          accept={acceptAttr}
          aria-label={t('upload.chooseAria')}
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) void handleFile(file);
            e.target.value = '';
          }}
        />
        {formats && (
          <p className="desk__formats">
            {t('upload.supported', {
              list: formats.map((f) => `.${f}`).join(', '),
            })}
            {maxUploadSizeBytes && (
              <>
                {' '}
                {t('upload.maxSize', { size: humanSize(maxUploadSizeBytes) })}
              </>
            )}
          </p>
        )}
      </div>

      <p
        className={`upload__message upload__message--${phase}`}
        role="status"
        aria-live="polite"
      >
        {message}
      </p>

      {phase === 'done' && result && (
        <dl className="upload__result" aria-label={t('upload.resultName')}>
          <div>
            <dt>{t('upload.resultName')}</dt>
            <dd>{result.original_filename}</dd>
          </div>
          <div>
            <dt>{t('upload.resultType')}</dt>
            <dd>.{result.file_extension}</dd>
          </div>
          <div>
            <dt>{t('upload.resultSize')}</dt>
            <dd>{humanSize(result.file_size)}</dd>
          </div>
          <div>
            <dt>{t('upload.resultId')}</dt>
            <dd>
              <code>{result.document_id}</code>
            </dd>
          </div>
        </dl>
      )}

      {phase === 'done' && result && (
        <button
          type="button"
          className="button button--primary upload__enter"
          onClick={() => onUploaded?.()}
        >
          {t('upload.enter')}
        </button>
      )}
    </main>
  );
}
