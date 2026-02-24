# Angular Integration Guide

This guide shows how to integrate the Divergentia API with an Angular frontend.

## Setup

### 1. Install Angular HTTP Client

```bash
# Already included in Angular core
```

### 2. Configure Environment

```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:5000/api'
};

// src/environments/environment.prod.ts
export const environment = {
  production: true,
  apiUrl: 'https://your-production-api.com/api'
};
```

## TypeScript Interfaces

```typescript
// src/app/models/document.model.ts

export interface DocumentUploadResponse {
  document_id: string;
  original_filename: string;
  file_size: number;
  mime_type: string;
  file_extension: string;
  message: string;
}

export interface TextExtractionResponse {
  document_id: string;
  text_content: string;
  character_count: number;
  word_count: number;
}

export interface FormattingOptions {
  font_name?: string;
  font_size?: number;
  font_color?: string;
  bold?: boolean;
  italic?: boolean;
  alignment?: 'left' | 'center' | 'right' | 'justify';
}

export interface FramingOptions {
  sections: boolean;
  paragraphs: boolean;
  subparagraphs: boolean;
  sentences: boolean;
}

export interface FramingRequest {
  framing: FramingOptions;
}

export interface FormattingResponse {
  success: boolean;
  output_path: string;
  format: string;
  message?: string;
  applied_options?: FormattingOptions;
  borders_applied?: number;
  framing_options?: FramingOptions;
}

export interface SummaryResponse {
  document_id: string;
  document_name: string;
  summary: string;
  key_points: string[];
  summary_type: string;
  original_length: number;
  summary_length: number;
  compression_ratio: number;
}

export interface ParaphraseResponse {
  document_id: string;
  document_name: string;
  style: string;
  total_sections: number;
  paraphrased_sections: { [key: number]: string };
}

export interface ApiError {
  error: string;
  message: string;
  status_code: number;
  details?: any;
}
```

## Document Service

```typescript
// src/app/services/document.service.ts

import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpEvent, HttpEventType } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import {
  DocumentUploadResponse,
  TextExtractionResponse,
  FormattingOptions,
  FormattingResponse,
  SummaryResponse,
  ParaphraseResponse,
  ApiError
} from '../models/document.model';

@Injectable({
  providedIn: 'root'
})
export class DocumentService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  /**
   * Upload a document
   */
  uploadDocument(file: File): Observable<DocumentUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post<DocumentUploadResponse>(
      `${this.apiUrl}/documents/upload`,
      formData
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Upload with progress tracking
   */
  uploadDocumentWithProgress(file: File): Observable<number | DocumentUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post<DocumentUploadResponse>(
      `${this.apiUrl}/documents/upload`,
      formData,
      {
        reportProgress: true,
        observe: 'events'
      }
    ).pipe(
      map(event => {
        if (event.type === HttpEventType.UploadProgress) {
          const progress = Math.round(100 * event.loaded / event.total!);
          return progress;
        } else if (event.type === HttpEventType.Response) {
          return event.body!;
        }
        return 0;
      }),
      catchError(this.handleError)
    );
  }

  /**
   * Extract text from document
   */
  extractText(documentId: string): Observable<TextExtractionResponse> {
    return this.http.post<TextExtractionResponse>(
      `${this.apiUrl}/documents/${documentId}/extract-text`,
      {}
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Apply formatting to document (Legacy - for font formatting)
   * Note: The current API uses this endpoint for framing. 
   * This method is kept for reference but should use applyFraming() instead.
   */
  applyFormatting(documentId: string, options: FormattingOptions): Observable<FormattingResponse> {
    return this.http.put<FormattingResponse>(
      `${this.apiUrl}/documents/${documentId}/format`,
      options
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Apply framing (borders) to document parts
   */
  applyFraming(documentId: string, framingOptions: FramingOptions): Observable<FormattingResponse> {
    const request: FramingRequest = { framing: framingOptions };
    
    return this.http.put<FormattingResponse>(
      `${this.apiUrl}/documents/${documentId}/format`,
      request
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Get available styles for document
   */
  getDocumentStyles(documentId: string): Observable<any> {
    return this.http.get(
      `${this.apiUrl}/documents/${documentId}/styles`
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Summarize document
   */
  summarizeDocument(
    documentId: string,
    summaryType: 'brief' | 'detailed' | 'executive' = 'brief'
  ): Observable<SummaryResponse> {
    return this.http.post<SummaryResponse>(
      `${this.apiUrl}/documents/${documentId}/summarize`,
      { summary_type: summaryType }
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Paraphrase document
   */
  paraphraseDocument(
    documentId: string,
    style: 'formal' | 'casual' | 'professional' | 'simple' = 'formal',
    sections?: number[]
  ): Observable<ParaphraseResponse> {
    const body: any = { style };
    if (sections) {
      body.sections = sections;
    }

    return this.http.post<ParaphraseResponse>(
      `${this.apiUrl}/documents/${documentId}/paraphrase`,
      body
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Summarize text directly
   */
  summarizeText(text: string, maxLength: number = 500): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/text/summarize`,
      { text, max_length: maxLength }
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Paraphrase text directly
   */
  paraphraseText(
    text: string,
    style: 'formal' | 'casual' | 'professional' | 'simple' = 'formal'
  ): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/text/paraphrase`,
      { text, style }
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Download document
   */
  downloadDocument(documentId: string): Observable<Blob> {
    return this.http.get(
      `${this.apiUrl}/documents/${documentId}/download`,
      { responseType: 'blob' }
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Get document preview
   */
  getDocumentPreview(documentId: string): Observable<any> {
    return this.http.get(
      `${this.apiUrl}/documents/${documentId}/preview`
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Check API health
   */
  healthCheck(): Observable<any> {
    return this.http.get(`${this.apiUrl}/health`).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Get supported formats
   */
  getSupportedFormats(): Observable<any> {
    return this.http.get(`${this.apiUrl}/formats/supported`).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Handle HTTP errors
   */
  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'An error occurred';

    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Server-side error
      const apiError = error.error as ApiError;
      errorMessage = apiError?.message || `Error Code: ${error.status}\nMessage: ${error.message}`;
    }

    console.error(errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}
```

