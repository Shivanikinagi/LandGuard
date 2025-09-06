from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Tuple, Dict

class Compressor(ABC):
    """Abstract base for all learned/heuristic compressors.

    Implementations must be pure‑Python compatible and deterministic.
    """
    name: str = "base"
    version: str = "0.1"

    @abstractmethod
    def compress(self, *, path: str, mime: str) -> Tuple[bytes, Dict]:
        """Return (compressed_bytes, model_metadata)."""
        raise NotImplementedError

    @abstractmethod
    def decompress(self, *, data: bytes, meta: Dict) -> bytes:
        """Return original bytes from compressed bytes + model metadata."""
        raise NotImplementedError
