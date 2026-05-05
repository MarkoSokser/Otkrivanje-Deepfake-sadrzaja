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
        "image_rank_reason": "Jedini model treniran direktno na video datasetu (FaceForensics++); uključuje detekciju i izrezivanje lica.",
        "video_rank_reason": "Jedini model treniran na video datasetu (FF++); detekcija lica po frameu čini ga najpouzdanijim za video analizu.",
    },
    "wvolf_vit_deepfake": {
        "name": "ViT Deepfake Detection",
        "provider": "Hugging Face",
        "model_id": "Wvolf/ViT-Deepfake-Detection",
        "type": "image/frame",
        "supports": ["image", "video"],
        "video_mode": "frame_based",
        "dataset": "140k Real and Fake Faces dataset",
        "description": (
            "ViT model za detekciju deepfake slika treniran na skupu od 140k stvarnih i lažnih lica. "
            "Za video se koristi frame-based analiza."
        ),
        "image_rank": 2,
        "video_rank": 3,
        "image_rank_reason": "ViT treniran na 140k raznolikih lica — široka pokrivenost vrsta slika.",
        "video_rank_reason": "Treniran na statičnim slikama bez video-specifičnog konteksta; prihvatljiv za frame analizu.",
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
    "vit_deepfake_v2": {
        "name": "ViT Deep-Fake Detector v2",
        "provider": "Hugging Face",
        "model_id": "prithivMLmods/Deep-Fake-Detector-v2-Model",
        "type": "image/frame",
        "supports": ["image", "video"],
        "video_mode": "frame_based",
        "dataset": "Real/deepfake image dataset, exact public train split not clearly specified",
        "description": (
            "ViT image-classification model za real/deepfake klasifikaciju. "
            "Za video se koristi frame-based analiza."
        )
    }
}


ENSEMBLE_MODEL_KEYS = [
    "efficientnet_ffpp_c23",
    "opendeepfake_siglip",
    "deepfake_detector_v1",
    "vit_deepfake_v2"
]


ENSEMBLE_WEIGHTS = {
    "efficientnet_ffpp_c23": 0.25,
    "opendeepfake_siglip": 0.25,
    "deepfake_detector_v1": 0.25,
    "vit_deepfake_v2": 0.25
}


def get_model_info(model_key: str) -> dict | None:
    model = AVAILABLE_MODELS.get(model_key)
    if model is None:
        return None
    return {"key": model_key, **model}


def get_available_models() -> list[dict]:
    return list(AVAILABLE_MODELS.values())
