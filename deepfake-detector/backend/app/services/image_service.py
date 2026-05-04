from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torchvision import models, transforms
from transformers import AutoImageProcessor, AutoModelForImageClassification

from app.services.model_registry import (
    DEFAULT_MODEL_KEY,
    ENSEMBLE_MODEL_KEYS,
    ENSEMBLE_WEIGHTS,
    get_model_info,
)


DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

EFFNET_MODEL_URL = (
    "https://huggingface.co/Xicor9/efficientnet-b0-ffpp-c23/"
    "resolve/main/efficientnet_b0_ffpp_c23.pth"
)

THRESHOLD_SUSPICIOUS = 0.55
THRESHOLD_DEEPFAKE = 0.75

_loaded_models = {}


efficientnet_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def label_from_probability(fake_probability: float) -> str:
    if fake_probability >= THRESHOLD_DEEPFAKE:
        return "deepfake"

    if fake_probability >= THRESHOLD_SUSPICIOUS:
        return "suspicious"

    return "authentic"


def confidence_from_label(label: str, fake_probability: float) -> float:
    if label in ["deepfake", "suspicious"]:
        return fake_probability

    return 1.0 - fake_probability


def crop_face_if_detected(image: Image.Image) -> tuple[Image.Image, bool]:
    image_rgb = np.array(image)
    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(80, 80)
    )

    if len(faces) == 0:
        return image, False

    x, y, w, h = max(faces, key=lambda box: box[2] * box[3])
    margin = int(0.25 * max(w, h))

    x1 = max(x - margin, 0)
    y1 = max(y - margin, 0)
    x2 = min(x + w + margin, image.width)
    y2 = min(y + h + margin, image.height)

    return image.crop((x1, y1, x2, y2)), True


def load_efficientnet_model():
    if "efficientnet_ffpp_c23" in _loaded_models:
        return _loaded_models["efficientnet_ffpp_c23"]

    state_dict = torch.hub.load_state_dict_from_url(
        EFFNET_MODEL_URL,
        map_location=DEVICE
    )

    loaded_model = models.efficientnet_b0(weights=None)
    loaded_model.classifier[1] = nn.Linear(
        loaded_model.classifier[1].in_features,
        2
    )

    loaded_model.load_state_dict(state_dict)
    loaded_model.to(DEVICE)
    loaded_model.eval()

    _loaded_models["efficientnet_ffpp_c23"] = loaded_model
    return loaded_model


def load_hf_image_model(model_key: str, model_id: str):
    if model_key in _loaded_models:
        return _loaded_models[model_key]

    processor = AutoImageProcessor.from_pretrained(model_id)
    loaded_model = AutoModelForImageClassification.from_pretrained(model_id)

    loaded_model.to(DEVICE)
    loaded_model.eval()

    _loaded_models[model_key] = {
        "processor": processor,
        "model": loaded_model
    }

    return _loaded_models[model_key]