## Component Example

```typescript
// src/app/components/document-upload/document-upload.component.ts

import { Component } from '@angular/core';
import { DocumentService } from '../../services/document.service';

@Component({
  selector: 'app-document-upload',
  templateUrl: './document-upload.component.html',
  styleUrls: ['./document-upload.component.css']
})
export class DocumentUploadComponent {
  selectedFile: File | null = null;
  uploadProgress: number = 0;
  uploadedDocumentId: string | null = null;
  isUploading: boolean = false;
  error: string | null = null;

  constructor(private documentService: DocumentService) {}

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
    this.error = null;
  }

  uploadDocument() {
    if (!this.selectedFile) {
      this.error = 'Please select a file';
      return;
    }

    this.isUploading = true;
    this.uploadProgress = 0;

    this.documentService.uploadDocumentWithProgress(this.selectedFile).subscribe({
      next: (result) => {
        if (typeof result === 'number') {
          // Progress update
          this.uploadProgress = result;
        } else {
          // Upload complete
          this.uploadedDocumentId = result.document_id;
          this.isUploading = false;
          console.log('Upload complete:', result);
        }
      },
      error: (error) => {
        this.error = error.message;
        this.isUploading = false;
      }
    });
  }

  summarizeDocument() {
    if (!this.uploadedDocumentId) return;

    this.documentService.summarizeDocument(this.uploadedDocumentId, 'brief').subscribe({
      next: (summary) => {
        console.log('Summary:', summary);
      },
      error: (error) => {
        this.error = error.message;
      }
    });
  }
}
```

## Template Example

```html
<!-- src/app/components/document-upload/document-upload.component.html -->

<div class="upload-container">
  <h2>Upload Document</h2>

  <div class="file-input">
    <input 
      type="file" 
      (change)="onFileSelected($event)"
      accept=".pdf,.docx,.doc,.txt,.rtf"
    >
  </div>

  <button 
    (click)="uploadDocument()" 
    [disabled]="!selectedFile || isUploading"
  >
    Upload
  </button>

  <div *ngIf="isUploading" class="progress">
    <div class="progress-bar" [style.width.%]="uploadProgress">
      {{ uploadProgress }}%
    </div>
  </div>

  <div *ngIf="error" class="error">
    {{ error }}
  </div>

  <div *ngIf="uploadedDocumentId" class="success">
    <p>Document uploaded successfully!</p>
    <button (click)="summarizeDocument()">Summarize</button>
  </div>
</div>
```

## HTTP Interceptor for Error Handling

```typescript
// src/app/interceptors/error.interceptor.ts

import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { Router } from '@angular/router';

@Injectable()
export class ErrorInterceptor implements HttpInterceptor {
  constructor(private router: Router) {}

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(request).pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 401) {
          // Handle unauthorized
          this.router.navigate(['/login']);
        } else if (error.status === 429) {
          // Handle rate limit
          alert('Too many requests. Please try again later.');
        }
        
        return throwError(() => error);
      })
    );
  }
}
```

## Module Configuration

