from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services.media_service import detect_media_type
from app.services.image_service import analyze_image
from app.services.video_service import analyze_video
from app.services.model_registry import (
    DEFAULT_MODEL_KEY,
    get_available_models,
    is_valid_model_key,
)
from app.utils.file_utils import save_upload_file, validate_file_extension

router = APIRouter()

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".mp4",
    ".mov",
    ".avi",
    ".webm",
    ".mkv"
}


@router.get("/models")
def get_models():
    return {
        "default_model_key": DEFAULT_MODEL_KEY,
        "available_models": get_available_models(),
        "usage": {
            "endpoint": "POST /analyze",
            "form_fields": {
                "file": "Slika ili video datoteka.",
                "model_key": (
                    "Opcionalno. Jedan od dostupnih model_key vrijednosti. "
                    "Ako nije poslano, koristi se ensemble."
                )
            }
        },
        "labels": {
            "authentic": "Sadržaj se procjenjuje kao autentičan.",
            "suspicious": "Sadržaj je sumnjiv i preporučuje se dodatna provjera.",
            "deepfake": "Sadržaj se procjenjuje kao vjerojatni deepfake."
        },
        "supported_formats": sorted(list(ALLOWED_EXTENSIONS))
    }


@router.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    model_key: str = Form(DEFAULT_MODEL_KEY)
):
    extension = Path(file.filename).suffix.lower()

    if not validate_file_extension(extension, ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail=(
                "Nepodržan format datoteke. "
                "Podržani formati su: jpg, jpeg, png, webp, mp4, mov, avi, webm, mkv."
            )
        )

    if not is_valid_model_key(model_key):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Nepoznat model_key: {model_key}. "
                "Dostupne modele možeš vidjeti na GET /models."
            )
        )

    saved_path = save_upload_file(file)

    media_type = detect_media_type(saved_path)

    if media_type == "image":
        result = analyze_image(saved_path, model_key=model_key)
    elif media_type == "video":
        result = analyze_video(saved_path, model_key=model_key)
    else:
        raise HTTPException(
            status_code=400,
            detail="Nije moguće odrediti tip medija."
        )

    return {
        "filename": file.filename,
        "media_type": media_type,
        "requested_model_key": model_key,
        "is_deepfake": result.get("is_deepfake"),
        "is_suspicious": result.get("is_suspicious"),
        "label": result.get("label"),
        "deepfake_probability": result.get("deepfake_probability"),
        "confidence_percent": result.get("confidence_percent"),
        "analysis": result
    }