# compressors/compressor.py
from pathlib import Path
import os
import traceback

def compress_file(file_path: str, file_info: dict, model_hint: str = None):
    """
    Compress the given file and return a 3-tuple:
      (compressed_bytes, model_name, compressed_size)

    This function will try AI-based compressors first (image VAE for images,
    BPE for text), and fall back to returning the original bytes on failure.
    """
    try:
        ext = Path(file_path).suffix.lower()

        # Read the original file contents (ensure we call .read())
        with open(file_path, "rb") as fh:
            original_data = fh.read()
        original_size = len(original_data)

        # IMAGE: try VAE compression if appropriate
        if file_info.get("type") == "image" and (model_hint == "vae" or not model_hint):
            print("🖼️ Using VAE for image compression...")
            try:
                # local import so project doesn't require torch/pillow unless used
                from compressors.image.vae import VAE, load_image, save_latent
                import torch

                model = VAE()
                # adjust model path if needed — relative to project root
                model_path = os.path.join(os.path.dirname(__file__), "..", "models", "vae.pth")
                model_path = os.path.normpath(model_path)

                model.load_state_dict(torch.load(model_path, map_location="cpu"))
                model.eval()

                img = load_image(file_path)  # expects tensor or pillow transform
                with torch.no_grad():
                    mu, _ = model.encode(img)

                latent_path = file_path + ".vae.npy"
                save_latent(mu, latent_path)

                with open(latent_path, "rb") as lf:
                    compressed = lf.read()

                return compressed, "vae-v1", len(compressed)
            except Exception as e:
                print(f"⚠️ VAE failed: {e}")
                traceback.print_exc()
                # fallback to original

        # TEXT: try BPE compression
        if file_info.get("type") == "text":
            print("📄 Using BPE for text compression...")
            try:
                from compressors.text.bpe_compressor import compress_text

                # decode to text (assume utf-8); if decoding fails, fall back
                try:
                    text = original_data.decode("utf-8")
                except UnicodeDecodeError:
                    # not valid UTF-8; return original
                    raise

                compressed = compress_text(text)
                # ensure bytes
                if isinstance(compressed, str):
                    compressed = compressed.encode("utf-8")
                return compressed, "bpe-gpt-lite", len(compressed)
            except Exception as e:
                print(f"⚠️ BPE failed: {e}")
                traceback.print_exc()
                # fallback to original

        # Default fallback: return raw original bytes (no compression)
        print("⚠️ No AI model applied or compression failed. Returning original data.")
        return original_data, "none", original_size

    except Exception as outer_e:
        # Fatal error during compress_file — return original with 'none'
        print(f"❌ Unexpected error inside compress_file: {outer_e}")
        traceback.print_exc()
        # try to safely return original bytes if possible
        try:
            with open(file_path, "rb") as fh:
                orig = fh.read()
            return orig, "none", len(orig)
        except Exception:
            # Last resort: empty bytes
            return b"", "none", 0
