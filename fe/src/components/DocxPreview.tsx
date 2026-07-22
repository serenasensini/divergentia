import { useEffect, useRef, useState } from 'react';
import { renderAsync } from 'docx-preview';
import { apiClient } from '../api/client';
import { useI18n } from '../state/i18n';

interface DocxPreviewProps {
  documentId: string;
  /** Bump to re-fetch and re-render after each edit. */
  refreshKey: number;
}

type Phase = 'loading' | 'ready' | 'error';

/**
 * Renders the *real* processed Word document — with all colours, frames and
 * highlights — into a sandboxed same-origin iframe using the `docx-preview`
 * library. The iframe isolates the library's injected styles from the app.
 */
export function DocxPreview({ documentId, refreshKey }: DocxPreviewProps) {
  const { t } = useI18n();
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [phase, setPhase] = useState<Phase>('loading');

  useEffect(() => {
    let cancelled = false;

    async function render() {
      setPhase('loading');
      try {
        const res = await fetch(apiClient.downloadUrl(documentId));
        if (!res.ok) throw new Error(`Download failed: ${res.status}`);
        const blob = await res.blob();
        if (cancelled) return;

        const iframe = iframeRef.current;
        const doc = iframe?.contentDocument;
        if (!iframe || !doc) throw new Error('Preview frame unavailable');

        // Reset the iframe document and prepare containers.
        doc.open();
        doc.write(
          '<!doctype html><html><head><meta charset="utf-8">' +
            '<style>body{margin:0;background:#f4f8fa;}' +
            '.docx-wrapper{background:transparent;padding:16px;}' +
            '.docx-wrapper>section.docx{box-shadow:0 1px 6px rgba(0,0,0,.15);margin:0 auto 16px;}' +
            '</style></head><body></body></html>',
        );
        doc.close();

        await renderAsync(blob, doc.body, undefined, {
          className: 'docx',
          inWrapper: true,
          ignoreWidth: false,
          ignoreHeight: false,
          breakPages: true,
          experimental: true,
          useBase64URL: true,
        });
        if (!cancelled) setPhase('ready');
      } catch {
        if (!cancelled) setPhase('error');
      }
    }

    void render();
    return () => {
      cancelled = true;
    };
  }, [documentId, refreshKey]);

  return (
    <div className="docx-preview">
      {phase === 'loading' && (
        <p className="docx-preview__status" aria-live="polite">
          {t('preview.loading')}
        </p>
      )}
      {phase === 'error' && (
        <p className="docx-preview__status preview__error" role="alert">
          {t('preview.renderError')}
        </p>
      )}
      <iframe
        ref={iframeRef}
        className="docx-preview__frame"
        title={t('preview.title')}
        data-phase={phase}
      />
    </div>
  );
}

