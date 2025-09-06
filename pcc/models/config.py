from pathlib import Path
import os

# Directory to save models
MODELS_DIR = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models")))

# Path to save the VAE model
VAE_MODEL_PATH = MODELS_DIR / "vae_model.pth"