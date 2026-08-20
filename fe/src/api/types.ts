/**
 * Types mirroring the Divergentia Flask API contract.
 * Verified live against the running backend.
 */

export interface OllamaStatus {
  available: boolean;
  status: string;
  model: string;
  base_url: string;
}

export interface HealthResponse {
  status: string;
  api_version: string;
  ollama_status: OllamaStatus;
}

export interface FormatOptionDetail {
  description: string;
  type: string;
  examples?: string[];
}

export interface FormatDetail {
  format: string;
  option_details: Record<string, FormatOptionDetail>;
}

export interface SupportedFormatsResponse {
  supported_formats: string[];
  format_details: Record<string, FormatDetail>;
  /** Maximum accepted upload size, in bytes. */
  max_upload_size_bytes?: number;
  /** Maximum accepted upload size, in megabytes (rounded, for display). */
  max_upload_size_mb?: number;
}

export interface UploadResponse {
  document_id: string;
  original_filename: string;
  file_size: number;
  mime_type: string;
  file_extension: string;
  message: string;
}

/** Common shape returned by document-processing endpoints (chained edits). */
export interface ProcessResult {
  success: boolean;
  document_id: string;
  filename: string;
  download_url: string;
  format: string;
  note?: string;
  [key: string]: unknown;
}

export interface PreviewResponse {
  document_id: string;
  original_filename: string;
  file_size: number;
  file_extension: string;
  text_preview: string;
  character_count: number;
  word_count: number;
}

export interface ExtractTextResponse {
  document_id: string;
  text_content: string;
  character_count: number;
  word_count: number;
}

// ---- Request option payloads (mirror the pydantic schemas) ----

export interface ThemeColors {
  positive?: string;
  negative?: string;
  scheme?: 'complementary' | 'triadic' | 'tetradic' | 'even' | 'analogous';
}

export interface FormattingOptions {
  titles?: boolean;
  section_titles?: boolean;
  paragraphs_titles?: boolean;
  paragraphs?: boolean;
  captions?: boolean;
  bibliography?: boolean;
  font_name?: string;
  font_size?: number;
  font_color?: string;
  bold?: boolean;
  italic?: boolean;
  alignment?: 'left' | 'center' | 'right' | 'justify';
  theme?: ThemeColors;
  from_original?: boolean;
}

export interface FramingOptions {
  sections?: boolean;
  paragraphs?: boolean;
  subparagraphs?: boolean;
  sentences?: boolean;
  use_tables?: boolean;
  border_style?: string;
  border_width?: number;
  border_color?: string;
  cell_margin?: number;
  preserve_spacing?: boolean;
  from_original?: boolean;
}

export interface SpacingOptions {
  paragraphs?: boolean;
  sentences?: boolean;
  from_original?: boolean;
}

export interface KeywordOptions {
  max_keywords?: number;
  include_proper_nouns?: boolean;
  model?: string;
  from_original?: boolean;
}

export interface HighlightingOptions {
  enabled: boolean;
  color?: string;
  style?: string;
  font_size?: number;
  font_family?: string;
  nouns?: boolean;
  verbs?: boolean;
  adjectives?: boolean;
  adverbs?: boolean;
  from_original?: boolean;
}

export type SummaryType = 'brief' | 'detailed' | 'executive';
export type ParaphraseStyle = 'casual' | 'professional' | 'simple';

export interface SummarizeResponse {
  document_id: string;
  document_name?: string;
  summary: string;
  key_points?: string[];
  summary_type?: string;
  original_length?: number;
  summary_length?: number;
  compression_ratio?: number;
  added_to_document?: boolean;
  download_url?: string;
  filename?: string;
}

export interface ParaphraseResponse {
  document_id: string;
  document_name?: string;
  style: string;
  total_sections?: number;
  paraphrased_sections?: Record<string, string>;
  applied_to_document?: boolean;
  download_url?: string;
  filename?: string;
}

export interface TextSummarizeResponse {
  summary: string;
  original_length: number;
  summary_length: number;
}

export interface TextParaphraseResponse {
  paraphrased_text: string;
  style: string;
  original_length: number;
  paraphrased_length: number;
}
