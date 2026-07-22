import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App';
import { PreferencesProvider } from './state/preferences';
import { DocumentProvider } from './state/document';
import { I18nProvider } from './state/i18n';
import { ToastProvider } from './components/Toast';
import './styles/global.css';

/**
 * Safety net: this app does not use a service worker, but a stale one left by a
 * previous deployment on this origin can intercept and stall API uploads
 * (surfacing as an nginx 408). Proactively unregister any existing worker and
 * clear its caches on startup. The self-destroying /sw.js handles browsers that
 * only run their registered worker; this covers the current page load.
 */
function purgeStaleServiceWorkers(): void {
  if (typeof navigator === 'undefined' || !('serviceWorker' in navigator)) {
    return;
  }
  navigator.serviceWorker
    .getRegistrations()
    .then((registrations) => {
      for (const registration of registrations) {
        void registration.unregister();
      }
    })
    .catch(() => {
      /* Ignore: nothing we can do if the SW API rejects. */
    });

  if ('caches' in window) {
    caches
      .keys()
      .then((keys) => Promise.all(keys.map((key) => caches.delete(key))))
      .catch(() => {
        /* Ignore. */
      });
  }
}

purgeStaleServiceWorkers();

const container = document.getElementById('root');

if (!container) {
  throw new Error('Root container #root not found');
}

createRoot(container).render(
  <StrictMode>
    <PreferencesProvider>
      <I18nProvider>
        <ToastProvider>
          <DocumentProvider>
            <App />
          </DocumentProvider>
        </ToastProvider>
      </I18nProvider>
    </PreferencesProvider>
  </StrictMode>,
);
