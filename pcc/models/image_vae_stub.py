from __future__ import annotations
from typing import Dict
from pyzstd import ZstdCompressor, ZstdDecompressor
from ..utils import read_bytes

class ImageVAEStub:
    """Placeholder for a real VAE. Uses Zstd as a strong baseline.
    Replace with real VAE encode/decode later (store codebook/model hash in meta).
    """
    name = "image-vae-stub"
    version = "0.1"

    def compress(self, *, path: str, mime: str):
        raw = read_bytes(path)
        comp = ZstdCompressor(7).compress(raw)
        meta: Dict = {"post": "zstd", "level": 7}
        return comp, meta

    def decompress(self, *, data: bytes, meta: Dict) -> bytes:
        return ZstdDecompressor().decompress(data)