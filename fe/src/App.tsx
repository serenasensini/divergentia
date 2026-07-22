import { useState } from 'react';
import { WelcomeScreen } from './screens/WelcomeScreen';
import { UploadScreen } from './screens/UploadScreen';
import { WorkshopHub } from './screens/WorkshopHub';
import { useDocument } from './state/document';
import { usePreferences } from './state/preferences';
import { useI18n } from './state/i18n';
import { LanguageSelector } from './components/LanguageSelector';

type Route = 'welcome' | 'upload' | 'hub';

export function App() {
  const { preferences, setPreference } = usePreferences();
  const { t } = useI18n();
  const { clearDocument } = useDocument();
  const [route, setRoute] = useState<Route>(
    preferences.onboarded ? 'upload' : 'welcome',
  );

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-region">
        {t('app.skip')}
      </a>

      <div id="main-region">
        {route === 'welcome' && (
          <WelcomeScreen onEnter={() => setRoute('upload')} />
        )}
        {route === 'upload' && (
          <UploadScreen onUploaded={() => setRoute('hub')} />
        )}
        {route === 'hub' && (
          <WorkshopHub
            onNewDocument={() => {
              clearDocument();
              setRoute('upload');
            }}
          />
        )}
      </div>

      {route !== 'welcome' && (
        <footer className="app-footer">
          <LanguageSelector id="footer-language" />
          <button
            type="button"
            className="button button--ghost"
            onClick={() => {
              setPreference('onboarded', false);
              setRoute('welcome');
            }}
          >
            {t('app.settings')}
          </button>
        </footer>
      )}
    </div>
  );
}
