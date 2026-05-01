from pathlib import Path
import cv2

from app.services.image_service import analyze_image


def analyze_video(file_path: Path) -> dict:
    video = cv2.VideoCapture(str(file_path))

    if not video.isOpened():
        return {
            "label": "error",
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
            "deepfake_probability": None,
            "confidence_percent": None,
            "frames_analyzed": 0,
            "frame_results": [],
            "explanation": "Video ne sadrži valjane frameove."
        }

    max_frames_to_analyze = 10
    step = max(total_frames // max_frames_to_analyze, 1)

    fake_probabilities = []
    frame_results = []
    frames_analyzed = 0

    temp_frame_path = Path("uploads/temp_video_frame.jpg")

    for frame_index in range(0, total_frames, step):
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        success, frame = video.read()

        if not success:
            continue

        cv2.imwrite(str(temp_frame_path), frame)

        frame_result = analyze_image(temp_frame_path)

        if frame_result.get("label") == "error":
            continue

        fake_probability = frame_result.get("deepfake_probability")

        if fake_probability is None:
            continue

        fake_probabilities.append(fake_probability)

        frame_results.append({
            "frame_index": frame_index,
            "label": frame_result.get("label"),
            "real_probability": frame_result.get("real_probability"),
            "deepfake_probability": frame_result.get("deepfake_probability"),
            "confidence_percent": frame_result.get("confidence_percent"),
            "face_detected": frame_result.get("face_detected")
        })

        frames_analyzed += 1

        if frames_analyzed >= max_frames_to_analyze:
            break

    video.release()

    if not fake_probabilities:
        return {
            "label": "error",
            "deepfake_probability": None,
            "confidence_percent": None,
            "frames_analyzed": 0,
            "frame_results": [],
            "explanation": "Nije moguće analizirati frameove iz videa."
        }

    average_fake_probability = round(
        sum(fake_probabilities) / len(fake_probabilities),
        4
    )

    if average_fake_probability >= 0.65:
        label = "deepfake"
    elif average_fake_probability >= 0.35:
        label = "suspicious"
    else:
        label = "authentic"

    confidence = (
        average_fake_probability
        if label in ["deepfake", "suspicious"]
        else 1 - average_fake_probability
    )

    if label == "deepfake":
        explanation = (
            "Video je označen kao deepfake jer prosječna vjerojatnost manipulacije "
            "kroz analizirane frameove prelazi zadani prag."
        )
    elif label == "suspicious":
        explanation = (
            "Video je označen kao sumnjiv jer dio analiziranih frameova pokazuje "
            "znakove moguće manipulacije, ali rezultat nije dovoljno visok za sigurnu deepfake oznaku."
        )
    else:
        explanation = (
            "Video je označen kao autentičan jer većina analiziranih frameova "
            "ne pokazuje visoku vjerojatnost deepfake manipulacije."
        )

    return {
        "label": label,
        "deepfake_probability": average_fake_probability,
        "confidence_percent": round(confidence * 100, 2),
        "frames_analyzed": frames_analyzed,
        "total_frames": total_frames,
        "model": "EfficientNet-B0 FF++ C23 frame-based video analysis",
        "frame_results": frame_results,
        "explanation": explanation
    }