```typescript
// src/app/app.module.ts

import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';

import { AppComponent } from './app.component';
import { DocumentUploadComponent } from './components/document-upload/document-upload.component';
import { DocumentService } from './services/document.service';
import { ErrorInterceptor } from './interceptors/error.interceptor';

@NgModule({
  declarations: [
    AppComponent,
    DocumentUploadComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule
  ],
  providers: [
    DocumentService,
    {
      provide: HTTP_INTERCEPTORS,
      useClass: ErrorInterceptor,
      multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
```

## Best Practices

1. **Error Handling**: Always handle errors in subscriptions
2. **Unsubscribe**: Use `takeUntil` or `async` pipe to prevent memory leaks
3. **Loading States**: Show loading indicators during API calls
4. **Type Safety**: Use TypeScript interfaces for all API responses
5. **Environment Config**: Use Angular environment files for API URLs
6. **Interceptors**: Use HTTP interceptors for global error handling
7. **File Validation**: Validate files before upload (size, type)
8. **Progress Tracking**: Show upload progress for large files

## Testing

```typescript
// document.service.spec.ts

import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { DocumentService } from './document.service';

describe('DocumentService', () => {
  let service: DocumentService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [DocumentService]
    });
    service = TestBed.inject(DocumentService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  it('should upload document', () => {
    const mockFile = new File(['content'], 'test.txt', { type: 'text/plain' });
    const mockResponse = {
      document_id: '123',
      original_filename: 'test.txt',
      file_size: 100,
      mime_type: 'text/plain',
      file_extension: 'txt',
      message: 'Success'
    };

    service.uploadDocument(mockFile).subscribe(response => {
      expect(response.document_id).toBe('123');
    });

    const req = httpMock.expectOne(`${service['apiUrl']}/documents/upload`);
    expect(req.request.method).toBe('POST');
    req.flush(mockResponse);
  });

  afterEach(() => {
    httpMock.verify();
  });
});
```

## Framing Feature Examples

### Component Example with Framing

```typescript
// src/app/components/document-framing/document-framing.component.ts

import { Component } from '@angular/core';
import { DocumentService } from '../../services/document.service';
import { FramingOptions } from '../../models/document.model';

@Component({
  selector: 'app-document-framing',
  templateUrl: './document-framing.component.html',
  styleUrls: ['./document-framing.component.css']
})
export class DocumentFramingComponent {
  documentId: string | null = null;
  uploadProgress: number = 0;
  isProcessing: boolean = false;
  resultMessage: string = '';
  
  framingOptions: FramingOptions = {
    sections: false,
    paragraphs: false,
    subparagraphs: false,
    sentences: false
  };

  constructor(private documentService: DocumentService) {}

  onFileSelected(event: any): void {
    const file: File = event.target.files[0];
    if (!file) return;

    this.isProcessing = true;
    this.uploadProgress = 0;

    this.documentService.uploadDocumentWithProgress(file).subscribe({
      next: (result) => {
        if (typeof result === 'number') {
          this.uploadProgress = result;
        } else {
          this.documentId = result.document_id;
          this.resultMessage = `Document uploaded: ${result.original_filename}`;
          this.isProcessing = false;
        }
      },
      error: (error) => {
        console.error('Upload failed:', error);
        this.resultMessage = `Error: ${error.message}`;
        this.isProcessing = false;
      }
    });
  }

  applyFraming(): void {
    if (!this.documentId) {
      this.resultMessage = 'Please upload a document first';
      return;
    }

    // Check if at least one option is selected
    const hasSelection = Object.values(this.framingOptions).some(v => v);
    if (!hasSelection) {
      this.resultMessage = 'Please select at least one framing option';
      return;
    }

    this.isProcessing = true;
    this.resultMessage = 'Applying borders...';

    this.documentService.applyFraming(this.documentId, this.framingOptions).subscribe({
      next: (response) => {
        this.resultMessage = `Success! ${response.borders_applied} borders applied.`;
        this.isProcessing = false;
      },
      error: (error) => {
        console.error('Framing failed:', error);
        this.resultMessage = `Error: ${error.message}`;
        this.isProcessing = false;
      }
    });
  }

  downloadDocument(): void {
    if (!this.documentId) return;
    
    const url = `${this.documentService['apiUrl']}/documents/${this.documentId}/download`;
    window.open(url, '_blank');
  }

  reset(): void {
    this.documentId = null;
    this.uploadProgress = 0;
    this.resultMessage = '';
    this.framingOptions = {
      sections: false,
      paragraphs: false,
      subparagraphs: false,
      sentences: false
    };
  }
}
```

### Template Example

