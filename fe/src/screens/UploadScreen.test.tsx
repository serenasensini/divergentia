import { describe, expect, it } from 'vitest';
import { fireEvent, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe } from 'jest-axe';
import { UploadScreen } from './UploadScreen';
import { renderWithProviders } from '../test/renderWithProviders';
import { mockEndpoint } from '../test/fetchMock';
import { uploadFixture } from '../test/fixtures';

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

  it('shows the maximum upload size fetched from the backend', async () => {
    renderWithProviders(<UploadScreen />);
    await waitFor(() =>
      expect(screen.getByText(/Supported:/i)).toHaveTextContent(
        /Maximum size: 10\.0 MB/i,
      ),
    );
  });

  it('rejects an oversized file before uploading', async () => {
    renderWithProviders(<UploadScreen />);
    await screen.findByText(/Supported:/i);

    // formatsFixture caps uploads at 10485760 bytes (10 MB); this file is
    // deliberately larger so the client-side size check rejects it without
    // ever calling the upload endpoint.
    const bigFile = new File([new Uint8Array(11 * 1024 * 1024)], 'huge.docx', {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    });
    const input = screen.getByLabelText(/Choose a document to upload/i);
    await userEvent.setup().upload(input, bigFile);

    await waitFor(() =>
      expect(screen.getByRole('status')).toHaveTextContent(/too large/i),
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

  it('keeps the selected file alive until the upload finishes', async () => {
    // Regression guard: the input used to be cleared synchronously in onChange,
    // while the request body was still being read. Firefox invalidates the
    // FileList (and the File's backing blob) on clear, so the upload hung
    // forever. The input must only be reset once the request has settled.
    let releaseUpload: (() => void) | undefined;
    const uploadInFlight = new Promise<void>((resolve) => {
      releaseUpload = resolve;
    });

    mockEndpoint('POST', '/api/documents/upload', async () => {
      await uploadInFlight;
      return new Response(JSON.stringify(uploadFixture), {
        status: 201,
        headers: { 'Content-Type': 'application/json' },
      });
    });

    const user = userEvent.setup();
    renderWithProviders(<UploadScreen />);
    await screen.findByText(/Supported:/i);

    const file = new File(['hello world'], 'sample.txt', {
      type: 'text/plain',
    });
    const input = screen.getByLabelText(
      /Choose a document to upload/i,
    ) as HTMLInputElement;
    await user.upload(input, file);

    // Request is in flight: the File must still be attached to the input.
    await waitFor(() =>
      expect(screen.getByRole('status')).toHaveTextContent(/Uploading/i),
    );
    expect(input.files).toHaveLength(1);

    releaseUpload?.();

    await waitFor(() =>
      expect(screen.getByRole('status')).toHaveTextContent(/is on the desk/i),
    );
    // Only now is it safe to reset the input.
    expect(input.files).toHaveLength(0);
  });

  it('has no detectable accessibility violations', async () => {
    const { container } = renderWithProviders(<UploadScreen />);
    await screen.findByText(/Supported:/i);
    expect(await axe(container)).toHaveNoViolations();
  });
});
