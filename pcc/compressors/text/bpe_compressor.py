# compressors/text/bpe_compressor.py
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import Whitespace
import numpy as np
import os

def train_bpe(files, vocab_size=256):
    tokenizer = Tokenizer(BPE(unk_token="[UNK]"))
    tokenizer.pre_tokenizer = Whitespace()
    trainer = BpeTrainer(special_tokens=["[UNK]"], vocab_size=vocab_size)
    tokenizer.train(files)
    tokenizer.save("../models/bpe.json")
    print("✅ BPE Tokenizer saved")

def compress_text(text: str) -> bytes:
    tokenizer = Tokenizer.from_file("../models/bpe.json")
    encoded = tokenizer.encode(text)
    return np.array(encoded.ids, dtype=np.uint16).tobytes()

def decompress_text(data: bytes) -> str:
    ids = np.frombuffer(data, dtype=np.uint16)
    tokenizer = Tokenizer.from_file("../models/bpe.json")
    return tokenizer.decode(ids.tolist())