import { Component, OnInit, signal } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { AnalysisStateService } from '../../services/analysis-state.service';
import { HistoryService } from '../../services/history.service';
import { ToastService } from '../../services/toast.service';
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
  copied = signal(false);

  constructor(
    private stateService: AnalysisStateService,
    private historyService: HistoryService,
    private toastService: ToastService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.result = this.stateService.getResult();
    this.file = this.stateService.getFile();
    if (!this.result) {
      this.router.navigate(['/analyze']);
      return;
    }

    // Save to history
    this.historyService.save({
      verdict: this.result.verdict,
      confidence: this.result.confidence,
      media_type: this.result.media_type,
      model_used: this.result.model_used,
      explanation: this.result.explanation,
      fileName: this.file?.file.name ?? 'Nepoznata datoteka',
    });

    this.toastService.success('Analiza završena!');
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

  copyResult(): void {
    if (!this.result) return;
    const now = new Date().toLocaleString('hr-HR', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
    const text = [
      'DeepfakeDetector – Rezultat analize',
      '=====================================',
      `Verdict:       ${this.result.verdict === 'REAL' ? 'AUTENTIČAN' : 'DEEPFAKE'}`,
      `Pouzdanost:    ${this.result.confidence.toFixed(1)}%`,
      `Tip medija:    ${this.result.media_type === 'image' ? 'Slika' : 'Video'}`,
      `Korišteni model: ${this.result.model_used}`,
      `Datum analize: ${now}`,
      '',
      'Obrazloženje:',
      this.result.explanation,
    ].join('\n');

    navigator.clipboard.writeText(text).then(() => {
      this.copied.set(true);
      this.toastService.success('Rezultat kopiran u međuspremnik!');
      setTimeout(() => this.copied.set(false), 2000);
    }).catch(() => {
      this.toastService.error('Kopiranje nije uspjelo. Pokušajte ručno.');
    });
  }
}
