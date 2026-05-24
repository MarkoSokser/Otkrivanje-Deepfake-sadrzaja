from pathlib import Path

import cv2
import torch
import torch.nn.functional as F
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForVideoClassification

from app.services.image_service import label_from_probability, confidence_from_label
from app.services.model_registry import get_video_model_info


DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

_loaded_video_models = {}


def load_videomae_model():
    video_model_info = get_video_model_info()
    model_key = video_model_info["key"]
    model_id = video_model_info["model_id"]

    if model_key in _loaded_video_models:
        return _loaded_video_models[model_key]

    processor = AutoImageProcessor.from_pretrained(model_id)
    model = AutoModelForVideoClassification.from_pretrained(model_id)

    model.to(DEVICE)
    model.eval()

    _loaded_video_models[model_key] = {
        "processor": processor,
        "model": model
    }

    return _loaded_video_models[model_key]


def sample_video_frames(
    file_path: Path,
    num_frames: int
) -> list[Image.Image]:
    video = cv2.VideoCapture(str(file_path))

    if not video.isOpened():
        raise ValueError("Video nije moguće otvoriti.")

    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    if total_frames <= 0:
        video.release()
        raise ValueError("Video ne sadrži valjane frameove.")

    if total_frames <= num_frames:
        frame_indices = list(range(total_frames))
    else:
        step = total_frames / num_frames
        frame_indices = [
            int(index * step)
            for index in range(num_frames)
        ]

    frames = []

    try:
        for frame_index in frame_indices:
            video.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            success, frame = video.read()

            if not success:
                continue

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_frame = Image.fromarray(frame_rgb).convert("RGB")
            frames.append(pil_frame)

    finally:
        video.release()

    if not frames:
        raise ValueError("Nije moguće izdvojiti frameove iz videa.")

    while len(frames) < num_frames:
        frames.append(frames[-1])

    return frames[:num_frames]


def extract_fake_probability(
    probabilities: torch.Tensor,
    id2label: dict
) -> tuple[float, float, str]:
    probs = probabilities.detach().cpu().tolist()

    fake_keywords = [
        "fake",
        "deepfake",
        "deep fake",
        "manipulated",
        "synthetic"
    ]

    real_keywords = [
        "real",
        "authentic",
        "original",
        "pristine"
    ]

    fake_indices = []
    real_indices = []

    for index, label in id2label.items():
        index = int(index)
        normalized_label = str(label).lower()

        if any(keyword in normalized_label for keyword in fake_keywords):
            fake_indices.append(index)

        if any(keyword in normalized_label for keyword in real_keywords):
            real_indices.append(index)

    if fake_indices:
        fake_probability = sum(probs[index] for index in fake_indices)
    else:
        fake_probability = probs[1] if len(probs) > 1 else probs[0]

    if real_indices:
        real_probability = sum(probs[index] for index in real_indices)
    else:
        real_probability = 1.0 - fake_probability

    predicted_index = int(torch.argmax(probabilities).item())
    predicted_label = str(id2label.get(predicted_index, predicted_index))

    fake_probability = max(0.0, min(1.0, fake_probability))
    real_probability = max(0.0, min(1.0, real_probability))

    return real_probability, fake_probability, predicted_label


def analyze_video_with_videomae(file_path: Path) -> dict:
    video_model_info = get_video_model_info()
    model_key = video_model_info["key"]

    try:
        loaded = load_videomae_model()
        processor = loaded["processor"]
        model = loaded["model"]

        num_frames = getattr(model.config, "num_frames", 16)

        frames = sample_video_frames(
            file_path=file_path,
            num_frames=num_frames
        )

        inputs = processor(frames, return_tensors="pt")

        if inputs["pixel_values"].ndim == 4:
            inputs["pixel_values"] = inputs["pixel_values"].unsqueeze(0)

        inputs = {
            key: value.to(DEVICE)
            for key, value in inputs.items()
        }

        with torch.no_grad():
            outputs = model(**inputs)
            probabilities = F.softmax(outputs.logits, dim=1)[0]

        real_probability, fake_probability, raw_predicted_label = extract_fake_probability(
            probabilities=probabilities,
            id2label=model.config.id2label
        )

        label = label_from_probability(fake_probability)
        confidence = confidence_from_label(label, fake_probability)
        fake_percent = round(fake_probability * 100, 1)

        if label == "deepfake":
            explanation = (
                f"VideoMAE video model detektira deepfake — "
                f"vjerojatnost manipulacije: {fake_percent}%."
            )
        elif label == "suspicious":
            explanation = (
                f"VideoMAE video model uočava moguću manipulaciju "
                f"({fake_percent}%), ali rezultat nije dovoljno visok za sigurnu deepfake oznaku."
            )
        else:
            explanation = (
                f"VideoMAE video model procjenjuje video kao autentičan — "
                f"vjerojatnost manipulacije: {fake_percent}%."
            )

        return {
            "label": label,
            "is_deepfake": label == "deepfake",
            "is_suspicious": label == "suspicious",
            "real_probability": round(real_probability, 4),
            "deepfake_probability": round(fake_probability, 4),
            "confidence_percent": round(confidence * 100, 2),
            "models_used": 1,
            "model_key": model_key,
            "model": video_model_info["name"],
            "dataset": video_model_info["dataset"],
            "device": DEVICE,
            "raw_predicted_label": raw_predicted_label,
            "video_frames_used": num_frames,
            "model_results": [
                {
                    "label": label,
                    "is_deepfake": label == "deepfake",
                    "is_suspicious": label == "suspicious",
                    "real_probability": round(real_probability, 4),
                    "deepfake_probability": round(fake_probability, 4),
                    "confidence_percent": round(confidence * 100, 2),
                    "model_key": model_key,
                    "model": video_model_info["name"],
                    "dataset": video_model_info["dataset"],
                    "device": DEVICE,
                    "raw_predicted_label": raw_predicted_label,
                    "video_frames_used": num_frames,
                    "explanation": explanation
                }
            ],
            "explanation": explanation
        }

    except Exception as error:
        return {
            "label": "error",
            "is_deepfake": None,
            "is_suspicious": None,
            "real_probability": None,
            "deepfake_probability": None,
            "confidence_percent": None,
            "models_used": 0,
            "model_key": model_key,
            "model": video_model_info["name"],
            "dataset": video_model_info["dataset"],
            "device": DEVICE,
            "raw_predicted_label": "error",
            "video_frames_used": 0,
            "model_results": [],
            "explanation": f"Greška tijekom VideoMAE video analize: {str(error)}"
        }