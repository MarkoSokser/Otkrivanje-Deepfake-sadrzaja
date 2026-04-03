import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AnalysisResult } from '../models/analysis-result.model';

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

  getModels(): Observable<{ models: string[] }> {
    return this.http.get<{ models: string[] }>(`${this.apiUrl}/models`);
  }
}