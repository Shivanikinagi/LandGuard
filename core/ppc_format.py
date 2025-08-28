# core/ppc_format.py
import cbor2
from typing import Dict, Any
import struct
import json

PPC_MAGIC = b"PPCv2"

class PPCFile:
    def __init__(self, original_data: bytes, metedata: Dict[str, Any]):
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
    def unpack(data: bytes) -> dict:
        header_len = struct.unpack('<I', data[:4])[0]
        header = json.loads(data[4:4+header_len].decode('utf-8'))  # Only header!
        payload = data[4+header_len:]  # This is raw bytes, do NOT decode
        return {"header": header, "data": payload}

# with open(ppc_path, "rb") as f:
#     raw_ppc_data = f.read()
# print("DEBUG first 16 bytes:", raw_ppc_data[:16])