AVAILABLE_MODELS = {
    "efficientnet_ffpp_c23": {
        "key": "efficientnet_ffpp_c23",
        "name": "EfficientNet-B0 FF++ C23",
        "provider": "Hugging Face",
        "type": "image/frame",
        "supports": ["image", "video"],
        "video_mode": "frame_based",
        "dataset": "FaceForensics++ C23",
        "description": (
            "EfficientNet-B0 model treniran na FaceForensics++ C23 datasetu. "
            "Koristi se za detekciju face-manipulation deepfake sadržaja."
        )
    },
    "opendeepfake_siglip": {
        "key": "opendeepfake_siglip",
        "name": "Open Deepfake Detection SigLIP2",
        "provider": "Hugging Face",
        "model_id": "prithivMLmods/open-deepfake-detection",
        "type": "image/frame",
        "supports": ["image", "video"],
        "video_mode": "frame_based",
        "dataset": "prithivMLmods/OpenDeepfake-Preview",
        "description": (
            "SigLIP2 image-classification model fine-tunan za real/deepfake detekciju. "
            "Za video se koristi frame-based analiza."
        )
    },
    "deepfake_detector_v1": {
        "key": "deepfake_detector_v1",
        "name": "Deepfake Detector Model v1",
        "provider": "Hugging Face",
        "model_id": "prithivMLmods/deepfake-detector-model-v1",
        "type": "image/frame",
        "supports": ["image", "video"],
        "video_mode": "frame_based",
        "dataset": "prithivMLmods/OpenDeepfake-Preview",
        "description": (
            "SigLIP image-classification model za detekciju AI-generiranih/deepfake slika. "
            "Za video se koristi frame-based analiza."
        )
    },
    "vit_deepfake_v2": {
        "key": "vit_deepfake_v2",
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
    return AVAILABLE_MODELS.get(model_key)


def get_available_models() -> list[dict]:
    return list(AVAILABLE_MODELS.values())