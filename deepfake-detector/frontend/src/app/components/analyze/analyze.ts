import { Component, OnInit, signal, computed } from '@angular/core';
import { Router } from '@angular/router';
import { FileUploadComponent } from '../file-upload/file-upload';
import { ApiService } from '../../services/api.services';
import { AnalysisStateService } from '../../services/analysis-state.service';
import { ToastService } from '../../services/toast.service';
import { AnalysisResult, ModelInfo, UploadedFile } from '../../models/analysis-result.model';

@Component({
  selector: 'app-analyze',
  standalone: true,
  imports: [FileUploadComponent],
  templateUrl: './analyze.html',
  styleUrl: './analyze.css',
})
export class AnalyzeComponent implements OnInit {
  selectedFile = signal<UploadedFile | null>(null);
  isLoading = signal(false);
  errorMessage = signal<string | null>(null);
  currentStep = signal(0); // 0=idle, 1=uploading, 2=analyzing, 3=done

  private allModels = signal<ModelInfo[]>([]);
  private stepTimer: ReturnType<typeof setTimeout> | null = null;

  rankedModels = computed<ModelInfo[]>(() => {
    const file = this.selectedFile();
    const models = this.allModels();

    if (!file || models.length === 0) return [];

    return models.filter(model => {
      if (file.type === 'image') {
        return model.key !== 'videomae_ffpp_c23';
      }

      if (file.type === 'video') {
        return model.key === 'videomae_ffpp_c23';
      }

      return false;
    });
  });

  constructor(
    private apiService: ApiService,
    private stateService: AnalysisStateService,
    private toastService: ToastService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.apiService.getModels().subscribe({
      next: (res) => this.allModels.set(res.available_models),
      error: () => { /* non-critical, rankings just won't display */ },
    });
  }

  onFileSelected(file: File): void {
    this.errorMessage.set(null);
    const type: 'image' | 'video' = file.type.startsWith('image/') ? 'image' : 'video';
    const preview_url = URL.createObjectURL(file);
    this.selectedFile.set({ file, preview_url, type });
  }

  onValidationError(msg: string): void {
    this.toastService.error(msg);
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

  stars(rank: number | null | undefined): number[] {
    const safeRank = Math.max(0, Math.floor(rank ?? 0));
    return Array.from({ length: safeRank });
  }

  emptyStars(rank: number | null | undefined): number[] {
    const safeRank = Math.max(0, Math.min(5, Math.floor(rank ?? 0)));
    return Array.from({ length: 5 - safeRank });
  }

  rankBadgeClass(rank: number): string {
    const base = 'shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold';
    switch (rank) {
      case 1: return `${base} bg-yellow-500 text-yellow-900`;
      case 2: return `${base} bg-gray-400 text-gray-900`;
      case 3: return `${base} bg-amber-700 text-amber-100`;
      default: return `${base} bg-gray-600 text-gray-300`;
    }
  }

  private startSteps() {
    this.currentStep.set(1);
    this.stepTimer = setTimeout(() => {
      this.currentStep.set(2);
    }, 900);
  }

  private finishSteps() {
    if (this.stepTimer) clearTimeout(this.stepTimer);
    this.currentStep.set(3);
  }

  private resetSteps() {
    if (this.stepTimer) clearTimeout(this.stepTimer);
    this.currentStep.set(0);
  }

  submit(): void {
    const uploaded = this.selectedFile();
    if (!uploaded || this.isLoading()) return;

    this.isLoading.set(true);
    this.errorMessage.set(null);
    this.startSteps();

    this.apiService.uploadFile(uploaded.file).subscribe({
      next: (result) => {
        this.finishSteps();
        const mapped = this.mapApiResponse(result);
        this.stateService.setResult(mapped, uploaded);
        this.isLoading.set(false);
        setTimeout(() => this.router.navigate(['/results']), 400);
      },
      error: (err) => {
        this.resetSteps();
        this.isLoading.set(false);
        const msg =
          err?.error?.detail ?? err?.message ?? 'Došlo je do greške. Pokušajte ponovo.';
        this.errorMessage.set(msg);
        this.toastService.error(msg);
      },
    });
  }

  private mapApiResponse(api: any): AnalysisResult {
    const deepfakeProb =
      api.analysis?.deepfake_probability ??
      api.deepfake_probability ??
      0;

    const confidence = +(deepfakeProb * 100).toFixed(1);

    let label: 'authentic' | 'suspicious' | 'deepfake';

    if (confidence < 40) {
      label = 'authentic';
    } else if (confidence < 70) {
      label = 'suspicious';
    } else {
      label = 'deepfake';
    }

    return {
      filename: api.filename ?? '',
      media_type: api.media_type ?? 'image',
      analysis_mode: api.analysis_mode ?? 'ensemble',
      models_used:
        api.analysis?.models_used ??
        api.models_used ??
        api.analysis?.model_results?.length ??
        0,

      is_deepfake: label === 'deepfake',
      is_suspicious: label === 'suspicious',
      label,

      deepfake_probability: deepfakeProb,
      confidence_percent: confidence,

      analysis: {
        label,
        deepfake_probability: deepfakeProb,
        confidence_percent: confidence,

        models_used:
          api.analysis?.models_used ??
          api.analysis?.model_results?.length ??
          0,

        model_results: api.analysis?.model_results ?? [],

        explanation:
          api.analysis?.explanation ??
          'Analiza završena bez dodatnog objašnjenja.',

        frames_analyzed:
          api.analysis?.frames_analyzed ??
          api.analysis?.frame_count,

        deepfake_frame_count:
          api.analysis?.deepfake_frame_count ??
          api.analysis?.suspicious_frames,

        suspicious_frame_count:
          api.analysis?.suspicious_frame_count
      }
    };
  }
}
