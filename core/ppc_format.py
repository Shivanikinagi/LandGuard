# core/ppc_format.py
import cbor2
from typing import Dict, Any
import json

PPC_MAGIC = b"PPCv2"

class PPCFile:
    def __init__(self, original_data: bytes, metadata: Dict[str, Any]):
        self.original_data = original_data
        self.metadata = metadata

    def pack(self) -> bytes:
        header = {
            "magic_number": PPC_MAGIC.decode(),
            "version": "1.0",
            "original_size_bytes": len(self.original_data),
            "compressed_size_bytes": len(self.original_data),  # placeholder
            "compression_ratio": 1.0,
            **self.metadata
        }
        # In Phase 2: self.original_data will be compressed
        return cbor2.dumps({
            "header": header,
            "payload": self.original_data
        })

    @staticmethod
    def unpack(data: bytes) -> Dict[str, Any]:
        try:
            decoded = cbor2.loads(data)
            if decoded["header"]["magic_number"] != "PPCv2":
                raise ValueError("Not a valid .ppc file")
            return decoded
        except Exception as e:
            raise ValueError(f"Invalid PPC file: {e}")