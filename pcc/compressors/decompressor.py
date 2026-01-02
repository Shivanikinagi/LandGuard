"""
Pied Piper 2.0 - Decompression Module
Handles decompression for all supported algorithms
"""
import os
import tempfile
import traceback


def decompress_file(compressed_data: bytes, algorithm: str):
    """
    Decompress data based on the algorithm used.
    
    Args:
        compressed_data: The compressed bytes
        algorithm: Compression algorithm name ('vae-v1', 'bpe-gpt-lite', 'none', etc.)
    
    Returns:
        bytes: The decompressed original data
    """
    try:
        # No compression case
        if algorithm == "none":
            return compressed_data
        
        # VAE image decompression
        if algorithm == "vae-v1":
            print("🖼️ Decompressing with VAE...")
            try:
                from compressors.image.vae import VAE, load_latent, tensor_to_image
                import torch
                import io
                
                # Load model
                model = VAE()
                model_path = os.path.join(os.path.dirname(__file__), "..", "models", "vae.pth")
                model_path = os.path.normpath(model_path)
                
                model.load_state_dict(torch.load(model_path, map_location="cpu"))
                model.eval()
                
                # Save compressed data to temp file and load latent
                with tempfile.NamedTemporaryFile(delete=False, suffix=".vae.npy") as tmp:
                    tmp.write(compressed_data)
                    tmp_path = tmp.name
                
                try:
                    latent = load_latent(tmp_path)
                    
                    # Decode
                    with torch.no_grad():
                        reconstructed = model.decode(latent)
                    
                    # Convert to bytes
                    img_bytes = tensor_to_image(reconstructed)
                    return img_bytes
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                
            except Exception as e:
                print(f"⚠️ VAE decompression failed: {e}")
                traceback.print_exc()
                raise
        
        # BPE text decompression
        if algorithm == "bpe-gpt-lite":
            print("📄 Decompressing with BPE...")
            try:
                from compressors.text.bpe_compressor import decompress_text
                
                # If data is bytes, decode to string first
                if isinstance(compressed_data, bytes):
                    compressed_str = compressed_data.decode("utf-8")
                else:
                    compressed_str = compressed_data
                
                decompressed_text = decompress_text(compressed_str)
                
                # Return as bytes
                if isinstance(decompressed_text, str):
                    return decompressed_text.encode("utf-8")
                return decompressed_text
                
            except Exception as e:
                print(f"⚠️ BPE decompression failed: {e}")
                traceback.print_exc()
                raise
        
        # Unknown algorithm - return as-is
        print(f"⚠️ Unknown compression algorithm: {algorithm}. Returning data as-is.")
        return compressed_data
        
    except Exception as e:
        print(f"❌ Decompression error: {e}")
        traceback.print_exc()
        raise


# Legacy function for backward compatibility
def decompress_data(data, metadata):
    """Legacy function - use decompress_file instead"""
    algorithm = metadata.get('compression_algorithm', 'none')
    return decompress_file(data, algorithm)