from pathlib import Path
import uuid

import cv2

from app.services.image_service import analyze_image, label_from_probability, confidence_from_label


MAX_FRAMES_TO_ANALYZE = 20

THRESHOLD_SUSPICIOUS = 0.55
THRESHOLD_DEEPFAKE = 0.75

DEEPFAKE_FRAME_RATIO_THRESHOLD = 0.30
SUSPICIOUS_FRAME_RATIO_THRESHOLD = 0.20
VERY_HIGH_FRAME_SCORE = 0.90
MIN_STRONG_DEEPFAKE_FRAMES = 4


def label_from_video_statistics(
    average_fake_probability: float,
    max_fake_probability: float,
    deepfake_frame_ratio: float,
    suspicious_frame_ratio: float,
    strong_deepfake_frame_count: int
) -> str:
    if average_fake_probability >= THRESHOLD_DEEPFAKE:
        return "deepfake"

    if (
        strong_deepfake_frame_count >= MIN_STRONG_DEEPFAKE_FRAMES
        and deepfake_frame_ratio >= DEEPFAKE_FRAME_RATIO_THRESHOLD
    ):
        return "deepfake"

    if (
        deepfake_frame_ratio >= DEEPFAKE_FRAME_RATIO_THRESHOLD
        and max_fake_probability >= VERY_HIGH_FRAME_SCORE
    ):
        return "deepfake"

    if average_fake_probability >= THRESHOLD_SUSPICIOUS:
        return "suspicious"

    if suspicious_frame_ratio >= SUSPICIOUS_FRAME_RATIO_THRESHOLD:
        return "suspicious"

    return "authentic"


def combine_video_frame_results(frame_results: list[dict]) -> dict:
    fake_probabilities = [
        frame["deepfake_probability"]
        for frame in frame_results
        if frame.get("deepfake_probability") is not None
    ]

    if not fake_probabilities:
        return {
            "label": "error",
            "is_deepfake": None,
            "is_suspicious": None,
            "deepfake_probability": None,
            "confidence_percent": None
        }

    average_fake_probability_raw = sum(fake_probabilities) / len(fake_probabilities)
    max_fake_probability_raw = max(fake_probabilities)

    deepfake_frame_count = sum(
        1 for probability in fake_probabilities
        if probability >= THRESHOLD_DEEPFAKE
    )

    suspicious_frame_count = sum(
        1 for probability in fake_probabilities
        if probability >= THRESHOLD_SUSPICIOUS
    )

    strong_deepfake_frame_count = sum(
        1 for probability in fake_probabilities
        if probability >= VERY_HIGH_FRAME_SCORE
    )

    deepfake_frame_ratio_raw = deepfake_frame_count / len(fake_probabilities)
    suspicious_frame_ratio_raw = suspicious_frame_count / len(fake_probabilities)

    final_fake_probability_raw = (
        0.75 * average_fake_probability_raw
        + 0.25 * max_fake_probability_raw
    )

    label = label_from_video_statistics(
        average_fake_probability=average_fake_probability_raw,
        max_fake_probability=max_fake_probability_raw,
        deepfake_frame_ratio=deepfake_frame_ratio_raw,
        suspicious_frame_ratio=suspicious_frame_ratio_raw,
        strong_deepfake_frame_count=strong_deepfake_frame_count
    )

    confidence = confidence_from_label(label, final_fake_probability_raw)

    return {
        "label": label,
        "is_deepfake": label == "deepfake",
        "is_suspicious": label == "suspicious",
        "deepfake_probability": round(final_fake_probability_raw, 4),
        "average_deepfake_probability": round(average_fake_probability_raw, 4),
        "max_deepfake_probability": round(max_fake_probability_raw, 4),
        "deepfake_frame_count": deepfake_frame_count,
        "suspicious_frame_count": suspicious_frame_count,
        "strong_deepfake_frame_count": strong_deepfake_frame_count,
        "deepfake_frame_ratio": round(deepfake_frame_ratio_raw, 4),
        "suspicious_frame_ratio": round(suspicious_frame_ratio_raw, 4),
        "confidence_percent": round(confidence * 100, 2)
    }


def analyze_video(file_path: Path) -> dict:
    video = cv2.VideoCapture(str(file_path))

    if not video.isOpened():
        return {
            "label": "error",
            "is_deepfake": None,
            "is_suspicious": None,
            "deepfake_probability": None,
            "confidence_percent": None,
            "frames_analyzed": 0,
            "frame_results": [],
            "explanation": "Video nije moguće otvoriti."
        }

    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    if total_frames <= 0:
        video.release()
        return {
            "label": "error",
            "is_deepfake": None,
            "is_suspicious": None,
            "deepfake_probability": None,
            "confidence_percent": None,
            "frames_analyzed": 0,
            "frame_results": [],
            "explanation": "Video ne sadrži valjane frameove."
        }

    step = max(total_frames // MAX_FRAMES_TO_ANALYZE, 1)

    frame_results = []
    frames_analyzed = 0

    temp_frame_path = Path("uploads") / f"temp_video_frame_{uuid.uuid4()}.jpg"

    try:
        for frame_index in range(0, total_frames, step):
            video.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            success, frame = video.read()

            if not success:
                continue

            cv2.imwrite(str(temp_frame_path), frame)

            frame_result = analyze_image(temp_frame_path)

            if frame_result.get("label") == "error":
                continue

            frame_results.append({
                "frame_index": frame_index,
                "label": frame_result.get("label"),
                "is_deepfake": frame_result.get("is_deepfake"),
                "is_suspicious": frame_result.get("is_suspicious"),
                "real_probability": frame_result.get("real_probability"),
                "deepfake_probability": frame_result.get("deepfake_probability"),
                "confidence_percent": frame_result.get("confidence_percent"),
                "models_used": frame_result.get("models_used"),
                "model": frame_result.get("model"),
                "model_results": frame_result.get("model_results")
            })

            frames_analyzed += 1

            if frames_analyzed >= MAX_FRAMES_TO_ANALYZE:
                break

    finally:
        video.release()

        if temp_frame_path.exists():
            temp_frame_path.unlink(missing_ok=True)

    if not frame_results:
        return {
            "label": "error",
            "is_deepfake": None,
            "is_suspicious": None,
            "deepfake_probability": None,
            "confidence_percent": None,
            "frames_analyzed": 0,
            "frame_results": [],
            "explanation": "Nije moguće analizirati frameove iz videa."
        }

    combined_result = combine_video_frame_results(frame_results)

    if combined_result["label"] == "deepfake":
        explanation = (
            "Video je označen kao deepfake na temelju prosječnog rezultata četiri modela "
            "kroz analizirane frameove."
        )
    elif combined_result["label"] == "suspicious":
        explanation = (
            "Video je označen kao sumnjiv jer dio analiziranih frameova i modela pokazuje "
            "moguće znakove manipulacije."
        )
    else:
        explanation = (
            "Video je označen kao autentičan jer prosječni rezultat četiri modela kroz frameove "
            "ne pokazuje dovoljno visok deepfake signal."
        )

    most_suspicious_frames = sorted(
        frame_results,
        key=lambda frame: frame.get("deepfake_probability", 0),
        reverse=True
    )[:3]

    return {
        **combined_result,
        "frames_analyzed": frames_analyzed,
        "total_frames": total_frames,
        "model": "Frame-based equal-weight ensemble of four deepfake detectors",
        "frame_results": frame_results,
        "most_suspicious_frames": most_suspicious_frames,
        "explanation": explanation
    }