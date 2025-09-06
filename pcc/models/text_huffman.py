from __future__ import annotations
import heapq
from collections import Counter
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from ..utils import read_bytes

@dataclass
class _Node:
    freq: int
    sym: Optional[int] = None  # byte value 0..255
    left: Optional["_Node"] = None
    right: Optional["_Node"] = None

    def __lt__(self, other: "_Node"):
        return self.freq < other.freq

class TextHuffman:
    name = "text-huffman"
    version = "0.1"

    def _build_tree(self, data: bytes) -> _Node:
        freq = Counter(data)
        heap = [ _Node(f, s) for s, f in freq.items() ]
        heapq.heapify(heap)
        if len(heap) == 1:
            # Edge: single symbol; create a dummy parent
            only = heapq.heappop(heap)
            return _Node(only.freq, None, only, None)
        while len(heap) > 1:
            a = heapq.heappop(heap)
            b = heapq.heappop(heap)
            heapq.heappush(heap, _Node(a.freq + b.freq, None, a, b))
        return heap[0]

    def _build_table(self, node: _Node) -> Dict[int, str]:
        table: Dict[int, str] = {}
        def dfs(n: _Node, path: str):
            if n.sym is not None:
                table[n.sym] = path or "0"
                return
            if n.left:
                dfs(n.left, path + "0")
            if n.right:
                dfs(n.right, path + "1")
        dfs(node, "")
        return table


    def _pack_bits(self, bitstr: str) -> Tuple[bytes, int]:
        # returns (packed_bytes, padding_bits)
        pad = (8 - (len(bitstr) % 8)) % 8
        bitstr += "0" * pad
        out = bytearray()
        for i in range(0, len(bitstr), 8):
            out.append(int(bitstr[i:i+8], 2))
        return bytes(out), pad


    def _unpack_bits(self, data: bytes, pad: int) -> str:
        bits = ''.join(f"{b:08b}" for b in data)
        return bits[:-pad] if pad else bits

    def compress(self, *, path: str, mime: str):
        raw = read_bytes(path)
        # Treat bytes directly (works for UTF‑8 text too)
        if not raw:
            return b"", {"table": {}, "pad": 0}
        root = self._build_tree(raw)
        table = self._build_table(root)
        # Encode
        bits = ''.join(table[b] for b in raw)
        packed, pad = self._pack_bits(bits)
        # Serialize table as {"<byte>": "code"}
        tbl = {str(k): v for k, v in table.items()}
        meta = {"table": tbl, "pad": pad}
        return packed, meta

    def decompress(self, *, data: bytes, meta: Dict) -> bytes:
        table = {int(k): v for k, v in meta["table"].items()}
        inv = {v: k for k, v in table.items()}
        pad = int(meta.get("pad", 0))
        bits = self._unpack_bits(data, pad)
        out = bytearray()
        node = ""
        for bit in bits:
            node += bit
            if node in inv:
                out.append(inv[node])
                node = ""
        return bytes(out)