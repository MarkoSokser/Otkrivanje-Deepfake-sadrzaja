AVAILABLE_MODELS = {
    "efficientnet_ffpp_c23": {
        "name": "EfficientNet-B0 FF++ C23",
        "provider": "Hugging Face",
        "model_id": "Xicor9/efficientnet-b0-ffpp-c23",
        "type": "image/frame",
        "supports": ["image", "video"],
        "video_mode": "frame_based",
        "dataset": "FaceForensics++ C23",
        "description": (
            "EfficientNet-B0 model treniran na FaceForensics++ C23 datasetu. "
            "Koristi se za detekciju face-manipulation deepfake sadržaja."
        ),
        "image_rank": 1,
        "video_rank": 1,
        "image_rank_reason": "Model treniran direktno na FaceForensics++ video datasetu; uključuje detekciju i izrezivanje lica.",
        "video_rank_reason": "Treniran na video datasetu FF++; detekcija lica po frameu čini ga najpouzdanijim za video analizu.",
    },
    "boluobobo_ai_detector_v1": {
        "name": "ItsNotAI AI Detector v1",
        "provider": "Hugging Face",
        "model_id": "boluobobo/ItsNotAI-ai-detector-v1",
        "type": "image/frame",
        "supports": ["image", "video"],
        "video_mode": "frame_based",
        "dataset": "AI-generated and real image detection dataset",
        "description": (
            "Image-classification model za razlikovanje AI-generiranih i realnih slika. "
            "Za video se koristi frame-based analiza."
        ),
        "image_rank": 2,
        "video_rank": 3,
        "image_rank_reason": "Kompatibilan s Transformers AutoImageProcessor/AutoModelForImageClassification i fokusiran na AI/fake image detekciju.",
        "video_rank_reason": "Nije temporalni video model, ali može analizirati pojedinačne frameove.",
    },
    "dima806_vit_deepfake": {
        "name": "ViT Deepfake vs Real Image Detection",
        "provider": "Hugging Face",
        "model_id": "dima806/deepfake_vs_real_image_detection",
        "type": "image/frame",
        "supports": ["image", "video"],
        "video_mode": "frame_based",
        "dataset": "Deepfake vs real faces dataset, described in linked Kaggle notebook",
        "description": (
            "ViT image-classification model za real/fake odnosno AI-generated/deepfake detekciju. "
            "Za video se koristi frame-based analiza."
        ),
        "image_rank": 3,
        "video_rank": 2,
        "image_rank_reason": "ViT klasifikator fokusiran na lica; solidan ali uži skup podataka od ostalih.",
        "video_rank_reason": "Fokus na klasifikaciju lica čini ga pogodnim za frame-baziranu video analizu.",
    },
    "king1oo1_deepfake_model": {
        "name": "SigLIP2 Deepfake Model",
        "provider": "Hugging Face",
        "model_id": "king1oo1/deepfake-model",
        "type": "image/frame",
        "supports": ["image", "video"],
        "video_mode": "frame_based",
        "dataset": "Diverse multi-source real/fake image dataset with over 330,000 images",
        "description": (
            "SigLIP2 image-classification model za razlikovanje realnih i fake odnosno "
            "AI-generiranih/deepfake slika. Za video se koristi frame-based analiza."
        ),
        "image_rank": 4,
        "video_rank": 4,
        "image_rank_reason": "Treniran na velikom multi-source skupu slika, uključujući moderne AI generatore.",
        "video_rank_reason": "Nije temporalni video model, ali može analizirati pojedinačne frameove.",
    },
}

VIDEO_MODEL_KEY = "videomae_ffpp_c23"

VIDEO_MODEL = {
    "key": VIDEO_MODEL_KEY,
    "name": "VideoMAE FF++ C23 Deepfake Detector",
    "provider": "Hugging Face",
    "model_id": "eftt/VideoMae-ffc23-deepfake-detector",
    "type": "video",
    "supports": ["video"],
    "video_mode": "temporal_video_classification",
    "dataset": "FaceForensics++ C23",
    "description": (
        "VideoMAE model treniran za klasifikaciju videa kao originalan ili deepfake. "
        "Za razliku od image modela, analizira više frameova zajedno."
    ),
    "video_rank": 1,
    "video_rank_reason": (
        "Poseban video-classification model treniran na FaceForensics++ deepfake video podacima."
    ),
}


def get_video_model_info() -> dict:
    return VIDEO_MODEL

ENSEMBLE_MODEL_KEYS = list(AVAILABLE_MODELS.keys())

ENSEMBLE_WEIGHTS = {
    k: 1 / len(ENSEMBLE_MODEL_KEYS)
    for k in ENSEMBLE_MODEL_KEYS
}


def get_model_info(model_key: str) -> dict | None:
    model = AVAILABLE_MODELS.get(model_key)
    if model is None:
        return None
    return {"key": model_key, **model}


def get_available_models() -> list[dict]:
    image_models = [
        {"key": key, **value}
        for key, value in AVAILABLE_MODELS.items()
    ]

    return image_models + [VIDEO_MODEL]
