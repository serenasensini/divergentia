import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen, within, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PreferencesProvider } from '../../state/preferences';
import { DocumentProvider } from '../../state/document';
import { I18nProvider } from '../../state/i18n';
import { ToastProvider } from '../../components/Toast';
import { KeywordsStation, SummarizeStation, ParaphraseStation } from './StationForms';
import { resolveAiModel } from '../../state/aiModels';

const applyKeywords = vi.fn().mockResolvedValue({ success: true });
const summarizeDocument = vi.fn().mockResolvedValue({ summary: 'ok' });
const paraphraseDocument = vi.fn().mockResolvedValue({});

vi.mock('../../api/client', () => ({
  apiClient: {
    applyKeywords: (...args: unknown[]) => applyKeywords(...args),
    summarizeDocument: (...args: unknown[]) => summarizeDocument(...args),
    paraphraseDocument: (...args: unknown[]) => paraphraseDocument(...args),
  },
}));

function renderStation(children: React.ReactNode) {
  return render(
    <PreferencesProvider>
      <I18nProvider>
        <ToastProvider>
          <DocumentProvider>{children}</DocumentProvider>
        </ToastProvider>
      </I18nProvider>
    </PreferencesProvider>,
  );
}

describe('AI model tier selector (issue #22)', () => {
  beforeEach(() => {
    window.localStorage.clear();
    applyKeywords.mockClear();
    summarizeDocument.mockClear();
    paraphraseDocument.mockClear();
  });

  it('renders exactly the three tiers with friendly labels (no raw model ids)', async () => {
    renderStation(<KeywordsStation documentId="doc-1" onApplied={() => {}} />);
    const select = await screen.findByRole('combobox', { name: /ai model/i });
    const options = within(select).getAllByRole('option');
    const labels = options.map((o) => o.textContent);

    expect(labels).toEqual(['Fast (lighter)', 'Balanced', 'Advanced (best quality)']);
    // The user-visible labels never expose the raw Ollama model tag.
    expect(labels.join(' ')).not.toMatch(/llama/i);
  });

  it('has an accessible tooltip describing the performance trade-off', async () => {
    renderStation(<KeywordsStation documentId="doc-1" onApplied={() => {}} />);
    const trigger = await screen.findByRole('button', { name: /ai model/i });
    expect(trigger).toBeInTheDocument();
    fireEvent.focus(trigger);
    expect(await screen.findByRole('tooltip')).toHaveTextContent(/faster|slower/i);
  });

  it('defaults to the balanced tier and sends its resolved model id when extracting keywords', async () => {
    renderStation(<KeywordsStation documentId="doc-1" onApplied={() => {}} />);
    const select = await screen.findByRole('combobox', { name: /ai model/i });
    expect((select as HTMLSelectElement).value).toBe('balanced');

    fireEvent.submit(select.closest('form')!);

    await waitFor(() => expect(applyKeywords).toHaveBeenCalledTimes(1));
    const [, options] = applyKeywords.mock.calls[0];
    expect(options.model).toBe(resolveAiModel('balanced'));
  });

  it('persists the selected tier and reuses it for summarise/rephrase requests', async () => {
    const user = userEvent.setup();
    renderStation(<KeywordsStation documentId="doc-1" onApplied={() => {}} />);
    const select = await screen.findByRole('combobox', { name: /ai model/i });
    await user.selectOptions(select, 'fast');
    expect((select as HTMLSelectElement).value).toBe('fast');

    // Preference persists to localStorage immediately.
    await waitFor(() => {
      const raw = window.localStorage.getItem('divergentia.preferences.v1');
      expect(raw).toContain('"aiModel":"fast"');
    });

    // A different station picks up the same persisted tier.
    renderStation(<SummarizeStation documentId="doc-1" onApplied={() => {}} />);
    const sumSelects = await screen.findAllByRole('combobox', { name: /ai model/i });
    const lastSelect = sumSelects[sumSelects.length - 1] as HTMLSelectElement;
    expect(lastSelect.value).toBe('fast');

    fireEvent.submit(lastSelect.closest('form')!);
    await waitFor(() => expect(summarizeDocument).toHaveBeenCalledTimes(1));
    const summarizeArgs = summarizeDocument.mock.calls[0];
    expect(summarizeArgs[3]).toBe(resolveAiModel('fast'));
  });

  it('resolves the chosen tier to the expected model id for rephrase requests', async () => {
    renderStation(<ParaphraseStation documentId="doc-1" onApplied={() => {}} />);
    const select = await screen.findByRole('combobox', { name: /ai model/i });
    fireEvent.submit(select.closest('form')!);

    await waitFor(() => expect(paraphraseDocument).toHaveBeenCalledTimes(1));
    const args = paraphraseDocument.mock.calls[0];
    expect(args[3]).toBe(resolveAiModel('balanced'));
  });
});

