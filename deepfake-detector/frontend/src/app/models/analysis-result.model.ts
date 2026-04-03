export interface AnalysisResult {
  verdict: 'REAL' | 'DEEPFAKE';
  confidence: number; // 0–100
  media_type: 'image' | 'video';
  model_used: string;
  explanation: string;
  frame_count?: number;
  suspicious_frames?: number;
}

export interface UploadedFile {
  file: File;
  preview_url: string;
  type: 'image' | 'video';
}
