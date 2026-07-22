import { useMemo, useState } from 'react';
import { apiClient } from '../api/client';
import { AssistantAvatar } from '../components/AssistantAvatar';
import { Drawer } from '../components/Drawer';
import { useDocument } from '../state/document';
import { usePreferences } from '../state/preferences';
import { useBackendStatus } from '../state/useBackendStatus';
import { useI18n } from '../state/i18n';
import { PreviewPanel } from './workshop/PreviewPanel';
import { STATIONS, STATION_GROUPS } from './workshop/stations';

interface WorkshopHubProps {
  /** Called when the user wants to bring in a different document. */
  onNewDocument: () => void;
}

/**
 * Step 3 — Workshop hub.
 * The document sits on the desk; each tool station opens an accessible drawer.
 * A timeline records applied steps; a live preview and download sit alongside.
 */
export function WorkshopHub({ onNewDocument }: WorkshopHubProps) {
  const { preferences } = usePreferences();
  const { t } = useI18n();
  const backend = useBackendStatus();
  const { documentId, documentName, steps } = useDocument();
  const [activeStationId, setActiveStationId] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const activeStation = useMemo(
    () => STATIONS.find((s) => s.id === activeStationId) ?? null,
    [activeStationId],
  );

  if (!documentId) return null;

  const bumpPreview = () => setRefreshKey((k) => k + 1);

  return (
    <main className="hub" aria-labelledby="hub-title">
      <header className="hub__header">
        <AssistantAvatar
          characterId={preferences.characterId}
          asleep={!backend.aiAwake}
        />
        <div className="hub__heading">
          <h1 id="hub-title">{t('hub.title')}</h1>
          <p className="hub__doc">
            {t('hub.workingOn', { name: '' })}
            <strong>{documentName}</strong>
          </p>
        </div>
        <div className="hub__actions">
          <a
            className="button button--primary"
            href={apiClient.downloadUrl(documentId)}
            download
          >
            {t('common.download')}
          </a>
          <button
            type="button"
            className="button button--ghost"
            onClick={onNewDocument}
          >
            {t('hub.bringAnother')}
          </button>
        </div>
      </header>

      {!backend.aiAwake && (
        <p className="hub__notice" role="status">
          {t('hub.napping')}
        </p>
      )}

      <div className="hub__layout">
        <div className="hub__stations">
          {STATION_GROUPS.map((group) => (
            <section key={group} aria-labelledby={`group-${group}`}>
              <h2 id={`group-${group}`} className="hub__group-title">
                {t(`groups.${group}`)}
              </h2>
              <div className="station-grid">
                {STATIONS.filter((s) => s.group === group).map((station) => {
                  const disabled = station.requiresAI && !backend.aiAwake;
                  return (
                    <button
                      key={station.id}
                      type="button"
                      className="station-card"
                      onClick={() => setActiveStationId(station.id)}
                      disabled={disabled}
                      aria-describedby={`station-desc-${station.id}`}
                    >
                      <span className="station-card__emoji" aria-hidden="true">
                        {station.emoji}
                      </span>
                      <span className="station-card__title">
                        {t(`stations.${station.id}.title`)}
                        {station.requiresAI && (
                          <span className="station-card__ai">
                            {t('hub.ai')}
                          </span>
                        )}
                      </span>
                      <span
                        className="station-card__desc"
                        id={`station-desc-${station.id}`}
                      >
                        {t(`stations.${station.id}.description`)}
                      </span>
                    </button>
                  );
                })}
              </div>
            </section>
          ))}

          <section aria-labelledby="steps-title" className="hub__steps">
            <h2 id="steps-title" className="hub__group-title">
              {t('hub.appliedSoFar')}
            </h2>
            {steps.length === 0 ? (
              <p className="hub__steps-empty">{t('hub.nothingApplied')}</p>
            ) : (
              <ol className="timeline">
                {steps.map((step) => (
                  <li key={step.id} className="timeline__item">
                    <span className="timeline__label">{step.label}</span>
                    <span className="timeline__detail">{step.detail}</span>
                  </li>
                ))}
              </ol>
            )}
          </section>
        </div>

        <PreviewPanel documentId={documentId} refreshKey={refreshKey} />
      </div>

      <Drawer
        open={activeStation !== null}
        title={activeStation ? t(`stations.${activeStation.id}.title`) : ''}
        onClose={() => setActiveStationId(null)}
      >
        {activeStation && (
          <activeStation.Component
            documentId={documentId}
            onApplied={bumpPreview}
          />
        )}
      </Drawer>
    </main>
  );
}
