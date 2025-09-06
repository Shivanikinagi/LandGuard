from __future__ import annotations
from typing import Optional
from .base import Compressor
from .text_huffman import TextHuffman
from .image_vae_stub import ImageVAEStub
from .image_vae import ImageVAE  # Import real VAE
from .audio_noop import AudioNoop

_PRIMARY_TYPE_MAP = {
    "text": TextHuffman,
    "image": ImageVAE,  # Use real VAE instead of stub
    "audio": AudioNoop,
}

# MIME prefix → primary type
_MIME_TO_PRIMARY = {
    "text": "text",
    "image": "image",
    "audio": "audio",
}

def detect_primary_type(mime: str) -> str:
    for prefix, ptype in _MIME_TO_PRIMARY.items():
        if mime.startswith(prefix + "/"):
            return ptype
    return "binary"


def get_model(primary_type: str, override: Optional[str] = None) -> Compressor:
    if override:
        if override == "text-huffman":
            return TextHuffman()
        if override == "image-vae-stub":
            return ImageVAEStub()
        if override == "image-vae":  # Add this line
            return ImageVAE()
        if override == "audio-noop":
            return AudioNoop()
        raise ValueError(f"Unknown model override: {override}")
    # auto
    cls = _PRIMARY_TYPE_MAP.get(primary_type, TextHuffman)
    return cls()