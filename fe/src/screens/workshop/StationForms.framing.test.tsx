import { describe, expect, it } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import { PreferencesProvider, usePreferences } from '../../state/preferences';
import { DocumentProvider } from '../../state/document';
import { I18nProvider } from '../../state/i18n';
import { ToastProvider } from '../../components/Toast';
import { FramingStation } from './StationForms';
import { useEffect, type ReactNode } from 'react';

/** Force the UI language via the preferences store, then render children. */
function WithLanguage({
  lang,
  children,
}: {
  lang: 'en' | 'it';
  children: ReactNode;
}) {
  const { setPreference } = usePreferences();
  useEffect(() => {
    setPreference('language', lang);
  }, [lang, setPreference]);
  return <>{children}</>;
}

function renderFramingStation(lang: 'en' | 'it') {
  return render(
    <PreferencesProvider>
      <I18nProvider>
        <ToastProvider>
          <DocumentProvider>
            <WithLanguage lang={lang}>
              <FramingStation documentId="doc-1" onApplied={() => {}} />
            </WithLanguage>
          </DocumentProvider>
        </ToastProvider>
      </I18nProvider>
    </PreferencesProvider>,
  );
}

describe('FramingStation border style translation (issue #13)', () => {
  it('shows translated border style labels in English, not raw technical values', async () => {
    renderFramingStation('en');
    const select = await screen.findByLabelText(/border style/i);
    const options = within(select).getAllByRole('option');
    const labels = options.map((o) => o.textContent);

    // Labels are human-readable, translated strings...
    expect(labels).toContain('Single line');
    expect(labels).toContain('Double line');
    expect(labels).toContain('Dashed');
    // ...while the underlying values sent to the API remain the raw OOXML
    // border-style keywords the backend expects.
    const values = options.map((o) => (o as HTMLOptionElement).value);
    expect(values).toEqual(['single', 'double', 'dashed', 'dotted', 'thick']);
  });

  it('shows translated border style labels in Italian', async () => {
    renderFramingStation('it');
    const select = await screen.findByLabelText(/stile del bordo/i);
    const options = within(select).getAllByRole('option');
    const labels = options.map((o) => o.textContent);

    expect(labels).toContain('Linea singola');
    expect(labels).toContain('Linea doppia');
    expect(labels).toContain('Tratteggiato');
  });
});

