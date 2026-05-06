import { Component, OnInit, signal } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { Router } from '@angular/router';
import { AnalysisStateService } from '../../services/analysis-state.service';
import { HistoryService } from '../../services/history.service';
import { ToastService } from '../../services/toast.service';
import { AnalysisResult, ModelResult, UploadedFile } from '../../models/analysis-result.model';
import { ConfidenceMeterComponent } from '../confidence-meter/confidence-meter';

@Component({
  selector: 'app-results',
  standalone: true,
  imports: [ConfidenceMeterComponent, DecimalPipe],
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

    this.historyService.save({
      verdict: this.verdictLabel,
      confidence: this.result.confidence_percent,
      media_type: this.result.media_type,
      model_used: 'Ensemble (4 modela)',
      explanation: this.result.analysis.explanation,
      fileName: this.file?.file.name ?? 'Nepoznata datoteka',
    });

    this.toastService.success('Analiza završena!');
  }

  get verdictLabel(): 'REAL' | 'DEEPFAKE' {
    return this.result?.label === 'authentic' ? 'REAL' : 'DEEPFAKE';
  }

  get modelResults(): ModelResult[] {
    return this.result?.analysis.model_results ?? [];
  }

  get verdictReasoning(): string {
    if (!this.result) return '';
    const models = this.modelResults.filter(m => m.label !== 'error');
    const n = models.length;
    if (n === 0) return this.result.analysis.explanation;

    const deepfakeVotes = models.filter(m => m.label === 'deepfake').length;
    const suspiciousVotes = models.filter(m => m.label === 'suspicious').length;
    const authenticVotes = models.filter(m => m.label === 'authentic').length;
    const conf = this.result.confidence_percent;
    const faceDetected = models.some(m => m.face_detected === true);

    let text: string;
    if (this.result.label === 'deepfake') {
      text = `${deepfakeVotes} od ${n} modela klasificira sadržaj kao deepfake`;
      if (suspiciousVotes > 0) text += `, a još ${suspiciousVotes} kao sumnjiv`;
      text += `. Ensemble pouzdanost: ${conf.toFixed(1)}%.`;
    } else if (this.result.label === 'suspicious') {
      text = `Modeli su podijeljeni: ${deepfakeVotes} × deepfake, ${suspiciousVotes} × sumnjivo, ${authenticVotes} × autentično. Ensemble nije dostigao prag za sigurnu klasifikaciju (${conf.toFixed(1)}%).`;
    } else {
      text = `${authenticVotes} od ${n} modela klasificira sadržaj kao autentičan`;
      if (deepfakeVotes > 0) text += ` (${deepfakeVotes} modela ipak uočava sumnjive elemente)`;
      text += `. Ensemble pouzdanost: ${conf.toFixed(1)}%.`;
    }

    if (faceDetected) {
      text += ' Lice je uspješno detektirano i izrezirano za precizniju analizu.';
    }

    return text;
  }

  get confidenceInterpretation(): string {
    const score = this.result?.confidence_percent ?? 0;
    if (score < 40) {
      return `Model procjenjuje da je sadržaj AUTENTIČAN (${score.toFixed(1)}%).`;
    }
    if (score < 70) {
      return `Model nije siguran – sadržaj je SUMNJIV (${score.toFixed(1)}%). Preporučuje se dodatna provjera.`;
    }
    return `Model detektira visoku vjerojatnost manipulacije (${score.toFixed(1)}%).`;
  }

  modelCardBorderClass(label: string): string {
    switch (label) {
      case 'deepfake':   return 'border-red-600 bg-gray-800';
      case 'suspicious': return 'border-orange-500 bg-gray-800';
      case 'authentic':  return 'border-green-600 bg-gray-800';
      default:           return 'border-gray-600 bg-gray-800';
    }
  }

  modelLabelText(label: string): string {
    switch (label) {
      case 'deepfake':   return 'DEEPFAKE';
      case 'suspicious': return 'SUMNJIVO';
      case 'authentic':  return 'AUTENTIČAN';
      default:           return 'GREŠKA';
    }
  }

  modelLabelClass(label: string): string {
    switch (label) {
      case 'deepfake':   return 'bg-red-900 text-red-300';
      case 'suspicious': return 'bg-orange-900 text-orange-300';
      case 'authentic':  return 'bg-green-900 text-green-300';
      default:           return 'bg-gray-700 text-gray-400';
    }
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
      `Verdict:       ${this.verdictLabel === 'REAL' ? 'AUTENTIČAN' : 'DEEPFAKE'}`,
      `Pouzdanost:    ${this.result.confidence_percent.toFixed(1)}%`,
      `Tip medija:    ${this.result.media_type === 'image' ? 'Slika' : 'Video'}`,
      `Korišteni modeli: Ensemble (4 modela)`,
      `Datum analize: ${now}`,
      '',
      'Obrazloženje:',
      this.result.analysis.explanation,
    ].join('\n');

    navigator.clipboard.writeText(text).then(() => {
      this.copied.set(true);
      this.toastService.success('Rezultat kopiran u međuspremnik!');
      setTimeout(() => this.copied.set(false), 2000);
    }).catch(() => {
      this.toastService.error('Kopiranje nije uspjelo. Pokušajte ručno.');
    });
  }

  getModelDeepfakePercent(model: ModelResult): number {
     return Number(((model.deepfake_probability ?? 0) * 100).toFixed(2));
  }

  getModelDerivedLabel(model: ModelResult): 'authentic' | 'suspicious' | 'deepfake' | 'error' {
    const p = model.deepfake_probability;

    if (p === null || p === undefined) return 'error';

    const score = p * 100;

    if (score < 40) return 'authentic';
    if (score < 70) return 'suspicious';
    return 'deepfake';
  }
}
