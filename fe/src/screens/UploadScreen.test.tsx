import { describe, expect, it } from 'vitest';
import { fireEvent, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe } from 'jest-axe';
import { UploadScreen } from './UploadScreen';
import { renderWithProviders } from '../test/renderWithProviders';

describe('UploadScreen (Step 2)', () => {
  it('shows the workshop as open and the assistant awake', async () => {
    renderWithProviders(<UploadScreen />);
    await waitFor(() =>
      expect(
        screen.getByText(/your assistant is awake/i),
      ).toBeInTheDocument(),
    );
  });

  it('lists supported formats fetched from the backend', async () => {
    renderWithProviders(<UploadScreen />);
    await waitFor(() =>
      expect(screen.getByText(/Supported:/i)).toHaveTextContent('.txt'),
    );
  });

  it('uploads a supported file and reports success', async () => {
    const user = userEvent.setup();
    renderWithProviders(<UploadScreen />);
    await screen.findByText(/Supported:/i);

    const file = new File(['hello world'], 'sample.txt', {
      type: 'text/plain',
    });
    const input = screen.getByLabelText(/Choose a document to upload/i);
    await user.upload(input, file);

    await waitFor(() =>
      expect(screen.getByRole('status')).toHaveTextContent(
        /is on the desk/i,
      ),
    );
    expect(screen.getByText(/536df518-/)).toBeInTheDocument();
  });

  it('rejects an unsupported file type before uploading', async () => {
    renderWithProviders(<UploadScreen />);
    await screen.findByText(/Supported:/i);

    const file = new File(['data'], 'photo.png', { type: 'image/png' });
    const input = screen.getByLabelText(
      /Choose a document to upload/i,
    ) as HTMLInputElement;
    // fireEvent bypasses the input's `accept` filter so we can assert our own
    // client-side validation message.
    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() =>
      expect(screen.getByRole('status')).toHaveTextContent(
        /aren't supported yet/i,
      ),
    );
  });

  it('has no detectable accessibility violations', async () => {
    const { container } = renderWithProviders(<UploadScreen />);
    await screen.findByText(/Supported:/i);
    expect(await axe(container)).toHaveNoViolations();
  });
});
