from pathlib import Path
from typing import List, Dict, Any

import numpy as np
from PIL import Image
import streamlit as st

try:
    import tensorflow as tf
except Exception:
    tf = None

TM_IMAGE_SIZE = (224, 224)


@st.cache_resource(show_spinner=False)
def load_local_teachable_machine_model(model_path: str, labels_path: str):
    if tf is None:
        raise ImportError("TensorFlow is not installed. Use Python 3.10 or 3.11 and install requirements.txt.")
    model_file, label_file = Path(model_path), Path(labels_path)
    if not model_file.exists():
        raise FileNotFoundError(f"Model file not found: {model_file}")
    if not label_file.exists():
        raise FileNotFoundError(f"Labels file not found: {label_file}")
    return tf.keras.models.load_model(model_file, compile=False), load_labels(label_file)


def load_labels(labels_path: Path) -> List[str]:
    labels = []
    for line in open(labels_path, "r", encoding="utf-8"):
        cleaned = line.strip()
        if not cleaned:
            continue
        parts = cleaned.split(" ", 1)
        labels.append(parts[1].strip() if len(parts) == 2 and parts[0].isdigit() else cleaned)
    return labels


def preprocess_image_for_model(image: Image.Image) -> np.ndarray:
    arr = np.asarray(image.convert("RGB").resize(TM_IMAGE_SIZE)).astype(np.float32)
    return np.expand_dims((arr / 127.5) - 1.0, axis=0)


def get_top_predictions(probabilities: np.ndarray, labels: List[str], top_k: int = 3) -> List[Dict[str, Any]]:
    scored = sorted(enumerate(probabilities.tolist()), key=lambda x: x[1], reverse=True)
    return [{"label": labels[i] if i < len(labels) else f"Class {i}", "confidence": float(c)} for i, c in scored[:top_k]]


def predict_gesture_from_image(model, labels: List[str], image: Image.Image) -> Dict[str, Any]:
    raw = model.predict(preprocess_image_for_model(image), verbose=0)[0]
    best = int(np.argmax(raw))
    return {
        "label": labels[best] if best < len(labels) else f"Class {best}",
        "confidence": float(raw[best]),
        "top_predictions": get_top_predictions(raw, labels),
    }