def extract_fake_probability(
    probabilities: torch.Tensor,
    id2label: dict
) -> tuple[float, float, str]:
    probs = probabilities.detach().cpu().tolist()

    fake_keywords = [
        "fake",
        "deepfake",
        "deep fake",
        "generated",
        "synthetic",
        "ai"
    ]

    real_keywords = [
        "real",
        "authentic",
        "human",
        "natural",
        "realism"
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


def build_single_model_response(
    model_key: str,
    model_name: str,
    dataset: str,
    real_probability: float,
    fake_probability: float,
    raw_predicted_label: str,
    face_detected: bool | None
) -> dict:
    label = label_from_probability(fake_probability)
    confidence = confidence_from_label(label, fake_probability)

    if label == "deepfake":
        explanation = (
            "Model procjenjuje visoku vjerojatnost deepfake ili AI-manipuliranog sadržaja."
        )
    elif label == "suspicious":
        explanation = (
            "Model nije dovoljno siguran za deepfake oznaku, ali rezultat upućuje na moguću manipulaciju."
        )
    else:
        explanation = (
            "Model procjenjuje da sadržaj više odgovara autentičnom sadržaju."
        )

    return {
        "label": label,
        "is_deepfake": label == "deepfake",
        "is_suspicious": label == "suspicious",
        "real_probability": round(real_probability, 4),
        "deepfake_probability": round(fake_probability, 4),
        "confidence_percent": round(confidence * 100, 2),
        "model_key": model_key,
        "model": model_name,
        "dataset": dataset,
        "device": DEVICE,
        "raw_predicted_label": raw_predicted_label,
        "face_detected": face_detected,
        "explanation": explanation
    }


def analyze_with_efficientnet(file_path: Path) -> dict:
    image = Image.open(file_path).convert("RGB")
    cropped_image, face_detected = crop_face_if_detected(image)

    model = load_efficientnet_model()

    image_tensor = efficientnet_transform(cropped_image)
    image_tensor = image_tensor.unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = F.softmax(outputs, dim=1)[0]

    real_probability = probabilities[0].item()
    fake_probability = probabilities[1].item()

    return build_single_model_response(
        model_key="efficientnet_ffpp_c23",
        model_name="EfficientNet-B0 FF++ C23",
        dataset="FaceForensics++ C23",
        real_probability=real_probability,
        fake_probability=fake_probability,
        raw_predicted_label="deepfake" if fake_probability >= real_probability else "authentic",
        face_detected=face_detected
    )


def analyze_with_hf_image_model(file_path: Path, model_key: str) -> dict:
    model_info = get_model_info(model_key)

    if model_info is None:
        raise ValueError(f"Nepoznat model_key: {model_key}")

    model_id = model_info.get("model_id")

    if not model_id:
        raise ValueError(f"Model {model_key} nema definiran Hugging Face model_id.")

    image = Image.open(file_path).convert("RGB")

    loaded = load_hf_image_model(model_key, model_id)
    processor = loaded["processor"]
    model = loaded["model"]

    inputs = processor(images=image, return_tensors="pt")
    inputs = {
        key: value.to(DEVICE)
        for key, value in inputs.items()
    }

    with torch.no_grad():
        outputs = model(**inputs)
        probabilities = F.softmax(outputs.logits, dim=1)[0]

    real_probability, fake_probability, raw_predicted_label = extract_fake_probability(
        probabilities,
        model.config.id2label
    )

    return build_single_model_response(
        model_key=model_key,
        model_name=model_info["name"],
        dataset=model_info["dataset"],
        real_probability=real_probability,
        fake_probability=fake_probability,
        raw_predicted_label=raw_predicted_label,
        face_detected=None
    )


def combine_ensemble_results(model_results: list[dict]) -> dict:
    valid_results = [
        result for result in model_results
        if result.get("deepfake_probability") is not None
        and result.get("label") != "error"
    ]

    if not valid_results:
        return {
            "label": "error",
            "is_deepfake": None,
            "is_suspicious": None,
            "real_probability": None,
            "deepfake_probability": None,
            "confidence_percent": None,
            "model_key": "ensemble",
            "model": "Weighted Ensemble",
            "model_results": model_results,
            "explanation": "Nijedan model nije uspješno vratio rezultat."
        }

    total_weight = sum(
        ENSEMBLE_WEIGHTS.get(result["model_key"], 0.0)
        for result in valid_results
    )

    if total_weight <= 0:
        total_weight = len(valid_results)

    fake_probability = sum(
        result["deepfake_probability"]
        * ENSEMBLE_WEIGHTS.get(result["model_key"], 1.0)
        for result in valid_results
    ) / total_weight

    real_probability = 1.0 - fake_probability

    label = label_from_probability(fake_probability)
    confidence = confidence_from_label(label, fake_probability)

    deepfake_votes = sum(1 for result in valid_results if result["label"] == "deepfake")
    suspicious_votes = sum(1 for result in valid_results if result["label"] == "suspicious")
    authentic_votes = sum(1 for result in valid_results if result["label"] == "authentic")

    if label == "deepfake":
        explanation = (
            "Kombinirani rezultat više modela ukazuje na visoku vjerojatnost deepfake sadržaja."
        )
    elif label == "suspicious":
        explanation = (
            "Kombinirani rezultat je sumnjiv, ali nije dovoljno visok za sigurnu deepfake oznaku."
        )
    else:
        explanation = (
            "Kombinirani rezultat više odgovara autentičnom sadržaju."
        )

    explanation += (
        f" Glasovi modela: deepfake={deepfake_votes}, "
        f"sumnjivo={suspicious_votes}, autentično={authentic_votes}."
    )

    return {
        "label": label,
        "is_deepfake": label == "deepfake",
        "is_suspicious": label == "suspicious",
        "real_probability": round(real_probability, 4),
        "deepfake_probability": round(fake_probability, 4),
        "confidence_percent": round(confidence * 100, 2),
        "model_key": "ensemble",
        "model": "Weighted Ensemble",
        "models_used": len(valid_results),
        "device": DEVICE,
        "model_results": model_results,
        "explanation": explanation
    }


def analyze_image(file_path: Path, model_key: str = DEFAULT_MODEL_KEY) -> dict:
    try:
        if model_key == "ensemble":
            model_results = [
                analyze_image(file_path, single_model_key)
                for single_model_key in ENSEMBLE_MODEL_KEYS
            ]

            return combine_ensemble_results(model_results)

        if model_key == "efficientnet_ffpp_c23":
            return analyze_with_efficientnet(file_path)

        return analyze_with_hf_image_model(file_path, model_key)

    except Exception as error:
        return {
            "label": "error",
            "is_deepfake": None,
            "is_suspicious": None,
            "real_probability": None,
            "deepfake_probability": None,
            "confidence_percent": None,
            "model_key": model_key,
            "model": model_key,
            "device": DEVICE,
            "explanation": f"Greška tijekom analize slike: {str(error)}"
        }