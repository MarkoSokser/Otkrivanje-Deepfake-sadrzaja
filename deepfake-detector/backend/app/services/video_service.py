from pathlib import Path

import cv2

from app.services.video_model_service import analyze_video_with_videomae


def get_video_metadata(file_path: Path) -> dict:
    video = cv2.VideoCapture(str(file_path))

    if not video.isOpened():
        return {
            "total_frames": None,
            "fps": None,
            "duration_seconds": None,
            "width": None,
            "height": None
        }

    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = float(video.get(cv2.CAP_PROP_FPS))
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    video.release()

    duration_seconds = None

    if fps > 0 and total_frames > 0:
        duration_seconds = round(total_frames / fps, 2)

    return {
        "total_frames": total_frames,
        "fps": round(fps, 2) if fps else None,
        "duration_seconds": duration_seconds,
        "width": width,
        "height": height
    }


def analyze_video(file_path: Path) -> dict:
    metadata = get_video_metadata(file_path)

    if metadata["total_frames"] is None:
        return {
            "label": "error",
            "is_deepfake": None,
            "is_suspicious": None,
            "real_probability": None,
            "deepfake_probability": None,
            "confidence_percent": None,
            "models_used": 0,
            "model": "VideoMAE video-only analysis",
            "analysis_mode": "video_only_videomae",
            "video_metadata": metadata,
            "model_results": [],
            "explanation": "Video nije moguće otvoriti."
        }

    result = analyze_video_with_videomae(file_path)

    return {
        "label": result.get("label"),
        "is_deepfake": result.get("is_deepfake"),
        "is_suspicious": result.get("is_suspicious"),
        "real_probability": result.get("real_probability"),
        "deepfake_probability": result.get("deepfake_probability"),
        "confidence_percent": result.get("confidence_percent"),
        "models_used": result.get("models_used"),
        "model": "VideoMAE video-only analysis",
        "analysis_mode": "video_only_videomae",
        "video_metadata": metadata,
        "video_specific_result": result,
        "model_results": result.get("model_results", []),
        "explanation": result.get("explanation")
    }