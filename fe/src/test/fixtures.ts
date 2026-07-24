import type {
  HealthResponse,
  SupportedFormatsResponse,
  UploadResponse,
} from '../api/types';

export const healthFixture: HealthResponse = {
  status: 'healthy',
  api_version: '1.0.0',
  ollama_status: {
    available: true,
    status: 'healthy',
    model: 'llama3.2:latest',
    base_url: 'http://localhost:11434',
  },
};

export const formatsFixture: SupportedFormatsResponse = {
  supported_formats: ['pdf', 'docx', 'doc', 'txt'],
  format_details: {
    txt: { format: 'txt', option_details: {} },
  },
};

export const uploadFixture: UploadResponse = {
  document_id: '536df518-ab15-4742-9dfd-520819398931',
  original_filename: 'sample.txt',
  file_size: 54,
  mime_type: 'text/plain',
  file_extension: 'txt',
  message: 'Document uploaded successfully',
};

export const previewFixture = {
  document_id: uploadFixture.document_id,
  original_filename: 'sample.txt',
  file_size: 54,
  file_extension: 'txt',
  text_preview: 'Hello Divergentia. This is a preview of the document text.',
  character_count: 57,
  word_count: 9,
};

export const processResultFixture = {
  success: true,
  document_id: uploadFixture.document_id,
  filename: 'edited_sample.docx',
  download_url: `/api/documents/${uploadFixture.document_id}/download`,
  format: 'docx',
};
