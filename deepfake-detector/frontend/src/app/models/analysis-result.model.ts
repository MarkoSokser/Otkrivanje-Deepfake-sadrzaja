export interface ModelResult {
  label: 'deepfake' | 'suspicious' | 'authentic' | 'error';
  is_deepfake: boolean | null;
  is_suspicious: boolean | null;
  real_probability: number | null;
  deepfake_probability: number | null;
  confidence_percent: number | null;
  model_key: string;
  model: string;
  dataset: string;
  device: string;
  raw_predicted_label: string;
  face_detected: boolean | null;
  weight: number;
  explanation: string;
}

export interface AnalysisResult {
  filename: string;
  media_type: 'image' | 'video';
  analysis_mode: string;
  models_used: number;
  is_deepfake: boolean;
  is_suspicious: boolean;
  label: 'deepfake' | 'suspicious' | 'authentic';
  deepfake_probability: number;
  confidence_percent: number;
  analysis: {
    label: string;
    deepfake_probability: number;
    confidence_percent: number;
    models_used: number;
    model_results: ModelResult[];
    explanation: string;
    frames_analyzed?: number;
    deepfake_frame_count?: number;
    suspicious_frame_count?: number;
  };
}

export interface ModelInfo {
  key: string;
  name: string;
  dataset: string;
  description: string;
  image_rank: number;
  video_rank: number;
  image_rank_reason: string;
  video_rank_reason: string;
}

export interface UploadedFile {
  file: File;
  preview_url: string;
  type: 'image' | 'video';
}
