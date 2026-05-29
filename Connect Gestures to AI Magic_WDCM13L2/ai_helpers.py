"""Lesson 2 AI helpers — spell text generation and spell scene image generation."""

from __future__ import annotations
from typing import Optional, Tuple

import requests
from huggingface_hub import InferenceClient
from PIL import Image

import config

GESTURE_TO_SPELL = {
    "Palm": "Shield of Light",
    "Peace": "Healing Aura",
    "Pointer": "Lightning Strike",
    "Thumbs Up": "Phoenix Blessing",
}

SPELL_IMAGE_PROMPTS = {
    "Shield of Light": "A radiant magical shield forming from a glowing open hand, golden energy barrier, fantasy spell casting, cinematic fantasy art, luminous particles, enchanted temple",
    "Healing Aura": "A peaceful healing spell with green and silver glowing energy, floating magical particles, restoration magic, fantasy art, gentle mystical light",
    "Lightning Strike": "A sharp bolt of magical lightning cast from a pointing hand, storm energy, glowing blue electricity, ancient ruins, epic fantasy spell scene",
    "Phoenix Blessing": "A fiery phoenix spirit blessing the caster, warm magical glow, flame wings, fantasy spell scene, sacred mystical fire",
}


def get_spell_name(gesture_label: str) -> str:
    return GESTURE_TO_SPELL.get(gesture_label, "Arcane Pulse")


def build_image_prompt(spell_name: str, gesture_label: str, source: str) -> str:
    base = SPELL_IMAGE_PROMPTS.get(spell_name, f"A magical fantasy spell scene for {spell_name}, triggered by a {gesture_label} hand gesture, glowing enchanted energy, cinematic fantasy art")
    ctx = ("triggered by a live webcam-captured hand gesture" if source == "webcam"
           else "triggered by an uploaded hand gesture image")
    return f"{base}. Scene {ctx}. Keep the hand sign influence visible. Cinematic, fantasy-rich, colorful, suitable for a student project."


def generate_spell_text(gesture_label: str, spell_name: str, source: str) -> str:
    fallback = (f"Spell Name: {spell_name}\n\nThe studio reads the gesture '{gesture_label}' and channels {spell_name}. "
                "Runes shimmer through the air as the magic awakens. "
                "A wave of energy surges outward and the room responds like a living spellbook.")
    if not config.GROQ_API_KEY:
        return fallback
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {config.GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": config.GROQ_TEXT_MODEL,
                "messages": [
                    {"role": "system", "content": "You create clean fantasy spell text for a Streamlit classroom project."},
                    {"role": "user", "content": (
                        f"You are the narrator inside a magical gesture-controlled AI studio.\n"
                        f"The user performed this gesture: {gesture_label}\n"
                        f"The detected spell is: {spell_name}\n"
                        f"Input source: {source}\n\n"
                        "Write a student-friendly fantasy response with:\n"
                        "1. Spell Name\n2. 3 short vivid lines of magical narration\n3. A one-line power summary\n\n"
                        "Keep it immersive, exciting, and easy to read."
                    )},
                ],
                "temperature": 0.9,
            },
            timeout=60,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return fallback


def generate_spell_image(prompt: str) -> Tuple[Optional[Image.Image], Optional[str]]:
    if not config.HF_API_KEY:
        return None, "HF_API_KEY is missing. Add your Hugging Face key in .env."
    try:
        image = InferenceClient(provider=config.HF_PROVIDER, api_key=config.HF_API_KEY).text_to_image(prompt, model=config.HF_IMAGE_MODEL)
        return image.convert("RGB"), None
    except Exception as e:
        return None, f"Image generation failed with model '{config.HF_IMAGE_MODEL}' and provider '{config.HF_PROVIDER}': {e}"
