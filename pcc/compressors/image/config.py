from pathlib import Path
import os

MODELS_DIR = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "models")))
VAE_MODEL_PATH = MODELS_DIR / "vae_model.pth"