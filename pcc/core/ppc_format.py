# core/ppc_format.py

import cbor2
from typing import Dict, Any
import json
import struct

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
    def unpack(data: bytes) -> dict:
        obj = cbor2.loads(data)
        return {"header": obj["header"], "data": obj["payload"]}


def create_ppc_file(encrypted_data: bytes, metadata: Dict[str, Any], output_path: str) -> None:
    """
    Create a .ppc file with encrypted data and metadata
    
    Args:
        encrypted_data: The encrypted data to store
        metadata: Metadata to include in the file
        output_path: Path where to save the .ppc file
    """
    ppc_file = PPCFile(encrypted_data, metadata)
    packed_data = ppc_file.pack()
    
    with open(output_path, "wb") as f:
        f.write(packed_data)


def read_ppc_file(ppc_path: str) -> tuple:
    """
    Read a .ppc file and return the encrypted data and metadata
    
    Args:
        ppc_path: Path to the .ppc file
        
    Returns:
        Tuple of (encrypted_data, metadata)
    """
    with open(ppc_path, "rb") as f:
        raw_data = f.read()
    
    unpacked = PPCFile.unpack(raw_data)
    return unpacked["data"], unpacked["header"]