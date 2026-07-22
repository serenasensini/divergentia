import { render } from '@testing-library/react';
import type { ReactElement } from 'react';
import { PreferencesProvider } from '../state/preferences';
import { DocumentProvider } from '../state/document';
import { I18nProvider } from '../state/i18n';
import { ToastProvider } from '../components/Toast';

/** Render a component wrapped in the app-wide providers. */
export function renderWithProviders(ui: ReactElement) {
  return render(
    <PreferencesProvider>
      <I18nProvider>
        <ToastProvider>
          <DocumentProvider>{ui}</DocumentProvider>
        </ToastProvider>
      </I18nProvider>
    </PreferencesProvider>,
  );
}
