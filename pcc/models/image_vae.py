from __future__ import annotations
import torch
import numpy as np
from PIL import Image
from io import BytesIO
from typing import Dict
import pickle
from pathlib import Path

from ..utils import read_bytes

# Try to import VAE, fall back to stub if not available
try:
    from ..compressors.image.vae import VAE
    from .config import VAE_MODEL_PATH
    VAE_AVAILABLE = True
except ImportError:
    VAE_AVAILABLE = False
    print("Warning: VAE model not available, falling back to stub compression")

class ImageVAE:
    """VAE-based image compressor with graceful fallback."""
    name = "image-vae"
    version = "1.0"
    
    def __init__(self, latent_dim=128):
        self.latent_dim = latent_dim
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def _load_model(self):
        """Load the trained VAE model or fall back."""
        if not VAE_AVAILABLE:
            return False
            
        if self.model is None:
            model_path = Path(__file__).parent.parent / "compressors" / "image" / "models" / "vae_model.pth"
            print("Loading VAE model from:", model_path)
            print("Model exists?", model_path.exists())
            if not model_path.exists():
                print(f"Warning: VAE model not found at {model_path}")
                return False
            
            self.model = VAE(latent_dim=self.latent_dim)
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.model.to(self.device)
            self.model.eval()
            return True
        return True
    
    def compress(self, *, path: str, mime: str):
        if not self._load_model():
            # Fallback to Zstd compression (like the stub)
            print("Using Zstd fallback for image compression")
            from pyzstd import ZstdCompressor
            raw = read_bytes(path)
            comp = ZstdCompressor(15).compress(raw)
            meta = {"fallback": "zstd", "reason": "vae_model_not_available"}
            return comp, meta
        
        # Use real VAE compression
        raw_bytes = read_bytes(path)
        image = Image.open(BytesIO(raw_bytes)).convert('RGB')
        original_size = image.size
        
        # Resize to 64x64 for VAE
        image = image.resize((64, 64))
        
        # Convert to tensor
        img_tensor = torch.from_numpy(np.array(image)).float() / 255.0
        img_tensor = img_tensor.permute(2, 0, 1).unsqueeze(0)
        img_tensor = img_tensor.to(self.device)
        
        # Encode to latent space
        with torch.no_grad():
            mu, logvar = self.model.encode(img_tensor)
            latent = mu.cpu().numpy()
        
        # Serialize
        compressed_data = pickle.dumps({
            'latent': latent,
            'original_size': original_size,
            'latent_dim': self.latent_dim
        })
        
        meta = {
            'compression_type': 'vae_latent',
            'original_size': original_size,
            'latent_shape': latent.shape
        }
        
        return compressed_data, meta
    
    def decompress(self, *, data: bytes, meta: Dict) -> bytes:
        """Decompress image from VAE or Zstd fallback."""
        if meta.get('fallback') == 'zstd':
            # Use Zstd decompression
            from pyzstd import ZstdDecompressor
            return ZstdDecompressor().decompress(data)
        
        if not self._load_model():
            raise RuntimeError("Cannot decompress VAE-compressed image: model not available")
        
        # VAE decompression
        compressed_data = pickle.loads(data)
        latent = torch.from_numpy(compressed_data['latent']).to(self.device)
        original_size = compressed_data['original_size']
        
        with torch.no_grad():
            reconstructed = self.model.decode(latent)
            img_tensor = reconstructed.squeeze(0).cpu()
            img_array = (img_tensor.permute(1, 2, 0) * 255).clamp(0, 255).numpy().astype(np.uint8)
            
        image = Image.fromarray(img_array)
        image = image.resize(original_size)
        
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        return buffer.getvalue()