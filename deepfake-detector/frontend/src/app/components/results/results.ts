import { Component, OnInit } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { AnalysisStateService } from '../../services/analysis-state.service';
import { AnalysisResult, UploadedFile } from '../../models/analysis-result.model';
import { ConfidenceMeterComponent } from '../confidence-meter/confidence-meter';

@Component({
  selector: 'app-results',
  standalone: true,
  imports: [RouterLink, ConfidenceMeterComponent, DecimalPipe],
  templateUrl: './results.html',
  styleUrl: './results.css',
})
export class ResultsComponent implements OnInit {
  result: AnalysisResult | null = null;
  file: UploadedFile | null = null;

  constructor(
    private stateService: AnalysisStateService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.result = this.stateService.getResult();
    this.file = this.stateService.getFile();
    if (!this.result) {
      this.router.navigate(['/analyze']);
    }
  }

  get confidenceInterpretation(): string {
    const c = this.result?.confidence ?? 0;
    if (c <= 40) return 'Model je s visokom sigurnošću klasificirao ovaj sadržaj kao autentičan.';
    if (c <= 70) return 'Model nije u potpunosti siguran u klasifikaciju. Sadržaj zahtijeva dodatnu provjeru.';
    return 'Model je s visokom sigurnošću otkrio znakove manipulacije u sadržaju.';
  }

  formatFileSize(bytes: number): string {
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  analyzeNew(): void {
    this.stateService.clear();
    this.router.navigate(['/analyze']);
  }
}
