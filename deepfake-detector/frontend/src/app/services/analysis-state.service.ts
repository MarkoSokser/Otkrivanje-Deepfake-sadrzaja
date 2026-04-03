import { Injectable, signal } from '@angular/core';
import { AnalysisResult, UploadedFile } from '../models/analysis-result.model';

@Injectable({ providedIn: 'root' })
export class AnalysisStateService {
  private _result = signal<AnalysisResult | null>(null);
  private _file = signal<UploadedFile | null>(null);

  setResult(result: AnalysisResult, file: UploadedFile): void {
    this._result.set(result);
    this._file.set(file);
  }

  getResult(): AnalysisResult | null {
    return this._result();
  }

  getFile(): UploadedFile | null {
    return this._file();
  }

  clear(): void {
    const file = this._file();
    if (file?.preview_url) {
      URL.revokeObjectURL(file.preview_url);
    }
    this._result.set(null);
    this._file.set(null);
  }
}
