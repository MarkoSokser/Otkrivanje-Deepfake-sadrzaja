import { Component, signal } from '@angular/core';
import { Router } from '@angular/router';
import { FileUploadComponent } from '../file-upload/file-upload';
import { ApiService } from '../../services/api.services';
import { AnalysisStateService } from '../../services/analysis-state.service';
import { UploadedFile } from '../../models/analysis-result.model';

@Component({
  selector: 'app-analyze',
  standalone: true,
  imports: [FileUploadComponent],
  templateUrl: './analyze.html',
  styleUrl: './analyze.css',
})
export class AnalyzeComponent {
  selectedFile = signal<UploadedFile | null>(null);
  isLoading = signal(false);
  errorMessage = signal<string | null>(null);

  constructor(
    private apiService: ApiService,
    private stateService: AnalysisStateService,
    private router: Router,
  ) {}

  onFileSelected(file: File): void {
    this.errorMessage.set(null);
    const type: 'image' | 'video' = file.type.startsWith('image/') ? 'image' : 'video';
    const preview_url = type === 'image' ? URL.createObjectURL(file) : URL.createObjectURL(file);
    this.selectedFile.set({ file, preview_url, type });
  }

  onValidationError(msg: string): void {
    this.errorMessage.set(msg);
  }

  removeFile(): void {
    const f = this.selectedFile();
    if (f?.preview_url) {
      URL.revokeObjectURL(f.preview_url);
    }
    this.selectedFile.set(null);
    this.errorMessage.set(null);
  }

  formatFileSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  submit(): void {
    const uploaded = this.selectedFile();
    if (!uploaded || this.isLoading()) return;

    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.apiService.uploadFile(uploaded.file).subscribe({
      next: (result) => {
        this.stateService.setResult(result, uploaded);
        this.isLoading.set(false);
        this.router.navigate(['/results']);
      },
      error: (err) => {
        this.isLoading.set(false);
        const msg =
          err?.error?.detail ?? err?.message ?? 'Došlo je do greške. Pokušajte ponovo.';
        this.errorMessage.set(msg);
      },
    });
  }
}
