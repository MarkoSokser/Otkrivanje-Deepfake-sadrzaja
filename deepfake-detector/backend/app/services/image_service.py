from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torchvision import models, transforms


DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

MODEL_URL = "https://huggingface.co/Xicor9/efficientnet-b0-ffpp-c23/resolve/main/efficientnet_b0_ffpp_c23.pth"

CLASS_NAMES = {
    0: "authentic",
    1: "deepfake"
}


def load_model():
    """
    Učitava EfficientNet-B0 model treniran za deepfake detekciju.
    Model se učitava jednom pri importu ovog modula.
    """
    state_dict = torch.hub.load_state_dict_from_url(
        MODEL_URL,
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

    return loaded_model


model = load_model()


image_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def crop_face_if_detected(image: Image.Image) -> tuple[Image.Image, bool]:
    """
    Pokušava pronaći lice na slici i cropati ga.
    Ako lice nije pronađeno, vraća originalnu sliku.
    """
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

    # Uzmi najveće detektirano lice
    x, y, w, h = max(faces, key=lambda box: box[2] * box[3])

    # Dodaj marginu oko lica
    margin = int(0.25 * max(w, h))

    x1 = max(x - margin, 0)
    y1 = max(y - margin, 0)
    x2 = min(x + w + margin, image.width)
    y2 = min(y + h + margin, image.height)

    cropped = image.crop((x1, y1, x2, y2))
    return cropped, True


def preprocess_image(file_path: Path) -> tuple[torch.Tensor, bool]:
    """
    Učitava sliku, cropa lice ako je moguće i priprema ulaz za model.
    """
    image = Image.open(file_path).convert("RGB")
    image, face_detected = crop_face_if_detected(image)

    image_tensor = image_transform(image)
    image_tensor = image_tensor.unsqueeze(0)

    return image_tensor.to(DEVICE), face_detected


def analyze_image(file_path: Path) -> dict:
    """
    Analizira sliku pomoću stvarnog EfficientNet-B0 deepfake modela.
    Vraća labelu, vjerojatnost deepfake sadržaja i objašnjenje.
    """
    try:
        input_tensor, face_detected = preprocess_image(file_path)

        with torch.no_grad():
            outputs = model(input_tensor)
            probabilities = F.softmax(outputs, dim=1)[0]

        real_probability = probabilities[0].item()
        fake_probability = probabilities[1].item()

        # Pragovi su namjerno malo fleksibilniji jer model nije univerzalni AI-image detektor.
        if fake_probability >= 0.65:
            label = "deepfake"
        elif fake_probability >= 0.35:
            label = "suspicious"
        else:
            label = "authentic"

        confidence = fake_probability if label in ["deepfake", "suspicious"] else real_probability

        if label == "deepfake":
            explanation = (
                "Model procjenjuje visoku vjerojatnost deepfake/manipuliranog sadržaja. "
                "Rezultat se temelji na analizi detektiranog lica ako je lice pronađeno."
            )
        elif label == "suspicious":
            explanation = (
                "Model nije dovoljno siguran da sadržaj označi kao deepfake, "
                "ali vjerojatnost manipulacije je dovoljno visoka da se sadržaj označi kao sumnjiv."
            )
        else:
            explanation = (
                "Model procjenjuje da sadržaj više odgovara autentičnoj slici. "
                "Napomena: ovaj model nije univerzalni detektor svih AI-generiranih slika."
            )

        return {
            "label": label,
            "real_probability": round(real_probability, 4),
            "deepfake_probability": round(fake_probability, 4),
            "confidence_percent": round(confidence * 100, 2),
            "face_detected": face_detected,
            "model": "EfficientNet-B0 FF++ C23",
            "device": DEVICE,
            "explanation": explanation
        }

    except Exception as error:
        return {
            "label": "error",
            "real_probability": None,
            "deepfake_probability": None,
            "confidence_percent": None,
            "face_detected": False,
            "model": "EfficientNet-B0 FF++ C23",
            "device": DEVICE,
            "explanation": f"Greška tijekom analize slike: {str(error)}"
        }