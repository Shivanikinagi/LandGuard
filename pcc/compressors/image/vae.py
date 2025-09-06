# compressors/image/vae.py


import torch


import torch.nn as nn


import torch.nn.functional as F


import torchvision.transforms as transforms


from PIL import Image


import numpy as np


import os


from torchvision.utils import save_image as tv_save_image





class VAE(nn.Module):


    """Variational Autoencoder for image compression."""
    


    def __init__(self, latent_dim=128, input_channels=3):


        super(VAE, self).__init__()


        self.latent_dim = latent_dim





        # Encoder


        self.encoder = nn.Sequential(


            # 64x64x3 -> 32x32x32


            nn.Conv2d(input_channels, 32, 4, stride=2, padding=1),


            nn.ReLU(),


            # 32x32x32 -> 16x16x64


            nn.Conv2d(32, 64, 4, stride=2, padding=1),


            nn.ReLU(),


            # 16x16x64 -> 8x8x128


            nn.Conv2d(64, 128, 4, stride=2, padding=1),


            nn.ReLU(),


            # 8x8x128 -> 4x4x256


            nn.Conv2d(128, 256, 4, stride=2, padding=1),


            nn.ReLU(),


        )


        


        # Latent space


        self.fc_mu = nn.Linear(256 * 4 * 4, latent_dim)


        self.fc_logvar = nn.Linear(256 * 4 * 4, latent_dim)


        self.fc_decode = nn.Linear(latent_dim, 256 * 4 * 4)





        # Decoder


        self.decoder = nn.Sequential(


            # 4x4x256 -> 8x8x128


            nn.ConvTranspose2d(256, 128, 4, stride=2, padding=1),


            nn.ReLU(),


            # 8x8x128 -> 16x16x64


            nn.ConvTranspose2d(128, 64, 4, stride=2, padding=1),


            nn.ReLU(),


            # 16x16x64 -> 32x32x32


            nn.ConvTranspose2d(64, 32, 4, stride=2, padding=1),


            nn.ReLU(),


            # 32x32x32 -> 64x64x3


            nn.ConvTranspose2d(32, input_channels, 4, stride=2, padding=1),


            nn.Sigmoid(),  # Output in [0,1]


        )


    
    def encode(self, x):


        """Encode input to latent space."""


        x = self.encoder(x)


        x = x.view(x.size(0), -1)  # Flatten


        mu = self.fc_mu(x)


        logvar = self.fc_logvar(x)


        return mu, logvar
    


    def reparameterize(self, mu, logvar):


        """Reparameterization trick for backpropagation through stochastic nodes."""


        std = torch.exp(0.5 * logvar)


        eps = torch.randn_like(std)


        return mu + eps * std





    def decode(self, z):


        """Decode from latent space to image."""


        x = self.fc_decode(z)


        x = x.view(x.size(0), 256, 4, 4)  # Reshape for conv layers


        x = self.decoder(x)


        return x
    


    def forward(self, x):


        """Full forward pass."""


        mu, logvar = self.encode(x)


        z = self.reparameterize(mu, logvar)


        recon = self.decode(z)


        return recon, mu, logvar





def load_image(path, img_size=64):


    transform = transforms.Compose([


        transforms.Resize((img_size, img_size)),


        transforms.ToTensor()


    ])


    img = Image.open(path).convert("RGB")


    return transform(img).unsqueeze(0)





def save_latent(z, path):


    np.save(path, z.detach().cpu().numpy())





def load_latent(path):


    z = np.load(path)


    return torch.tensor(z)





def decompress_latent(latent_path, output_filename="reconstructed.png"):


    """


    Loads a VAE model, decodes a latent representation from a .npy file,


    and saves the reconstructed image.


    Returns the path to the reconstructed image.


    """


    import torch





    # Load the model


    model = VAE()


    # NOTE: This path is relative and might be fragile in other contexts.


    model_path = "../models/vae.pth"


    if not os.path.exists(model_path):


        raise FileNotFoundError(f"VAE model not found at {model_path}. Please train it first.")


    model.load_state_dict(torch.load(model_path))


    model.eval()





    # Load the latent vector and decode


    latent_z = load_latent(latent_path)


    with torch.no_grad():


        reconstructed_img_tensor = model.decode(latent_z)





    # Save the reconstructed image


    tv_save_image(reconstructed_img_tensor, output_filename)


    print(f"✅ Reconstructed image saved to {output_filename}")


    return output_filename