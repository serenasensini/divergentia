import { useCallback, useEffect, useState } from 'react';
import { apiClient, ApiError } from '../../api/client';
import type { PreviewResponse } from '../../api/types';
import { DocxPreview } from '../../components/DocxPreview';
import { useI18n } from '../../state/i18n';

interface PreviewPanelProps {
  documentId: string;
  /** Changes to this value trigger a refresh (bumped after each operation). */
  refreshKey: number;
}

type Phase = 'loading' | 'ready' | 'error';

/**
 * Live preview of the current (latest processed) document: a rich rendering of
 * the real Word file — with every colour, frame and highlight — via an embedded
 * docx viewer. The viewer can be collapsed for a calmer, lower-stimulation
 * view, and refreshes whenever refreshKey changes.
 */
export function PreviewPanel({ documentId, refreshKey }: PreviewPanelProps) {
  const { t } = useI18n();
  const [phase, setPhase] = useState<Phase>('loading');
  const [preview, setPreview] = useState<PreviewResponse | null>(null);
  const [error, setError] = useState('');
  const [showDocument, setShowDocument] = useState(true);

  const load = useCallback(async () => {
    setPhase('loading');
    try {
      const res = await apiClient.preview(documentId);
      setPreview(res);
      setPhase('ready');
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t('preview.error'));
      setPhase('error');
    }
  }, [documentId, t]);

  useEffect(() => {
    void load();
  }, [load, refreshKey]);

  return (
    <aside className="preview" aria-labelledby="preview-title">
      <div className="preview__head">
        <h2 id="preview-title">{t('preview.title')}</h2>
        <div className="preview__controls">
          <button
            type="button"
            className={`button button--ghost${showDocument ? ' is-active' : ''}`}
            aria-pressed={showDocument}
            onClick={() => setShowDocument((prev) => !prev)}
          >
            <span className="button__icon" aria-hidden="true">
              📄
            </span>
            {t('preview.showDocument')}
          </button>
          <button
            type="button"
            className="button button--ghost"
            onClick={() => void load()}
          >
            <span className="button__icon" aria-hidden="true">
              🔄
            </span>
            {t('common.refresh')}
          </button>
        </div>
      </div>

      {phase === 'loading' && <p aria-live="polite">{t('preview.loading')}</p>}
      {phase === 'error' && (
        <p className="preview__error" role="alert">
          {error}
        </p>
      )}
      {phase === 'ready' && preview && (
        <p className="preview__counts">
          {t('preview.counts', {
            words: preview.word_count.toLocaleString(),
            chars: preview.character_count.toLocaleString(),
          })}
        </p>
      )}

      {showDocument && (
        <DocxPreview documentId={documentId} refreshKey={refreshKey} />
      )}
    </aside>
  );
}
