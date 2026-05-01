from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.media_service import detect_media_type
from app.services.image_service import analyze_image
from app.services.video_service import analyze_video
from app.utils.file_utils import save_upload_file, validate_file_extension

router = APIRouter()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".mp4", ".mov", ".avi"}


@router.get("/models")
def get_models():
    return {
        "available_models": [
            {
                "name": "Image deepfake detector",
                "type": "image",
                "description": "Model za analizu slika"
            },
            {
                "name": "Frame-based video detector",
                "type": "video",
                "description": "Video se dijeli na frameove, a zatim se svaki frame analizira image modelom"
            }
        ]
    }


@router.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    extension = Path(file.filename).suffix.lower()

    if not validate_file_extension(extension, ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail="Nepodržan format datoteke. Podržani formati su: jpg, jpeg, png, mp4, mov, avi."
        )

    saved_path = save_upload_file(file)

    media_type = detect_media_type(saved_path)

    if media_type == "image":
        result = analyze_image(saved_path)
    elif media_type == "video":
        result = analyze_video(saved_path)
    else:
        raise HTTPException(
            status_code=400,
            detail="Nije moguće odrediti tip medija."
        )

    return {
        "filename": file.filename,
        "media_type": media_type,
        "analysis": result
    }