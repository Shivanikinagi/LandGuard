from __future__ import annotations
from typing import Dict
from ..utils import read_bytes


class AudioNoop:
    """No‑op compressor for audio until WaveNet/SoundStream is integrated."""
    name = "audio-noop"
    version = "0.1"

    def compress(self, *, path: str, mime: str):
        # No compression (phase 2 placeholder)
        from pathlib import Path
        p = Path(path)
        data = p.read_bytes()
        return data, {"noop": True}

    def decompress(self, *, data: bytes, meta: Dict) -> bytes:
        return data