```html
<!-- src/app/components/document-framing/document-framing.component.html -->

<div class="framing-container">
  <h2>Document Framing</h2>

  <!-- File Upload -->
  <div class="upload-section">
    <input 
      type="file" 
      (change)="onFileSelected($event)"
      accept=".docx,.pdf,.txt"
      [disabled]="isProcessing"
    >
    
    <div *ngIf="uploadProgress > 0 && uploadProgress < 100" class="progress-bar">
      <div class="progress-fill" [style.width.%]="uploadProgress"></div>
      <span>{{ uploadProgress }}%</span>
    </div>
  </div>

  <!-- Framing Options -->
  <div class="framing-options" *ngIf="documentId">
    <h3>Select Parts to Border:</h3>
    
    <div class="option">
      <label>
        <input 
          type="checkbox" 
          [(ngModel)]="framingOptions.sections"
          [disabled]="isProcessing"
        >
        Sections
        <span class="help-text">Groups starting with " A. ", " B. ", etc.</span>
      </label>
    </div>

    <div class="option">
      <label>
        <input 
          type="checkbox" 
          [(ngModel)]="framingOptions.paragraphs"
          [disabled]="isProcessing"
        >
        Paragraphs
        <span class="help-text">All non-empty paragraphs</span>
      </label>
    </div>

    <div class="option">
      <label>
        <input 
          type="checkbox" 
          [(ngModel)]="framingOptions.subparagraphs"
          [disabled]="isProcessing"
        >
        Subparagraphs
        <span class="help-text">Complex periods separated by ; or :</span>
      </label>
    </div>

    <div class="option">
      <label>
        <input 
          type="checkbox" 
          [(ngModel)]="framingOptions.sentences"
          [disabled]="isProcessing"
        >
        Sentences
        <span class="help-text">Individual sentences</span>
      </label>
    </div>

    <!-- Action Buttons -->
    <div class="actions">
      <button 
        (click)="applyFraming()" 
        [disabled]="isProcessing"
        class="btn-primary"
      >
        Apply Borders
      </button>

      <button 
        (click)="downloadDocument()" 
        [disabled]="!documentId || isProcessing"
        class="btn-secondary"
      >
        Download
      </button>

      <button 
        (click)="reset()"
        [disabled]="isProcessing"
        class="btn-link"
      >
        Reset
      </button>
    </div>
  </div>

  <!-- Result Message -->
  <div *ngIf="resultMessage" class="result-message" 
       [class.error]="resultMessage.startsWith('Error')">
    {{ resultMessage }}
  </div>

  <!-- Loading Indicator -->
  <div *ngIf="isProcessing" class="loading">
    <div class="spinner"></div>
    <p>Processing...</p>
  </div>
</div>
```

### Styles Example

```css
/* src/app/components/document-framing/document-framing.component.css */

.framing-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.upload-section {
  margin-bottom: 30px;
}

.progress-bar {
  width: 100%;
  height: 30px;
  background: #f0f0f0;
  border-radius: 5px;
  position: relative;
  margin-top: 10px;
}

.progress-fill {
  height: 100%;
  background: #4CAF50;
  border-radius: 5px;
  transition: width 0.3s;
}

.progress-bar span {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-weight: bold;
}

.framing-options {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
}

.option {
  margin-bottom: 15px;
}

.option label {
  display: flex;
  align-items: flex-start;
  cursor: pointer;
}

.option input[type="checkbox"] {
  margin-right: 10px;
  margin-top: 3px;
}

.help-text {
  display: block;
  font-size: 0.85em;
  color: #666;
  margin-left: 30px;
  margin-top: 5px;
}

.actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.btn-primary {
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-secondary {
  background: #28a745;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
}

.btn-link {
  background: transparent;
  color: #007bff;
  border: none;
  padding: 10px 20px;
  cursor: pointer;
  text-decoration: underline;
}

.result-message {
  margin-top: 20px;
  padding: 15px;
  border-radius: 5px;
  background: #d4edda;
  color: #155724;
}

.result-message.error {
  background: #f8d7da;
  color: #721c24;
}

.loading {
  text-align: center;
  margin-top: 20px;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

---

## Summary

The framing feature allows users to visually distinguish different parts of their documents by applying borders. This Angular integration provides:

- ✅ Type-safe interfaces for framing options
- ✅ Service methods for applying framing
- ✅ Complete component example with UI
- ✅ Progress tracking for uploads
- ✅ Error handling and user feedback

For more details, see:
- `FRAMING_FEATURE.md` - Complete feature documentation
- `QUICKSTART_FRAMING.md` - Quick start guide
- `FRAMING_IMPLEMENTATION.md` - Technical implementation details

