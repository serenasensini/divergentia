import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import type { UploadResponse } from '../api/types';

export interface AppliedStep {
  id: string;
  /** Station label, e.g. "Colour & style". */
  label: string;
  /** Short human summary of what was applied. */
  detail: string;
  at: number;
}

interface DocumentContextValue {
  documentId: string | null;
  documentName: string | null;
  fileExtension: string | null;
  steps: AppliedStep[];
  setDocument: (upload: UploadResponse) => void;
  addStep: (label: string, detail: string) => void;
  clearDocument: () => void;
  /** Reset the applied-steps timeline (used with the API's from_original). */
  resetSteps: () => void;
}

const DocumentContext = createContext<DocumentContextValue | null>(null);

let stepCounter = 0;

export function DocumentProvider({ children }: { children: ReactNode }) {
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [documentName, setDocumentName] = useState<string | null>(null);
  const [fileExtension, setFileExtension] = useState<string | null>(null);
  const [steps, setSteps] = useState<AppliedStep[]>([]);

  const setDocument = useCallback((upload: UploadResponse) => {
    setDocumentId(upload.document_id);
    setDocumentName(upload.original_filename);
    setFileExtension(upload.file_extension);
    setSteps([]);
  }, []);

  const addStep = useCallback((label: string, detail: string) => {
    setSteps((prev) => [
      ...prev,
      { id: `step-${++stepCounter}`, label, detail, at: Date.now() },
    ]);
  }, []);

  const clearDocument = useCallback(() => {
    setDocumentId(null);
    setDocumentName(null);
    setFileExtension(null);
    setSteps([]);
  }, []);

  const resetSteps = useCallback(() => setSteps([]), []);

  const value = useMemo(
    () => ({
      documentId,
      documentName,
      fileExtension,
      steps,
      setDocument,
      addStep,
      clearDocument,
      resetSteps,
    }),
    [
      documentId,
      documentName,
      fileExtension,
      steps,
      setDocument,
      addStep,
      clearDocument,
      resetSteps,
    ],
  );

  return (
    <DocumentContext.Provider value={value}>
      {children}
    </DocumentContext.Provider>
  );
}

export function useDocument(): DocumentContextValue {
  const ctx = useContext(DocumentContext);
  if (!ctx) {
    throw new Error('useDocument must be used within a DocumentProvider');
  }
  return ctx;
}
