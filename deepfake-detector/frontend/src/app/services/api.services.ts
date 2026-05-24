import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AnalysisResult, ModelInfo } from '../models/analysis-result.model';

export interface ModelsResponse {
  analysis_mode: string;
  description: string;
  available_models: ModelInfo[];
  supported_formats: string[];
}

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private apiUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  uploadFile(file: File): Observable<AnalysisResult> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<AnalysisResult>(`${this.apiUrl}/analyze`, formData);
  }

  getHealth(): Observable<{ status: string }> {
    return this.http.get<{ status: string }>(`${this.apiUrl}/health`);
  }

  getModels(): Observable<ModelsResponse> {
    return this.http.get<ModelsResponse>(`${this.apiUrl}/models`);
  }
}
