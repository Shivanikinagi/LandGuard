# compressors/image/train_vae.py

import os
import argparse
from pathlib import Path
import platform

import torch
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from torchvision.io import read_image, ImageReadMode
from torchvision import transforms
from tqdm import tqdm

# Base directories
BASE_DIR = Path(__file__).parent
MODELS_DIR = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "models")))
VAE_MODEL_PATH = MODELS_DIR / "vae_model.pth"

# Training defaults
DEFAULT_LATENT_DIM = 128
DEFAULT_EPOCHS = 50
DEFAULT_BATCH_SIZE = 16
DEFAULT_LR = 1e-3

# Use absolute paths from our config for robustness
from pcc.models.config import VAE_MODEL_PATH, MODELS_DIR
from pcc.compressors.image.vae import VAE


class ImageDataset(Dataset):
    """A custom dataset to load images from a directory."""
    def __init__(self, image_dir, transform=None):
        self.image_dir = Path(image_dir)

        exts = (".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG")
        self.image_paths = [p for p in self.image_dir.iterdir() if p.suffix in exts]

        self.transform = transform
        if not self.image_paths:
            raise FileNotFoundError(f"No images found in {image_dir}")
        print(f"Found {len(self.image_paths)} images.")

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        # torchvision's efficient image reader (Tensor, CxHxW, uint8)
        image = read_image(str(img_path), mode=ImageReadMode.RGB)
        if self.transform:
            image = self.transform(image)
        return image


def train_vae(
    image_dir,
    epochs=50,
    batch_size=16,
    latent_dim=128,
    learning_rate=1e-3,
    kl_weight=1.0,
):
    """Trains the VAE model on a directory of images."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🧠 Using device: {device}")

    # Small perf win when image sizes are constant
    if device == "cuda":
        torch.backends.cudnn.benchmark = True

    model = VAE(latent_dim=latent_dim).to(device)
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Define transformations for the images
    transform = transforms.Compose([
        transforms.ToPILImage(),   # accepts Tensor from read_image
        transforms.Resize((64, 64)),
        transforms.ToTensor(),     # -> float in [0, 1]
    ])

    dataset = ImageDataset(image_dir, transform=transform)

    # Safer default for Windows spawn() issues
    default_workers = 0 if platform.system().lower().startswith("win") else min(4, os.cpu_count() or 1)

    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=default_workers,
        pin_memory=(device == "cuda"),
        drop_last=False,
    )

    print(f"🔥 Starting VAE training on {len(dataset)} images for {epochs} epochs...")

    for epoch in range(epochs):
        model.train()
        epoch_recon = 0.0
        epoch_kl = 0.0
        for images in tqdm(dataloader, desc=f"Epoch {epoch + 1}/{epochs}"):
            images = images.to(device)

            optimizer.zero_grad()
            recon, mu, logvar = model(images)

            # VAE loss (Reconstruction + KL divergence)
            recon_loss = F.mse_loss(recon, images, reduction="sum")
            kl_div = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
            loss = recon_loss + kl_weight * kl_div

            loss.backward()
            optimizer.step()

            epoch_recon += recon_loss.item()
            epoch_kl += kl_div.item()

        # Average per image for readability
        avg_recon = epoch_recon / len(dataset)
        avg_kl = epoch_kl / len(dataset)
        avg_total = avg_recon + kl_weight * avg_kl
        print(f"Epoch {epoch+1}: recon={avg_recon:.4f}, KL={avg_kl:.4f}, total={avg_total:.4f}")

    # Save the model using the robust path from config
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), VAE_MODEL_PATH)
    print(f"✅ VAE model saved to {VAE_MODEL_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Train a Variational Autoencoder (VAE) on a dataset of images.")
    parser.add_argument("image_dir", type=str, help="Directory containing training images (.png, .jpg).")
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs.")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size for training.")
    parser.add_argument("--latent-dim", type=int, default=128, help="Dimension of the latent space.")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate for the Adam optimizer.")
    parser.add_argument("--kl-weight", type=float, default=1.0, help="Weight for KL divergence term.")
    args = parser.parse_args()

    train_vae(args.image_dir, args.epochs, args.batch_size, args.latent_dim, args.lr, args.kl_weight)


if __name__ == "__main__":
    main()
