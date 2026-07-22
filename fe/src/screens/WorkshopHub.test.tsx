import { describe, expect, it } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useEffect, type ReactNode } from 'react';
import { axe } from 'jest-axe';
import { WorkshopHub } from './WorkshopHub';
import { PreferencesProvider } from '../state/preferences';
import { DocumentProvider, useDocument } from '../state/document';
import { I18nProvider } from '../state/i18n';
import { ToastProvider } from '../components/Toast';
import { uploadFixture } from '../test/fixtures';

function SeedDocument({ children }: { children: ReactNode }) {
  const { setDocument, documentId } = useDocument();
  useEffect(() => {
    setDocument(uploadFixture);
  }, [setDocument]);
  return documentId ? <>{children}</> : null;
}

function renderHub() {
  return render(
    <PreferencesProvider>
      <I18nProvider>
        <ToastProvider>
          <DocumentProvider>
            <SeedDocument>
              <WorkshopHub onNewDocument={() => {}} />
            </SeedDocument>
          </DocumentProvider>
        </ToastProvider>
      </I18nProvider>
    </PreferencesProvider>,
  );
}

describe('WorkshopHub (Step 3)', () => {
  it('shows the current document and a working download link', async () => {
    renderHub();
    expect(await screen.findByText(uploadFixture.original_filename)).toBeInTheDocument();
    const download = screen.getByRole('link', { name: /download document/i });
    expect(download).toHaveAttribute(
      'href',
      `/api/documents/${uploadFixture.document_id}/download`,
    );
  });

  it('loads the live preview with word counts', async () => {
    const user = userEvent.setup();
    renderHub();
    await waitFor(() =>
      expect(screen.getByText(/9 words/i)).toBeInTheDocument(),
    );
    // Switch to the plain-text view to assert the extracted preview text.
    await user.click(screen.getByRole('button', { name: /show text only/i }));
    expect(screen.getByText(/preview of the document text/i)).toBeInTheDocument();
  });

  it('renders reading and AI tool stations', async () => {
    renderHub();
    await screen.findByText(uploadFixture.original_filename);
    expect(
      screen.getByRole('button', { name: /Colour & style/i }),
    ).toBeEnabled();
    // AI stations are enabled because the health fixture reports Ollama awake.
    expect(screen.getByRole('button', { name: /Summary/i })).toBeEnabled();
  });

  it('applies a formatting step and records it in the timeline', async () => {
    const user = userEvent.setup();
    renderHub();
    await screen.findByText(uploadFixture.original_filename);

    await user.click(screen.getByRole('button', { name: /Colour & style/i }));
    const dialog = await screen.findByRole('dialog');
    await user.click(within(dialog).getByRole('button', { name: /Apply colours/i }));

    // Success is announced via a top-right toast (outside the dialog).
    await screen.findByText(/Colours applied/i);
    await user.click(within(dialog).getByRole('button', { name: /close/i }));

    expect(
      screen.getByText(/Applied colours to selected parts/i),
    ).toBeInTheDocument();
  });

  it('has no detectable accessibility violations', async () => {
    const user = userEvent.setup();
    const { container } = renderHub();
    await screen.findByText(/9 words/i);
    // Use the plain-text view: axe cannot traverse the docx preview iframe
    // under jsdom ("Respondable target must be a frame in the current window").
    await user.click(screen.getByRole('button', { name: /show text only/i }));
    expect(await axe(container)).toHaveNoViolations();
  });
});
